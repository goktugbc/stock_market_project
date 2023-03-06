import json
from kafka import KafkaProducer, KafkaConsumer


class EventStreamer:
    topic = ""
    producer = None
    consumer = None

    def __init__(self, topic):
        self.topic = topic

    def create_producer(self):
        self.producer = KafkaProducer(bootstrap_servers='kafka:9092',
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    def create_consumer(self):
        self.consumer = KafkaConsumer(self.topic,
                                      bootstrap_servers='kafka:9092',
                                      auto_offset_reset='earliest',
                                      consumer_timeout_ms=10 * 1000,
                                      connections_max_idle_ms=(10 * 1000) + 2,
                                      request_timeout_ms=(10 * 1000) + 1,
                                      session_timeout_ms=10 * 1000,
                                      value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                      group_id="goktug")

    def send_message(self, message):
        self.producer.send(self.topic, message)

    def process_messages(self, callback, message_count_to_process=None):
        i = 0
        unsuccessful_messages = []
        for message in self.consumer:
            message = message.value
            result = callback(message)
            if result:
                self.consumer.commit()
            else:
                unsuccessful_messages.append(message)
            if message_count_to_process and message_count_to_process <= i:
                unsuccessful_messages.append(message)
            i += 1

        self.consumer.close()
        self.create_producer()
        for message in unsuccessful_messages:
            self.send_message(message)
