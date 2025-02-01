# batesste-icloud-exporter

A [Prometheus][ref-prom] exporter for exporting a bunch of key
information (including my kids' GPS location) via iCloud
services. Note this is build on the excellent [pyicloud][ref-pyicloud]
Python library.

## Usage

Place a file called ```.user.json``` in the base directory of this
repo. It should contain the following:
```
{
    "username": "<iCloud email>"
    "password": "<iCloud Password>"
}
```
Then run the following command:
```
./batesste-icloud-exporter.py
```
If you point a browser at ```localhost:99478``` you should see the
metrics for the iCloud services  linked to your account. For more
usage options:
```
./batesste-icloud-exporter.py -h
```
## Systemd Service Install

You can install this as a systemd service on your using via the
following steps (tested on Ubuntu 24.04):

1. ```sudo python3 -m venv /usr/local/venvs/batesste-icloud-exporter```.
1. ```sudo /usr/local/venvs/batesste-icloud-exporter/bin/pip install -r requirements.txt```.
1. ```sudo cp batesste-icloud-exporter.py /usr/local/bin```.
1. ```sudo cp batesste-icloud-exporter.service /etc/systemd/system/```.
1. ```sudo mkdir -p /usr/local/share/batesste-icloud-exporter```.
1. ```sudo cp .user.json /usr/local/share/batesste-icloud-exporter/.user.json```.
1. ```sudo systemctl daemon-reload```
1. ```sudo systemctl enable batesste-icloud-exporter.service```
1. ```sudo systemctl start batesste-icloud-exporter.service```

[ref-prom]: https://prometheus.io/
[ref-pyicloud]: https://github.com/picklepete/pyicloud
