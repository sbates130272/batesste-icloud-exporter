#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause

import prometheus_client as pc
import pyicloud as pic

def init(args):

    icloud = pic.PyiCloudService(args.user, args.password)

    if icloud.requires_2fa:
        print("Two-factor authentication required.")
        code = input("Enter the code you received of one of your approved devices: ")
        result = icloud.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            sys.exit(1)

        if not icloud.is_trusted_session:
            print("Session is not trusted. Requesting trust...")





            r0
            esult = icloud.trust_session()
                print("Session trust result %s" % result)

                if not result:
                    print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    elif icloud.requires_2sa:

        import click
        print("Two-step authentication required. Your trusted devices are:")

        devices = icloud.trusted_devices
        for i, device in enumerate(devices):
            print(
                "  %s: %s" % (i, device.get('deviceName',
                                            "SMS to %s" % device.get('phoneNumber')))
            )

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not icloud.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not icloud.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)

    return icloud

if __name__ == '__main__':

    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description='A Prometheus metrics exporter for Apple iCloud related things.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', '-p', metavar='PORT',
                        type=int, default=9948,
                        help='The TCP/IP port to put metrics on.')
    parser.add_argument('--interval', '-n', metavar='SCRAPE_INTERVAL',
                        type=int, default=60,
                        help='The interval at which to update metrics.')
    parser.add_argument('--auth_file', metavar='AUTH_FILE', default='.user.json',
                        help='The authorization (username and password) file icloud.')
    args = parser.parse_args()

    icloud = init(args)

    try:
        with open(args.token_file) as f:
            data = json.load(f)

        vue.login(id_token=data['id_token'],
                  access_token=data['access_token'],
                  refresh_token=data['refresh_token'],
                  token_storage_file=args.token_file)
    except:
        with open(args.auth_file) as f:
            data = json.load(f)
        vue.login(username=data['username'],
                  password=data['password'],
                  token_storage_file=args.token_file)

    print("emvue-exporter: connected to Emporia web-server.")
    exporter = emVueMetricsExporter(port=args.port,
                                    interval=args.interval)
    try:
        exporter.run()
    except KeyboardInterrupt:
        pass
