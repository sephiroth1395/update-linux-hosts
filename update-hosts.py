#!/usr/bin/env python3

####
#### Python script to check the latest update of the dynamic DNS record to
#### reach home
#### In case the local hosts value does not match the current IP, the record
#### is updated and Wireguard is restarted
####

import dns.resolver
from python_hosts import Hosts, HostsEntry

#### Configuration
###############################################################################

target_host = 'ev1z-home.dynv6.net'

#### Step 1 - Check the current IP addresses
###############################################################################

resolver = dns.resolver.Resolver(configure = False)
resolver.nameservers = ['8.8.8.8']

try:
  r = dns.resolver.resolve(target_host, 'A')
  A_records = []
  for IPval in r:
    A_records.append(IPval.to_text())
  ip4_address = A_records[0]
#  print(ip4_address)
except:
  print('ERROR - Cannot resolve IPv4 record.')
  exit(1)

try:
  r = dns.resolver.resolve(target_host, 'AAAA')
  AAAA_records = []
  for IPval in r:
    AAAA_records.append(IPval.to_text())
  ip6_address = AAAA_records[0]
#  print(ip6_address)
except:
  print('ERROR - Cannot resolve IPv6 record.')
  exit(1)

#### Step 2 - Fetch the current host definition if any
###############################################################################

hosts_file = Hosts(path = '/etc/hosts')

# Unless we find a problem with the records, no update is needed.
record_update = False

try:
  if(hosts_file.exists(names = [target_host])):
    entries = hosts_file.find_all_matching(name = target_host)
    for entry in entries:
      if (entry.entry_type == 'ipv4'):
        if(entry.address != ip4_address):
          record_update = True
      elif (entry.entry_type == 'ipv6'):
        if(entry.address != ip6_address):
          record_update = True
  else:
    record_update = True
except:
  print('ERROR - Cannot check /etc/hosts existing records.')
  exit(1)

#### Step 3 - Update the records if needed
###############################################################################
# If needed, erase existing records and create new ones.

if(record_update == True):
  try:
    hosts_file.remove_all_matching(name = target_host)
    new_entry_ipv4 = HostsEntry(entry_type='ipv4', address=ip4_address, names=[target_host])
    new_entry_ipv6 = HostsEntry(entry_type='ipv6', address=ip6_address, names=[target_host])
    hosts_file.add([new_entry_ipv4, new_entry_ipv6])
    hosts_file.write()
  except:
    print('ERROR - Cannot update /etc/hosts file with new records.')
    exit(1)

exit(0)
