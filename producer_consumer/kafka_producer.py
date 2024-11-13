from kafkaConnections import kafkaConnections
import sys
import time
import argparse

# Define the parser
parser = argparse.ArgumentParser()

parser.add_argument('--file', action="store", dest='file', default=0)
args = parser.parse_args()
fx = args.file

#ec = kafkaConnections("configP1.conf")
ec = kafkaConnections(fx)

p = ec.createKafkaProducer()

msg = """
    {
     "time": %s,
     "site_id" : "D6Gsite1",
     "CPUs" : "100",
     "RAM" : "200",
     "storage" : "300",
     "active PODs" : "10"
}   
"""  

def delivery_callback(err, msg):
    if err:
        sys.stderr.write('%% Message failed delivery: %s\n' % err)
    else:
        sys.stderr.write('%% Message delivered to %s [%d] @ %d\n' %
                         (msg.topic(), msg.partition(), msg.offset()))


topic = ec.ktopic
ec.createKafkaTopic(topic)

i = 0
while True:
    try:
       mess = msg % str(i)    
       p.produce(topic, value=mess, callback=delivery_callback)
       p.flush()
       p.poll(1)
       print(mess)
       i = i + 1
       time.sleep(2)
    except KeyboardInterrupt:
       print("end of the task")
       break


