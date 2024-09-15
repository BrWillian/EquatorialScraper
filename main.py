import os
from KafkaClient import KafkaClient


def main():
    consumer_config = {
        'bootstrap.servers': os.getenv('KAFKA_CONSUMER_BOOTSTRAP_SERVERS', 'kafka:9092'),
        'group.id': os.getenv('KAFKA_CONSUMER_GROUP_ID', 'equatorial-scraper'),
        'auto.offset.reset': os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest')
    }

    producer_config = {
        'bootstrap.servers': os.getenv('KAFKA_PRODUCER_BOOTSTRAP_SERVERS', 'kafka:9092')
    }

    input_topic = os.getenv('KAFKA_CONSUMER_TOPIC', 'input_topic')
    output_topic = os.getenv('KAFKA_PRODUCER_TOPIC', 'output_topic')

    kafka_client = KafkaClient(consumer_config, producer_config, input_topic, output_topic)

    kafka_client.consume_messages()


if __name__ == "__main__":
    main()
