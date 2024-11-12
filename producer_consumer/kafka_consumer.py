from kafkaConnections import kafkaConnections
from confluent_kafka import KafkaError, KafkaException
import json
from confluent_kafka.error import ConsumeError

import argparse

# Define the parser
parser = argparse.ArgumentParser()

parser.add_argument('--file', action="store", dest='file', default=0)
args = parser.parse_args()
fx = args.file


print(fx)
#ec = kafkaConnections("configP1.conf")
ec = kafkaConnections(fx)

p = ec.createKafkaProducer()

topic = ec.ktopic
idx = ec.kID

def main():
        consumer = ec.createKafkaConsumer(idx, topic)
        while True:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        log.error('%% %s [%d] end at offset %d\n' % (msg.topic(),msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    #sys.stderr.write(json.load(msg.value()))
                    loaded_json = json.loads(msg.value())
                    print(json.dumps(loaded_json, indent=4, sort_keys=True))
            except ConsumeError as e:
                log.error("Consumer error: {}".format(str(e)))
                # Should be commits manually handled?
                consumer.close()
            except KeyboardInterrupt:
                consumer.close()
                break



main()
