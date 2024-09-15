from confluent_kafka import Consumer, Producer, KafkaException
from EquatorialScraper import EquatorialScraper
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')

class KafkaClient:
    def __init__(self, consumer_config, producer_config, input_topic, output_topic):
        self.consumer = Consumer(consumer_config)
        self.producer = Producer(producer_config)
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.scraper = EquatorialScraper()

    def consume_messages(self):
        self.consumer.subscribe([self.input_topic])
        while True:
            try:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    raise KafkaException(msg.error())

                self.handle_message(msg)

            except KafkaException as e:
                self.log_error(f"Error consuming message: {e}")

    def handle_message(self, msg):
        try:
            data = json.loads(msg.value().decode('utf-8'))
            self.log_info(f"Received message: {data}")

            self.scraper.process(data.get('unidade_consumidora'), data.get('doc'))

            result = self.create_result(data)
            self.produce_result(result)

        except Exception as e:
            self.log_error(f"Error processing message: {e}")

    def create_result(self, data: dict) -> dict:
        result = self.scraper.__dict__()
        result['id'] = data.get('id')
        return result

    def produce_result(self, result: dict):
        try:
            self.producer.produce(self.output_topic, json.dumps(result))
            self.producer.flush()
            self.log_info(f"Produced result: {result}")

        except KafkaException as e:
            self.log_error(f"Error producing result: {e}")

    @staticmethod
    def log_info(message: str):
        logging.info(message)

    @staticmethod
    def log_error(message: str):
        logging.error(message)
