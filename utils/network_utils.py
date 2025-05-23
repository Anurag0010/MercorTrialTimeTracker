"""
Utility module for retrieving network information such as
IP address and MAC address across different platforms.
"""

import socket
import uuid
import platform
import re
import subprocess
import json
from typing import Dict, List, Tuple, Optional, Any, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("network_utils")

def get_hostname() -> str:
    """
    Get the hostname of the current machine.
    
    Returns:
        str: The hostname of the current machine
    """
    try:
        hostname = socket.gethostname()
        logger.debug(f"Hostname retrieved: {hostname}")
        return hostname
    except Exception as e:
        logger.error(f"Error retrieving hostname: {str(e)}")
        return "unknown-host"

def get_ip_address() -> Dict[str, str]:
    """
    Get the IP address of the current machine.
    Attempts to determine the primary external IPv4 address.
    
    Returns:
        dict: Dictionary containing IP addresses by interface
    """
    ip_addresses = {}
    
    # Get hostname
    try:
        hostname = socket.gethostname()
        logger.debug(f"Hostname for IP lookup: {hostname}")
        
        # Get all IP addresses associated with the hostname
        try:
            # This gets all IPs for the local machine
            for addrinfo in socket.getaddrinfo(hostname, None):
                ip = addrinfo[4][0]
                if not ip.startswith('127.') and ':' not in ip:  # Skip loopback and IPv6
                    ip_addresses["primary"] = ip
                    logger.debug(f"Found primary IP from hostname: {ip}")
                    break
        except Exception as e:
            logger.warning(f"Error getting IP addresses from hostname: {str(e)}")
        
        # If no primary IP found, try a different approach
        if "primary" not in ip_addresses:
            try:
                # Try to get the primary IP by connecting to an external server
                # (doesn't actually establish a connection)
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2.0)  # Set timeout to avoid hanging
                s.connect(("8.8.8.8", 80))
                ip_addresses["primary"] = s.getsockname()[0]
                logger.debug(f"Found primary IP using socket connection: {ip_addresses['primary']}")
                s.close()
            except Exception as e:
                logger.warning(f"Error getting primary IP via socket connection: {str(e)}")
                ip_addresses["primary"] = "127.0.0.1"  # Fallback to localhost
                logger.debug("Using fallback localhost IP")
        
        # Get more detailed info on Windows
        if platform.system() == "Windows":
            try:
                # Run ipconfig and parse the output
                logger.debug("Getting Windows network interfaces via ipconfig")
                output = subprocess.check_output("ipconfig /all", shell=True).decode('utf-8')
                interfaces = re.split(r'\r?\nEthernet adapter |Wireless LAN adapter ', output)[1:]
                
                for interface in interfaces:
                    interface_lines = interface.split('\r\n')
                    interface_name = interface_lines[0].strip(':')
                    
                    ipv4_match = re.search(r'IPv4 Address.*: ([\d\.]+)', interface)
                    if ipv4_match:
                        ip_addresses[interface_name] = ipv4_match.group(1)
                        logger.debug(f"Found Windows interface {interface_name} with IP {ipv4_match.group(1)}")
            except Exception as e:
                logger.warning(f"Error getting Windows network interfaces: {str(e)}")
        
        # Get more detailed info on macOS/Linux
        elif platform.system() in ["Darwin", "Linux"]:
            try:
                # Run ifconfig and parse the output
                logger.debug("Getting macOS/Linux network interfaces via ifconfig")
                output = subprocess.check_output(["ifconfig"], stderr=subprocess.STDOUT).decode('utf-8')
                interfaces = re.split(r'\n(?=\w)', output)
                
                for interface in interfaces:
                    interface_match = re.match(r'^(\w+):', interface)
                    if interface_match:
                        interface_name = interface_match.group(1)
                        ipv4_match = re.search(r'inet ([\d\.]+)', interface)
                        if ipv4_match and not ipv4_match.group(1).startswith('127.'):
                            ip_addresses[interface_name] = ipv4_match.group(1)
                            logger.debug(f"Found Unix interface {interface_name} with IP {ipv4_match.group(1)}")
            except Exception as e:
                logger.warning(f"Error getting Unix network interfaces: {str(e)}")
    except Exception as e:
        logger.error(f"Error in get_ip_address: {str(e)}")
        ip_addresses["primary"] = "127.0.0.1"  # Ensure we have at least a fallback
    
    return ip_addresses

def get_mac_address() -> Dict[str, str]:
    """
    Get the MAC address of the current machine.
    Attempts to get MAC addresses for all network interfaces.
    
    Returns:
        dict: Dictionary with interface names as keys and MAC addresses as values
    """
    mac_addresses = {}
    
    # Get a "universal" MAC address (may not be from the active network interface)
    try:
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        mac_addresses["primary"] = mac
    except Exception:
        mac_addresses["primary"] = "00:00:00:00:00:00"
    
    # Get more detailed info on Windows
    if platform.system() == "Windows":
        try:
            # Run ipconfig and parse the output
            output = subprocess.check_output("ipconfig /all", shell=True).decode('utf-8')
            interfaces = re.split(r'\r?\nEthernet adapter |Wireless LAN adapter ', output)[1:]
            
            for interface in interfaces:
                interface_lines = interface.split('\r\n')
                interface_name = interface_lines[0].strip(':')
                
                mac_match = re.search(r'Physical Address.*: ([\dA-F]{2}-[\dA-F]{2}-[\dA-F]{2}-[\dA-F]{2}-[\dA-F]{2}-[\dA-F]{2})', interface)
                if mac_match:
                    mac_addresses[interface_name] = mac_match.group(1).replace('-', ':')
        except Exception:
            pass
    
    # Get more detailed info on macOS/Linux
    elif platform.system() in ["Darwin", "Linux"]:
        try:
            # Run ifconfig and parse the output
            output = subprocess.check_output(["ifconfig"], stderr=subprocess.STDOUT).decode('utf-8')
            interfaces = re.split(r'\n(?=\w)', output)
            
            for interface in interfaces:
                interface_match = re.match(r'^(\w+):', interface)
                if interface_match:
                    interface_name = interface_match.group(1)
                    mac_match = re.search(r'ether ([\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2}:[\da-f]{2})', interface)
                    if mac_match:
                        mac_addresses[interface_name] = mac_match.group(1)
        except Exception:
            pass
    
    return mac_addresses

def get_network_info() -> Dict[str, Any]:
    """
    Get comprehensive network information including hostname, IP addresses, and MAC addresses.
    
    Returns:
        dict: Dictionary containing all network information
    """
    try:
        return {
            "hostname": get_hostname(),
            "ip_addresses": get_ip_address(),
            "mac_addresses": get_mac_address()
        }
    except Exception as e:
        # Provide fallback information if any part fails
        result = {}
        try:
            result["hostname"] = get_hostname()
        except Exception:
            result["hostname"] = "unknown"
        
        try:
            result["ip_addresses"] = get_ip_address()
        except Exception:
            result["ip_addresses"] = {"primary": "127.0.0.1"}
            
        try:
            result["mac_addresses"] = get_mac_address()
        except Exception:
            result["mac_addresses"] = {"primary": "00:00:00:00:00:00"}
            
        return result
def get_active_interface() -> Tuple[Optional[str], Optional[str]]:
    """
    Get the IP and MAC address of the currently active network interface.
    
    Returns:
        tuple: (ip_address, mac_address) of the active interface, or (None, None) if not found
    """
    ip_addresses = get_ip_address()
    mac_addresses = get_mac_address()
    
    # First try to find the active interface
    active_ip = ip_addresses.get("primary")
    active_mac = mac_addresses.get("primary")
    
    # Try to match the active interface between IP and MAC
    for interface in ip_addresses:
        if interface != "primary" and interface in mac_addresses:
            active_ip = ip_addresses[interface]
            active_mac = mac_addresses[interface]
            break
    
    return active_ip, active_mac

def to_json() -> str:
    """
    Get all network information as a JSON string.
    
    Returns:
        str: JSON string with all network information
    """
    return json.dumps(get_network_info(), indent=2)