import json
import kafka

from mindsdb.streams.base.base_stream import BaseStream


class KafkaStream(BaseStream):
    def __init__(self, topic, connection_info):
        self.topic = topic
        self.consumer = kafka.KafkaConsumer(**connection_info)
        self.producer = kafka.KafkaProducer(**connection_info, acks='all')
        self.consumer.subscribe(topics=[topic])
        self.position = 0

    def read(self):
        for msg in self.consumer:
            yield json.loads(msg.value)

    def write(self, dct):
        self.producer.send(self.topic, json.dumps(dct).encode('utf-8'))

    def __len__(self):
        current_position = self.consumer.position()
        self.consumer.seek_to_end()
        length = self.consumer.position() - current_position
        self.consumer.seek(current_position)
        return length

    def __del__(self):
        self.consumer.close()
        self.producer.close()
