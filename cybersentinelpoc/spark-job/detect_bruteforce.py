import requests
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql.functions import col, window, regexp_extract, current_timestamp, lit, when, udf

# Spark session
spark = SparkSession.builder \
    .appName("CyberSentinel-SSH-Bruteforce") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# GeoIP UDF
geo_schema = StructType([
    StructField("ip", StringType(), True),
    StructField("country", StringType(), True),
    StructField("country_iso", StringType(), True),
    StructField("city", StringType(), True),
    StructField("lat", DoubleType(), True),
    StructField("lon", DoubleType(), True),
])

def geo_lookup(ip):
    try:
        r = requests.get(f"http://geoip:8000/geo/{ip}", timeout=2)
        return r.json()
    except Exception:
        return {"ip": ip, "country": None, "country_iso": None, "city": None, "lat": None, "lon": None}

geo_udf = udf(lambda ip: geo_lookup(ip), geo_schema)


# Read Kafka stream

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "raw-ssh-logs") \
    .option("startingOffsets", "latest") \
    .load()

logs = df.selectExpr("CAST(value AS STRING) as message") \
    .withColumn("ip", regexp_extract(col("message"), r"from ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", 1)) \
    .withColumn("is_failed", col("message").contains("Failed password")) \
    .withColumn("ts", current_timestamp())

failed = logs.filter(col("is_failed") == True) \
    .filter(col("ip") != "") \
    .withWatermark("ts", "2 minutes")

# Sliding window aggregation
agg = failed.groupBy(
    window(col("ts"), "60 seconds", "10 seconds"),
    col("ip")
).count()


# Build alerts + severity

alerts = agg.filter(col("count") > 10) \
    .withColumn(
        "severity",
        when(col("count") >= 25, lit("HIGH"))
        .when(col("count") >= 15, lit("MEDIUM"))
        .otherwise(lit("LOW"))
    ) \
    .select(
        col("ip").alias("source_ip"),
        col("count").alias("failed_count"),
        col("severity"),
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        lit("SSH_BRUTE_FORCE").alias("alert_type")
    )


# Enrich with GeoIP

alerts = (
    alerts
    .withColumn("geo", geo_udf(col("source_ip")))
    .withColumn("country", col("geo.country"))
    .withColumn("country_iso", col("geo.country_iso"))
    .withColumn("city", col("geo.city"))
    .withColumn("lat", col("geo.lat"))
    .withColumn("lon", col("geo.lon"))
    .drop("geo")
)


# Write to Elasticsearch

def write_to_es(batch_df, batch_id):
    if batch_df.rdd.isEmpty():
        return

    (batch_df.write
        .format("org.elasticsearch.spark.sql")
        .option("es.nodes", "elasticsearch")
        .option("es.port", "9200")
        .option("es.resource", "cybersentinel-alerts")
        .mode("append")
        .save()
    )

query = alerts.writeStream \
    .outputMode("update") \
    .foreachBatch(write_to_es) \
    .option("checkpointLocation", "/tmp/checkpoints/sshbf") \
    .start()

spark.streams.awaitAnyTermination()
