from .pillaging import (
    extract_ip_addresses,
    extract_software_versions,
    extract_pii,
    extract_credentials,
    run_crackmapexec_and_parse
)

__all__ = [
    # ... other existing exports ...
    "extract_ip_addresses",
    "extract_software_versions",
    "extract_pii",
    "extract_credentials",
    "run_crackmapexec_and_parse",
]