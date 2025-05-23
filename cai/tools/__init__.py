from .pillaging import (
    extract_ip_addresses,
    extract_software_versions,
    extract_pii,
    extract_credentials,
    run_crackmapexec_and_parse
)
from .reconnaissance import run_nmap_scan
from .web import run_nuclei_scan, run_nikto_scan # Added run_nikto_scan

__all__ = [
    # ... other existing exports ...
    "extract_ip_addresses",
    "extract_software_versions",
    "extract_pii",
    "extract_credentials",
    "run_crackmapexec_and_parse",
    "run_nmap_scan",
    "run_nuclei_scan",
    "run_nikto_scan", # Added to __all__
]