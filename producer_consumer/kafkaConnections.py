# Copyright 2021 Scuola Superiore Sant'Anna www.santannapisa.it
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# python imports

import configparser
from json import dumps, loads
from confluent_kafka.admin import AdminClient
from confluent_kafka import Consumer, Producer
from confluent_kafka.cimpl import NewTopic
import logging
import json

log = logging.getLogger("KafkaConnections")


class kafkaConnections:
    def __init__(self, configfile):
        self.kIp = "10.30.2.35"
        self.kPort = 9291
        self.ktopic = "infrastructure"
        self.kID = 30

        config = configparser.ConfigParser()
        if configfile is None:
            config.read('default.config')
        else:
            config.read(configfile)
        if 'kafka' in config:
            self.kIp = config['kafka']['kafkaIP']
            self.kPort = config['kafka']['kafkaPort']
            self.ktopic = config['kafka']['kafkaTopic']
            if 'kafkaID' in config['kafka']:
                self.kID = config['kafka']['kafkaID']


    ### KAFKA methods ###

    #create a new kafka topic
    def createKafkaTopic(self, topic):
        new_topics = []
        broker = f"{self.kIp}:{self.kPort}"
        client = AdminClient({'bootstrap.servers' : broker})
        
        new_topics.append(NewTopic(topic, 1, 1))
        fs = client.create_topics(new_topics)

        # Wait for operation to finish.
        # Timeouts are preferably controlled by passing request_timeout=15.0
        # to the create_topics() call.
        # All futures will finish at the same time.
        log.debug('External Connector: Creating kafka topic ' + str(topic))

        for topic_elem, f in fs.items():
            try:
                f.result()
                log.debug("External Connector: Topic {} created".format(topic_elem))
                return topic
            except Exception as e:
                log.error("External Connector: Failed to create topic {}: {}".format(topic_elem, e))
                return 0

    #delete a kafka topic
    def deleteKafkaTopic(self, topic):
        del_topics = []
        broker = f"{self.kIp}:{self.kPort}"
        client = AdminClient({'bootstrap.servers' : broker})
        del_topics.append(topic)
        fs = client.delete_topics(del_topics)
        # Wait for each operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                log.debug("External Connector: Topic {} deleted".format(topic))
                return topic
            except Exception as e:
                log.error("External Connector: Failed to delete topic {}: {}".format(topic, e))
                return 0

    def createKafkaTopic_free(self, topic):
        print(self.kIp + ":" + str(self.kPort))
        new_topics = []
        broker = f"{self.kIp}:{self.kPort}"
        client = AdminClient({'bootstrap.servers' : broker})
        new_topics.append(NewTopic(topic, 1, 1))
        fs = client.create_topics(new_topics)

        # Wait for operation to finish.
        # Timeouts are preferably controlled by passing request_timeout=15.0
        # to the create_topics() call.
        # All futures will finish at the same time.
        log.debug('External Connector: Creating kafka topic ' + str(topic))

        for topic_elem, f in fs.items():
            try:
                f.result()
                log.debug("External Connector: Topic {} created".format(topic_elem))
                return topic
            except Exception as e:
                log.error("External Connector: Failed to create topic {}: {}".format(topic_elem, e))
                return 0


    def createKafkaConsumer(self, id, topic):

        consumer = Consumer({
            'bootstrap.servers':  str(self.kIp) + ":" + str(self.kPort),
            'group.id': id,
            'auto.offset.reset': 'latest'#,
            #'value.deserializer': lambda m: json.loads(m.decode('utf-8'))
        })
        consumer.subscribe([topic])
        log.debug("External Connector: Kafka consumer enabled for topic {}".format(topic))
        return consumer

    def createKafkaProducer(self):
        # value_serializer = lambda m: json.dumps(m).encode('utf-8'))
        conf = {
            'bootstrap.servers': self.kIp + ":" + str(self.kPort)#,
            #'value.serializer': lambda m: json.dumps(m).encode('utf-8')
        }
        p = Producer(conf)
        return p


    ### Prometheus methods ###

    def startPrometheusJob(self, vnfdId, nsId, period, job_id):
        header = {'Accept': 'application/json',
                  'Content-Type': 'application/json'
                  }
        # create the exporter for the job
        uri = "http://" + self.monIp + ":" + self.monPort + "/prom-manager/exporter"
        name = "forecasting-"+nsId + "-" + vnfdId
        '''
        example
        {
            "name": "forecasting-fgt-7bbb232-1017-45af-8488-a993b874e7a3",
            "endpoint": [
                {"address": "10.5.1.153",
                 "port": "9100"}
            ],
            "nsId": "fgt-7bbb232-1017-45af-8488-a993b874e7a3",
            "collectionPeriod": 15,
            "metrics_path": "/metrics"
        }
        '''
        metric = "/metrics/" +str(nsId) + "/" + vnfdId
        body = {"name": name,
                "endpoint": [ {"address": self.localIp,
                               "port": self.localPort}
                            ],
                "vnfdId": vnfdId,
                "nsId": nsId,
                "collectionPeriod": period,
                "metrics_path": metric,
                "forecasted": "yes",
                "honor_labels": "true",
                "exporter": "forecasting_exporter"
               }
        log.debug("External Connector: Prometheus job request \n{}".format(body))
        try:
            conn = HTTPConnection(self.monIp, int(self.monPort))
            conn.request("POST", uri, body=dumps(body), headers=header)
            re = conn.getresponse()
            data = re.read()
            r8 = data.decode("utf-8")
            reply = loads(r8)
            log.debug("EC: Prometheus job reply: {}".format(str(reply)))
            conn.close()
            pid = reply.get('exporterId')
            return pid
        except ConnectionRefusedError:
            log.error("EC: Error, connection refused")
        return reply

    #stop and delete  running prometheus job
    def stopPrometheusJob(self, jobId):
        header = {'Content-Type': 'application/json',
                  'Accept': 'application/json'}
        # create the exporter for the job
        path = "http://" + self.monIp + ":" + self.monPort + "/prom-manager/exporter"
        log.debug("External Connector: Deleting prometheus job {}".format(str(jobId)))
        try:
            conn = HTTPConnection(self.monIp, self.monPort)
            conn.request("DELETE", path + "/" + jobId, None, header)
            rsp = conn.getresponse()
            log.debug("External Connector: Deleted prometheus job reply: {}".format(rsp))
        except ConnectionRefusedError:
            log.error("External Connector: Error, connection refused)")

    ### SCRAPER methods ###

    #create scraper job
    def startScraperJob(self, nsid, topic, vnfdid, metric, expression, period):
            header = {'Accept': 'application/json',
                      'Content-Type': 'application/json'
                      }
            body = {
                "nsid": nsid,
                "vnfid": vnfdid,
                "interval": period,
                "performanceMetric": metric,
                "kafkaTopic": topic,
                "expression": expression
            }
            log.debug("External Connector: Scraper job request \n{}".format(body))
            path = "http://" + self.monIp + ":" + str(self.monPort) + "/prom-manager/prometheus_scraper"
            try:
                conn = HTTPConnection(self.monIp, self.monPort)
                conn.request("POST", path, body=dumps(body), headers=header)
                re = conn.getresponse()
                data = re.read()
                r8 = data.decode("utf-8")
                reply = loads(r8)
                conn.close()
                log.debug("External Connector: Scraper job reply \n{}".format(reply))
                sid = reply.get('scraperId')
                return sid
            except ConnectionRefusedError:
                log.error("External Connector: Error, connection refused")
                # the Config Manager is not running or the connection configuration is wrong
            return 

    #delete scraper job
    def stopScraperJob(self, job_id):
            header = {'Accept': 'application/json'
                      }
            path = "http://" + self.monIp + ":" + self.monPort + "/prom-manager/prometheus_scraper/"+ str(job_id)
            log.debug("External Connector: Deleting scraper job {}".format(str(job_id)))
            try:
                conn = HTTPConnection(self.monIp, self.monPort)
                conn.request("DELETE", path, headers=header)
                rsp = conn.getresponse()
                resources = rsp.read()
                resp = resources.decode("utf-8")
                log.debug("External Connector: Deleted scaper job reply: {}".format(resp))
                conn.close()
                return 1
            except ConnectionRefusedError:
                log.error("External Connector: Error, connection refused")
                return 0
