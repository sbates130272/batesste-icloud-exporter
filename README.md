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
If you point a browser at ```localhost:9978``` you should see the
metrics for the iCloud services  linked to your account. For more
usage options:
```
./batesste-icloud-exporter.py -h
```

## Authentication

Note that most icloud accounts are protected with 2FA or 2SA which
will require setting up a code the first time this up. In normal
operation we can enter the 2FA/2SA code at the command line. See the
systemd section for information when running in that mode.

## Systemd Service Install

You can install this as a systemd service on your using via the
following steps (tested on Ubuntu 24.04):

1. ```sudo python3 -m venv /usr/local/venvs/batesste-icloud-exporter```.
1. ```sudo /usr/local/venvs/batesste-icloud-exporter/bin/pip install -r requirements.txt```.
1. ```sudo cp batesste-icloud-exporter.py /usr/local/bin```.
1. ```sudo cp batesste-icloud-exporter.service /etc/systemd/system/```.
1. ```sudo mkdir -p /usr/local/share/batesste-icloud-exporter```.
1. ```sudo cp .user.json /usr/local/share/batesste-icloud-exporter/.user.json```.
1. ```sudo touch /usr/local/share/batesste-icloud-exporter/.twofa.txt```.
1. ```sudo systemctl daemon-reload```.
1. ```sudo systemctl enable batesste-icloud-exporter.service```.
1. ```sudo systemctl start batesste-icloud-exporter.service```.

When running in systemd mode or when the session token expires we need
to do the following:

1. ```sudo systemctl restart batesste-icloud-tracker```
1. Get the 2FA code which will appear on your approved Apple devices.
1. ```sudo sh -c "echo '<2FA Code' > /usr/local/share/batesste-icloud-exporter/.twofa.txt"```

[ref-prom]: https://prometheus.io/
[ref-pyicloud]: https://github.com/picklepete/pyicloud
