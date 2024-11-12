# Kafka-docker-mm2
This is a deployment example of how to setup Kafka Docker multi cluster environment with MirrorMaker2.

Two versions are available:
- docker-compose.yml (classic Kafka+Zookeeper deployment)
- docker-compose_raft_ui.yml (new standalone Kafka with RAFT, plus Kafka-UI)

Run:

```docker compose -f [file_name] up -d```

Stop:

```docker compose -f [file_name] down (-v)```

The deployment uses MirrorMaker2 to syncronize information from one cluster to another one. The MM2 istance is a same Kafka broker image but with a different entrypoint. The relative configuration file is _mm2.properties_.
This example is based on the following guide, [Medium article](https://medium.com/larus-team/how-to-setup-mirrormaker-2-0-on-apache-kafka-multi-cluster-environment-87712d7997a4) but with a different base image of Kafka (bitami vs confluent).
