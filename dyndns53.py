#!/usr/bin/python3

import boto.route53
from boto.route53.record import Record
import subprocess
import sys
import time

time.sleep(10)
myip = subprocess.check_output(['/usr/bin/curl', '-s', 'http://instance-data/latest/meta-data/public-ipv4']).decode('utf-8')
conn = boto.route53.connect_to_region('us-west-2')
zone = conn.get_zone(sys.argv[1] + '.')

old_records = zone.find_records(name=sys.argv[1], type='A')

if old_records is not None:
    try:
        for orec in old_records:
            zone.delete_record(orec)
    except TypeError:
        zone.delete_record(old_records)

print('Binding ' + sys.argv[1] + ' to ' + myip)
change_set = boto.route53.record.ResourceRecordSets(connection=conn, hosted_zone_id=zone.id)
changes1 = change_set.add_change("UPSERT", sys.argv[1], type="A", ttl=3)
changes1.add_value(myip)
change_set.commit()
subprocess.check_output(['sudo', 'sysctl', '-p', '/etc/sysctl.conf'])
subprocess.check_output(['sudo', 'iptables', '-F'])
subprocess.check_output(['sudo', 'iptables', '-P', 'INPUT', 'ACCEPT'])
subprocess.check_output(['sudo', 'iptables', '-P', 'FORWARD', 'ACCEPT'])
subprocess.check_output(['sudo', 'iptables', '-P', 'OUTPUT', 'ACCEPT'])
subprocess.check_output(['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-j', 'MASQUERADE'])

