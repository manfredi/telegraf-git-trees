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