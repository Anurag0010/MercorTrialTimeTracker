#!/usr/bin/env python3
"""
Test script for network_utils module.
This script tests all the network utility functions and displays the results.
"""

import sys
import os
from utils.network_utils import (
    get_hostname,
    get_ip_address,
    get_mac_address,
    get_network_info,
    get_active_interface,
    to_json
)

def test_network_utils():
    """Test all network utility functions and display results"""
    print("=" * 50)
    print("NETWORK UTILITIES TEST")
    print("=" * 50)
    
    # Test hostname retrieval
    print("\n1. HOSTNAME")
    print("-" * 50)
    try:
        hostname = get_hostname()
        print(f"Hostname: {hostname}")
    except Exception as e:
        print(f"Error getting hostname: {str(e)}")
    
    # Test IP address retrieval
    print("\n2. IP ADDRESSES")
    print("-" * 50)
    try:
        ip_addresses = get_ip_address()
        print("IP Addresses:")
        for interface, ip in ip_addresses.items():
            print(f"  • {interface}: {ip}")
    except Exception as e:
        print(f"Error getting IP addresses: {str(e)}")
    
    # Test MAC address retrieval
    print("\n3. MAC ADDRESSES")
    print("-" * 50)
    try:
        mac_addresses = get_mac_address()
        print("MAC Addresses:")
        for interface, mac in mac_addresses.items():
            print(f"  • {interface}: {mac}")
    except Exception as e:
        print(f"Error getting MAC addresses: {str(e)}")
    
    # Test active interface retrieval
    print("\n4. ACTIVE INTERFACE")
    print("-" * 50)
    try:
        ip, mac = get_active_interface()
        print(f"Active Interface IP: {ip}")
        print(f"Active Interface MAC: {mac}")
    except Exception as e:
        print(f"Error getting active interface: {str(e)}")
    
    # Test comprehensive network info retrieval
    print("\n5. COMPLETE NETWORK INFO (JSON)")
    print("-" * 50)
    try:
        print(to_json())
    except Exception as e:
        print(f"Error getting network info JSON: {str(e)}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_network_utils()