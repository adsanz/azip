# AZ IP

A simple python tool to list IPs and filter them. Because Azure management interface sucks

## Installing

```
pip3 install -r requirements.txt
azip.py --help
```

## Requirements

You need valid azure credentials set-up and proper permissions. Also export AZURE_SUBSCRIPTION_ID for it to work.

## Usage

By default with no arguments it will output all network interfaces found in a table with ip, name, location, rg, attached resource and type of resource. You can filter by any of these options:

```
usage: azip.py [-h] [--output OUTPUT] [--ip IP] [--name NAME] [--rg RG] [--location LOCATION] [--attached ATTACHED] [--type TYPE]

options:
  -h, --help           show this help message and exit
  --output OUTPUT      Output format: table or json
  --ip IP              IP address to look up in each interface, if found, the interface will be displayed
  --name NAME          Name to look up in each interface, if found, the interface will be displayed
  --rg RG              Resource Group to look up in each interface, if found, the interfaces in the RG will be displayed
  --location LOCATION  Location to look up in each interface, if found, the interfaces in the location will be displayed
  --attached ATTACHED  Attached resource to look up in each interface, if found, the interfaces attached to the resource will be displayed
  --type TYPE          Type to look up in each interface, if found, the interfaces with the type will be displayed [VM, Private Endpoint, No attached resource]

```