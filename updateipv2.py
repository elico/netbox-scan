#!/usr/bin/env python3

# Script which updating ip addresses in netbox
# We need install pip3 install ipcalc networkscan python-netbox
# Don't forget to change your ip-address of netbox and token
# Define you scan ip range in variable my_network
# If you use https(SSL) in netbox API change port to 443

import ipcalc
import networkscan
from netbox import NetBox
import requests
import datetime
import sys

NET = sys.argv[1]
HOSTNAME = sys.argv[2]
API_TOKEN = sys.argv[3]

HEADERS = {'Authorization': f'Token {API_TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
NB_URL = f"http://{HOSTNAME}"
netbox = NetBox(host=f"{HOSTNAME}", port=80, use_ssl=False, auth_token=f'{API_TOKEN}')



if __name__ == '__main__':
    # Define the network to scan
    my_network = f"{NET}"
   
    # Create the object
    my_scan = networkscan.Networkscan(my_network)
    
    # Run the scan of hosts using pings
    my_scan.run()

    # Here we define exists ip address in our network and write it to list    
    found_ip_in_network = []
    for address1 in my_scan.list_of_hosts_found:
        found_ip_in_network.append(str(address1))
    
    # Get all ip from prefix
    for ipaddress in ipcalc.Network(my_network):
        # Doing get request to netbox
        request_url = f"{NB_URL}/api/ipam/ip-addresses/?q={ipaddress}/"
        ipaddress1 = requests.get(request_url, headers = HEADERS)
        netboxip = ipaddress1.json()
        print(ipaddress)
        print(netboxip)
        print(netboxip['count'])
        # If not in netbox
        if netboxip['count'] == 0:
            # Check if in network exists and not exist in netbox
            if ipaddress in found_ip_in_network:
                # Adding in IP netbox
                netbox.ipam.create_ip_address(str(ipaddress))
            else:
                pass        
        else:
            #If not exists in netbox and network
            if ipaddress in found_ip_in_network:
                netbox.ipam.update_ip(str(ipaddress),status="active")
            else:
                # If not exists in network but exists in netbox then delete from netbox
                #netbox.ipam.delete_ip_address(str(ipaddress))
                netbox.ipam.update_ip(str(ipaddress),status="deprecated")
                
