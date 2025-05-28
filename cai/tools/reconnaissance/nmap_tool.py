"""
Nmap tool for network scanning and host discovery.
"""
import subprocess
import xml.etree.ElementTree as ET
import json

def parse_nmap_xml_output(xml_output: str) -> dict:
    """
    Parses Nmap XML output into a Python dictionary.

    Args:
        xml_output: Nmap XML output as a string.

    Returns:
        A dictionary representing the Nmap scan results.
        Returns an empty dictionary if parsing fails.
    """
    try:
        root = ET.fromstring(xml_output)
        scan_results = {"hosts": []}

        for host_node in root.findall('host'):
            host_info = {
                "status": host_node.find('status').get('state') if host_node.find('status') is not None else 'unknown',
                "addresses": [],
                "hostnames": [],
                "ports": []
            }

            for address_node in host_node.findall('address'):
                host_info["addresses"].append({
                    "addr": address_node.get('addr'),
                    "addrtype": address_node.get('addrtype')
                })

            hostnames_node = host_node.find('hostnames')
            if hostnames_node is not None:
                for hostname_node in hostnames_node.findall('hostname'):
                    host_info["hostnames"].append({
                        "name": hostname_node.get('name'),
                        "type": hostname_node.get('type')
                    })
            
            ports_node = host_node.find('ports')
            if ports_node is not None:
                for port_node in ports_node.findall('port'):
                    port_info = {
                        "protocol": port_node.get('protocol'),
                        "portid": port_node.get('portid'),
                        "state": port_node.find('state').get('state') if port_node.find('state') is not None else 'unknown',
                        "reason": port_node.find('state').get('reason') if port_node.find('state') is not None else 'unknown',
                    }
                    service_node = port_node.find('service')
                    if service_node is not None:
                        port_info["service"] = {
                            "name": service_node.get('name'),
                            "product": service_node.get('product'),
                            "version": service_node.get('version'),
                            "extrainfo": service_node.get('extrainfo'),
                            "method": service_node.get('method'),
                            "conf": service_node.get('conf')
                        }
                        # Remove None values from service_info
                        port_info["service"] = {k: v for k, v in port_info["service"].items() if v is not None}
                    
                    script_nodes = port_node.findall('script')
                    if script_nodes:
                        port_info["scripts"] = []
                        for script_node in script_nodes:
                            port_info["scripts"].append({
                                "id": script_node.get('id'),
                                "output": script_node.get('output')
                            })
                    host_info["ports"].append(port_info)
            
            scan_results["hosts"].append(host_info)
        
        # Add runstats like finished time, hosts up/down etc.
        runstats_node = root.find('runstats')
        if runstats_node is not None:
            scan_results['runstats'] = {
                'finished': runstats_node.find('finished').get('timestr') if runstats_node.find('finished') is not None else None,
                'elapsed': runstats_node.find('finished').get('elapsed') if runstats_node.find('finished') is not None else None,
                'summary': runstats_node.find('finished').get('summary') if runstats_node.find('finished') is not None else None,
                'hosts_up': runstats_node.find('hosts').get('up') if runstats_node.find('hosts') is not None else None,
                'hosts_down': runstats_node.find('hosts').get('down') if runstats_node.find('hosts') is not None else None,
                'hosts_total': runstats_node.find('hosts').get('total') if runstats_node.find('hosts') is not None else None,
            }
            scan_results['runstats'] = {k: v for k, v in scan_results['runstats'].items() if v is not None}

        return scan_results
    except ET.ParseError as e:
        # Consider logging the error
        print(f"Error parsing Nmap XML: {e}")
        return {"error": "Failed to parse Nmap XML output", "details": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred during Nmap XML parsing: {e}")
        return {"error": "An unexpected error occurred during Nmap XML parsing", "details": str(e)}

def run_nmap_scan(targets: list[str], options: list[str] = None) -> dict:
    """
    Runs an Nmap scan against the specified targets with given options.

    Args:
        targets: A list of IP addresses, hostnames, or network ranges.
        options: A list of Nmap command-line options (e.g., ["-sV", "-p-"]).
                 The -oX - option for XML output is added automatically.

    Returns:
        A dictionary containing the parsed Nmap scan results or an error message.
    """
    if not targets:
        return {"error": "No targets specified for Nmap scan."}

    command = ["nmap"]
    if options:
        # Filter out any user-supplied XML output options to avoid conflict
        options = [opt for opt in options if not opt.startswith(('-oX', '-oA', '-oG', '-oS', '-oN'))]
        command.extend(options)
    
    command.extend(targets)
    command.append("-oX")  # Output in XML format
    command.append("-")     # Output to stdout

    try:
        print(f"Running Nmap command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        if process.returncode != 0:
            # Nmap might return non-zero for various reasons even with partial success (e.g. host down)
            # We still try to parse if there's any output.
            error_message = f"Nmap process exited with error code {process.returncode}."
            if process.stderr:
                error_message += f" Stderr: {process.stderr.strip()}"
            if not process.stdout:  # If no stdout, it's a more definite failure
                return {"error": error_message}
            # If there is stdout, proceed to parse, but include the error in the result
            parsed_output = parse_nmap_xml_output(process.stdout)
            if "error" not in parsed_output: # if parsing itself didn't error
                 parsed_output["warning"] = error_message # Add nmap execution error as warning
            else: # if parsing also errored, combine messages
                parsed_output["details"] = f"{parsed_output.get('details', '')}; Nmap execution: {error_message}"
            return parsed_output

        if not process.stdout:
            return {"error": "Nmap produced no output."}
        
        return parse_nmap_xml_output(process.stdout)

    except FileNotFoundError:
        return {"error": "Nmap command not found. Please ensure Nmap is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running Nmap: {str(e)}"}

if __name__ == '__main__':
    # Example Usage (requires Nmap to be installed and a host to scan)
    # Replace 'scanme.nmap.org' with a target you are authorized to scan.
    # For local testing, you can use 'localhost' or an IP on your local network.
    print("Starting Nmap tool example...")
    # test_targets = ["scanme.nmap.org"]
    test_targets = ["localhost"] # Use localhost for a safe, quick test
    # test_options = ["-sV", "-T4", "-F"] # Service Version, Aggressive Timing, Fast Scan (top 100 ports)
    test_options = ["-T4", "-F"] # Fast Scan on localhost
    
    print(f"Scanning targets: {test_targets} with options: {test_options}")
    results = run_nmap_scan(test_targets, test_options)
    
    print("\nNmap Scan Results:")
    print(json.dumps(results, indent=2))