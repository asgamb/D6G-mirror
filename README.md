# Kafka-docker-mm2
This is an example of synchronization/exporting of distriuted Kafka environemnt exploiting MirrorMaker2.

The deployment uses MirrorMaker2 to syncronize information from one cluster to another one. The MM2 istance is a same Kafka broker image but with a different entrypoint. The relative configuration file is _mm2.properties_.
This example is based on the following guide, [Medium article](https://medium.com/larus-team/how-to-setup-mirrormaker-2-0-on-apache-kafka-multi-cluster-environment-87712d7997a4) but with a different base image of Kafka (bitami vs confluent).

This version is based on the new standalone Kafka with RAFT, plus Kafka-UI.

# Code structure
3 folders are provided:
- cloud: files for the control of the cloud CD kafka instance
- edge: files for the control of an edge D6G kafka instance
- producer_consumer: example of consumer and producers based on python

# cloud_DC commands
Run:
```./start_cloud.sh```
Stop:
```./stop_cloud.sh```

# Edge site commands
Run:
```./start_edge.sh```
Stop:
```stop_edge.sh```


