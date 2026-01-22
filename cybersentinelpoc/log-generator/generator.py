import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='kafka:29092',
    value_serializer=lambda v: v.encode('utf-8')
)

topic = "raw-ssh-logs"
ip_attack = "192.168.1.100"

while True:
    if random.random() < 0.3:
        log = f"Failed password for root from {ip_attack} port 22 ssh2"
    else:
        log = "Accepted password for user admin from 192.168.1.10 port 22 ssh2"

    producer.send(topic, log)
    print(log)
    time.sleep(1)
