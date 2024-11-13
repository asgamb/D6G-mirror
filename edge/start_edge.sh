#!/bin/sh
filename=".env"
ip=$(ip route get 1 | sed -n 's/^.*src \([0-9.]*\) .*$/\1/p')

echo $ip


line="LOCAL_IP=${ip}"
echo "${line}"

printf $line > $filename
sudo docker compose -f d6gsite1.yml up -d
