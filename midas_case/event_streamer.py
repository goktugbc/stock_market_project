import json
from kafka import KafkaProducer, KafkaConsumer


class EventStreamer:
    topic = ""
    producer = None
    consumer = None

    def __init__(self, topic):
        self.topic = topic

    def create_producer(self):
        self.producer = KafkaProducer(bootstrap_servers='kafka:9092')

    def create_consumer(self):
        self.consumer = KafkaConsumer(self.topic,
                                      bootstrap_servers='kafka:9092',
                                      auto_offset_reset='earliest',
                                      value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    def send_message(self, message):
        self.producer.send(self.topic, message)

    def process_messages(self, callback):
        for message in self.consumer:
            message = message.value
            result = callback(message)
            if result:
                self.consumer.commit()
            else:
                self.consumer.close()
