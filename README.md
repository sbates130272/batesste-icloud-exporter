# emvue-exporter

A [Prometheus][ref-prom] exporter for exporting my kids' GPS location
via iCloud services.


## Overview


## Usage

Place a file called ```.user.json``` in the base directory of this
repo. It should contain the following:
```
{
    "username": "<Emporia Username>"
    "password": "<Emporia Password>"
}
```
See the pypi entry for the [PyEmVue module][ref-pyemvue] for more
information. Then run the following command:
```
./emvue-exporter.py
```
If you point a browser at ```localhost:9947``` you should see the
metrics for the Emporia devices linked to your account. For more usage
options:
```
./emvue-exporter.py -h
```
## Systemd Service Install

You can install this as a systemd service on your using via the
following steps (tested on Ubuntu 24.04):

1. ```sudo python3 -m venv /usr/local/venvs/batesste-itrack```.
1. ```sudo /usr/local/venvs/batesste-itrack/bin/pip install -r requirements.txt```.
1. ```sudo cp batesste-itrack.py /usr/local/bin```.
1. ```sudo cp batesste-itrack.service /etc/systemd/system/```.
1. ```sudo mkdir -p /usr/local/share/batesste-itrack```.
1. ```sudo cp .user.json /usr/local/share/batesste-itrack/.user.json```.
1. ```sudo touch /usr/local/share/batesste-itrack/.keys.json```.
1. ```sudo systemctl daemon-reload```
1. ```sudo systemctl enable batesste-itrack.service```
1. ```sudo systemctl start batesste-itrack.service```

[ref-prom]: https://prometheus.io/
[ref-emporia]: https://web.emporiaenergy.com/
[ref-prom-port]:https://github.com/prometheus/prometheus/wiki/Default-port-allocations
[ref-pyemvue]: https://pypi.org/project/pyemvue/
