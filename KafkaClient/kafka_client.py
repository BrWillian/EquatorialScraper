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
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            try:
                data = json.loads(msg.value().decode('utf-8'))
                logging.info(f"Received message: {data}")
                unidade_consumidora = data.get('unidade_consumidora')
                doc = data.get('doc')
                id = data.get('id')

                self.produce_result(self.scraper.process(id, unidade_consumidora, doc))

            except KafkaException as e:
                logging.error(f"Error consuming message: {e}")

    def produce_result(self, result):
        try:
            self.producer.produce(self.output_topic, result)
            self.producer.flush()
            logging.info(f"Produced result: {result}")
        except KafkaException as e:
            logging.error(f"Error producing result: {e}")