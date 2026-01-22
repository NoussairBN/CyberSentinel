FROM python:3.11-slim

WORKDIR /app
RUN pip install kafka-python

COPY generator.py .

CMD ["python", "generator.py"]
