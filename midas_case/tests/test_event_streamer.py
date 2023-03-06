from django.test import TestCase
from kafka import KafkaProducer, KafkaConsumer
from midas_case.event_streamer import EventStreamer



class EventStreamerTests(TestCase):
    def test_create_event_streamer(self):
        topic = "test"
        event_streamer = EventStreamer(topic)

        self.assertEqual(event_streamer.topic, topic)

    def test_create_producer(self):
        topic = "test"
        event_streamer = EventStreamer(topic)
        event_streamer.create_producer()

        self.assertTrue(isinstance(event_streamer.producer, KafkaProducer))

    def test_create_consumer(self):
        topic = "test"
        event_streamer = EventStreamer(topic)
        event_streamer.create_consumer()

        self.assertTrue(isinstance(event_streamer.consumer, KafkaConsumer))
