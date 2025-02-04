#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause

import re
import time

import prometheus_client as pc
from pyicloud import PyiCloudService

def two_fa(icloud):
    """
    A simple function to perform the Two Factor Authentication (2FA)
    steps in an iCloud login.
    """
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = icloud.validate_2fa_code(code)
    print("Code validation result: %s" % result)
    if not result:
        print("Failed to verify security code")

def two_sa(icloud):
    """
    A simple function to perform the Two Step Authentication (2SA)
    steps in an iCloud login.
    """
    import click
    print("Two-step authentication required. Your trusted devices are:")
    devices = icloud.trusted_devices
    for i, device in enumerate(devices):
        print("  %s: %s" % (i, device.get('deviceName',
                                          "SMS to %s" % device.get('phoneNumber'))))

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not icloud.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)
    code = click.prompt('Please enter validation code')
    if not icloud.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

def trust(icloud):
    """
    A simple function to try and setup a trusted session.
    """
    print("Session is not trusted. Requesting trust...")
    result = icloud.trust_session()
    print("Session trust result %s" % result)
    if not result:
        print("Failed to request trust. You will be prompted for the code again in the coming weeks")

class iCloudExporter:

    def __init__(self, args):
        self.icloud = None
        self.port = args.port
        self.interval = args.interval
        self.auth_file = args.auth_file
        self.twofa_file = args.twofa_file
        self.systemd = args.systemd
        self.needs_2fa = False
        self.verbose = args.verbose
        self.labels = [ 'device' ]
        self.ic_2fa  = pc.Gauge("icloud_auth_2fa_update_needed",
                                "Indicator that an updated 2FA code is needed")
        self.ic_time = pc.Gauge("icloud_location_timestamp",
                                "Timestamp of location measurement of icloud device",
                                [ 'device' ])
        self.ic_lat = pc.Gauge("icloud_location_latitude",
                               "Latitude measurement of icloud device",
                               [ 'device' ])
        self.ic_long = pc.Gauge("icloud_location_longtitude",
                                "Longtitude measurement of icloud device",
                                [ 'device' ])

    def connect(self):
        """
        This function connects us to the Apple iCloud servers. Also
        when we are in systemd mode it informs the user (via the
        exporter itself) that a new 2FA code is needed. Also when in
        systemd mode we do not bother to try and connect unless the
        2FA file exists and contains a 6 digit code.
        """

        with open(self.auth_file) as f:
            data = json.load(f)

        if self.systemd:
            if self.needs_2fa:
                f = open(self.twofa_file, "r")
                code = f.read().rstrip()
                f.close
                if code.isnumeric():
                    self.icloud.validate_2fa_code(code)
                if self.icloud.requires_2fa or self.icloud.requires_2sa:
                    f = open(self.twofa_file, "w")
                    f.truncate(0)
                    f.close
                    return 1
                self.needs_2fa = False
                f = open(self.twofa_file, "w")
                f.truncate(0)
                f.close
                return self.interval
            else:
                self.icloud = PyiCloudService(data['username'],
                                              data['password'])
                if self.icloud.requires_2fa or self.icloud.requires_2sa:
                    self.needs_2fa = True
                    return 1
        else:
            self.icloud = PyiCloudService(data['username'],
                                          data['password'])
            if self.icloud.requires_2fa:
                two_fa(self.icloud)
                if not self.icloud.is_trusted_session:
                    trust(self.icloud)
            elif self.icloud.requires_2sa:
                two_sa(self.icloud)

        self.needs_2fa = False

        return self.interval

    def export_location(self, device, location):
        """
        A function to export the metrics we care about with respect to
        devices that can be located.
        """
        labelname = re.sub('[^a-zA-Z0-9_]','_',str(device).lower())
        self.ic_time.labels(device=labelname).set(location['timeStamp'])
        self.ic_lat.labels(device=labelname).set(location['latitude'])
        self.ic_long.labels(device=labelname).set(location['longitude'])

    def run(self):
        """
        This is the main loop of the exporter that obtains information
        from the Apple servers and exports key metrics.
        """
        pc.start_http_server(port=self.port)
        while True:
            if self.verbose:
                if self.needs_2fa:
                    print("Attempting 2FA connection to iCloud.")
                else:
                    print("Connecting to iCloud and collecting stats.")
            interval = self.connect()
            if self.needs_2fa:
                self.ic_2fa.set(1)
            else:
                self.ic_2fa.set(0)
                for device in self.icloud.devices:
                    if self.verbose:
                        print("  Found a device: %s" % str(device))
                    try:
                        location = device.location()
                    except:
                        location = None
                        pass
                    if location:
                        self.export_location(device,
                                             location)
            time.sleep(interval)

if __name__ == '__main__':

    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description='A Prometheus metrics exporter for Apple iCloud related things.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Be verbose')
    parser.add_argument('--systemd', '-s', action='store_true',
                        help='Run in systemd mode, helps with 2FA.')
    parser.add_argument('--port', '-p', metavar='PORT',
                        type=int, default=9948,
                        help='The TCP/IP port to put metrics on.')
    parser.add_argument('--interval', '-n', metavar='SCRAPE_INTERVAL',
                        type=int, default=60,
                        help='The interval at which to update metrics.')
    parser.add_argument('--auth_file', metavar='AUTH_FILE', default='.user.json',
                        help='The authorization (username and password) file icloud.')
    parser.add_argument('--twofa_file', metavar='TWO_FA_FILE', default=None,
                        help='The file the program scans to detect a new 2FA code (systemd)')
    args = parser.parse_args()

    exporter = iCloudExporter(args)
    try:
        exporter.run()
    except KeyboardInterrupt:
        pass
