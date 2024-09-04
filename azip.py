#!/usr/bin/env python3
try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.network import NetworkManagementClient
    from azure.mgmt.compute.v2024_07_01 import ComputeManagementClient
    import azure.mgmt.network.models
    import os
    import argparse
    from tabulate import tabulate
    import json
    import re
    from dataclasses import dataclass
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run 'pip install -r requirements.txt'")
    exit(1)


@dataclass
class AZIP:
    headers = ["IP", "Name", "RG", "Location", "Attached resource", "Type"]
    args = argparse.ArgumentParser()

    def arg_builder(self):
        self.args.add_argument("--output", help="Output format: table or json")
        self.args.add_argument(
            "--ip",
            help="IP address to look up in each interface, if found, the interface will be displayed",
        )
        self.args.add_argument(
            "--name",
            help="Name to look up in each interface, if found, the interface will be displayed",
        )
        self.args.add_argument(
            "--rg",
            help="Resource Group to look up in each interface, if found, the interfaces in the RG will be displayed",
        )
        self.args.add_argument(
            "--location",
            help="Location to look up in each interface, if found, the interfaces in the location will be displayed",
        )
        self.args.add_argument(
            "--attached",
            help="Attached resource to look up in each interface, if found, the interfaces attached to the resource will be displayed",
        )
        self.args.add_argument(
            "--type",
            help="Type to look up in each interface, if found, the interfaces with the type will be displayed [VM, Private Endpoint, No attached resource]",
        )
        self.args = self.args.parse_args()

    def inet_getter(self) -> list[azure.mgmt.network.models.NetworkInterface]:
        self.credential = DefaultAzureCredential()
        self.subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        self.network_client = NetworkManagementClient(
            self.credential, self.subscription_id, api_version="2023-09-01"
        )  # using the default latest API version causes this to fail
        self.compute_client = ComputeManagementClient(
            self.credential, self.subscription_id
        )
        # Get all network interfaces
        all_network_interfaces = list(self.network_client.network_interfaces.list_all())
        # Get all scale sets
        all_scale_sets = self.compute_client.virtual_machine_scale_sets.list_all()
        # Get network interfaces for each scale set
        for scale_set in all_scale_sets:
            try:
                scale_set_network_interfaces = self.network_client.network_interfaces.list_virtual_machine_scale_set_network_interfaces(
                    virtual_machine_scale_set_name=scale_set.name,
                    resource_group_name=scale_set.id.split("/")[4],
                )
                for inet in scale_set_network_interfaces:
                    all_network_interfaces.append(inet)
            except Exception as e:
                print(f"Error: {e}")
                continue
        return all_network_interfaces

    def regex_filter(self, table: list) -> list:
        ip_regex = re.compile(self.args.ip) if self.args.ip else None
        name_regex = re.compile(self.args.name) if self.args.name else None
        rg_regex = re.compile(self.args.rg) if self.args.rg else None
        location_regex = re.compile(self.args.location) if self.args.location else None
        attached_regex = re.compile(self.args.attached) if self.args.attached else None
        type_regex = re.compile(self.args.type) if self.args.type else None
        filtered_table = []
        for row in table:
            if ip_regex and ip_regex.search(row[0]):
                filtered_table.append(row)
            elif name_regex and name_regex.search(row[1]):
                filtered_table.append(row)
            elif rg_regex and rg_regex.search(row[2]):
                filtered_table.append(row)
            elif location_regex and location_regex.search(row[3]):
                filtered_table.append(row)
            elif attached_regex and attached_regex.search(row[4]):
                filtered_table.append(row)
            elif type_regex and type_regex.search(row[5]):
                filtered_table.append(row)
            else:
                continue
        if (
            not ip_regex
            and not name_regex
            and not rg_regex
            and not location_regex
            and not attached_regex
            and not type_regex
        ):
            return table
        elif not filtered_table:
            raise Exception("No interfaces found with the specified filters")
        return filtered_table

    def table_builder(
        self, inet_list: azure.mgmt.network.models.NetworkInterface
    ) -> list:
        table = []
        for inet in inet_list:
            attached_resource = (
                inet.virtual_machine.id
                if inet.virtual_machine
                else inet.private_endpoint.id
                if inet.private_endpoint
                else "No attached resource"
            )
            table.append(
                [
                    inet.ip_configurations[0].private_ip_address,
                    inet.name,
                    inet.id.split("/")[4],
                    inet.location,
                    attached_resource.split("/")[8]
                    if attached_resource != "No attached resource"
                    else "No attached resource",
                    "VM"
                    if inet.virtual_machine
                    else "Private Endpoint"
                    if inet.private_endpoint
                    else "No attached resource",
                ]
            )
        return table

    def output(self, table: list, headers: list):
        if self.args.output == "json":
            json_table = []
            for row in table:
                json_table.append(
                    {
                        "IP": row[0],
                        "Name": row[1],
                        "Resource Group": row[2],
                        "Location": row[3],
                        "Attached resource": row[4],
                        "Type": row[5],
                    }
                )
            print(json.dumps(json_table, indent=4))
        else:
            print(tabulate(table, headers=headers))


if __name__ == "__main__":
    azip = AZIP()
    azip.arg_builder()
    inet_list = azip.inet_getter()
    table = azip.table_builder(inet_list)
    table = azip.regex_filter(table)
    azip.output(table, azip.headers)
