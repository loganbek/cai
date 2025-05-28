from .pillaging import (
    extract_ip_addresses,
    extract_software_versions,
    extract_pii,
    extract_credentials,
    run_crackmapexec_and_parse
)
from .reconnaissance import run_nmap_scan
from .web import run_nuclei_scan, run_nikto_scan
from .privilege_scalation import run_linpeas

__all__ = [
    # ... other existing exports ...
    "extract_ip_addresses",
    "extract_software_versions",
    "extract_pii",
    "extract_credentials",
    "run_crackmapexec_and_parse",
    "run_nmap_scan",
    "run_nuclei_scan",
    "run_nikto_scan",
    "run_linpeas",
]