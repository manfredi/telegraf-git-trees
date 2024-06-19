# telegraf-git-trees
Git Trees for Telegraf Exec Input Plugin

Count files of specific type, based on file extension, under a given path inside a GitHub repo.

The script is used as command for [Telegraf Exec Input Plugin](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec), e.g. `telegraf.conf`

```conf
[[inputs.exec]]
  commands = ["/etc/telegraf/scripts/git_trees.py -o os-autoinst -r os-autoinst-distri-opensuse -p schedule/yam/ -t yaml -m qe_yam_schedule_yaml"]
  timeout = "60s"
  interval = "4h"
  data_format = "influx"
```

For _standalone_ test, e.g.

```python
#!/usr/bin/env python3
from git_trees import git_trees
git_trees('os-autoinst', 'os-autoinst-distri-opensuse', 'schedule/yam/', 'yaml', 'qe_yam_schedule_yaml')
```

## An Example How To Setup in Container by `podman`

Run following script inside the repo directory where there are the Python and Bash scripts `git_trees.py` and `git_trees.sh`:

```bash
#!/usr/bin/env bash
set -e
echo "Setup TIG Stack in Containers"

temp=$(mktemp -d)
echo "Temp directory: $temp"
cp git_trees.py $temp/git_trees.py
cp git_trees.sh $temp/git_trees.sh
cd $temp

pod='tig_stack'
username='admin'
password='passwords_must_be_at_least_8_characters_long'
organization='qe-yam'
bucket='yaml-schedule'
token="$(openssl rand -base64 40)"

json=$(cat<<EOF
{"username":"$username","password":"$password","token":"$token","bucket":"$bucket","org":"$organization"}
EOF
)

Dockerfile="Dockerfile"
TelegrafConf="telegraf.conf"

cat > $Dockerfile <<EOF
FROM telegraf:1.28.5
RUN apt-get update && apt-get install -y --no-install-recommends git jq python3 python3-requests python3-venv python3-pip && rm -rf /var/lib/apt/lists/*
COPY ./git_trees.sh /etc/telegraf/scripts/qe_yam_count_yaml_schedule_files.sh
RUN chmod +x /etc/telegraf/scripts/qe_yam_count_yaml_schedule_files.sh
COPY ./git_trees.py /etc/telegraf/scripts/qe_yam_count_yaml_schedule_files.py
RUN chmod +x /etc/telegraf/scripts/qe_yam_count_yaml_schedule_files.py
EOF

cat > $TelegrafConf <<EOF
[agent]
  interval = "5s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "5s"
  flush_jitter = "0s"
  precision = ""
  hostname = ""
  omit_hostname = false
[[outputs.file]]
  files = ["stdout"]
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "$token"
  organization = "$organization"
  bucket = "$bucket"
[[inputs.exec]]
  commands = ["/etc/telegraf/scripts/qe_yam_count_yaml_schedule_files.py -o os-autoinst -r os-autoinst-distri-opensuse -p schedule/yam/ -t yaml -m yaml_schedule"]
  timeout = "60s"
  interval = "5m"
  data_format = "influx"
[[inputs.exec]]
  commands = ["/etc/telegraf/scripts/qe_yam_count_yaml_schedule_files.py -o os-autoinst -r os-autoinst-distri-opensuse -p schedule/yast/ -t yaml -m yaml_schedule"]
  timeout = "60s"
  interval = "5m"
  data_format = "influx"
[[inputs.exec]]
  commands = ["/etc/telegraf/scripts/qe_yam_count_yaml_schedule_files.sh -o os-autoinst -r os-autoinst-distri-opensuse -p schedule/qam/ -t yaml -m yaml_schedule"]
  timeout = "10m"
  interval = "15m"
  data_format = "influx"
EOF

podman pull docker.io/grafana/grafana:10.3.5
podman pull docker.io/library/telegraf:1.28.5
podman pull docker.io/library/influxdb:2.7.5

podman pod create -p 8086:8086 -p 3000:3000 $pod
podman run --pod $pod -d --rm --name grafana  grafana:10.3.5
podman run --pod $pod -d --rm --name influxdb  influxdb:2.7.5
echo "sleep 5 sec..." && sleep 5
curl -X POST --data "$json" "http://localhost:8086/api/v2/setup" 2>/dev/null | jq .
echo "sleep 5 sec..." && sleep 5
podman build -t telegraf-jq-py:1.28.5 -f $Dockerfile .
podman run --pod $pod --rm --privileged -v "$PWD/$TelegrafConf:/etc/telegraf/telegraf.conf" --name telegraf  localhost/telegraf-jq-py:1.28.5

# port 8086: InfluxDB (admin/passwords_must_be_at_least_8_characters_long)
# port 3000: Grafana  (admin/admin)
# firefox http://localhost:8086
# firefox http://localhost:3000

# podman stop telegraf influxdb grafana
# podman pod rm tig_stack
# rm -rf $temp
```
