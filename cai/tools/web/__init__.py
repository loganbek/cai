"""
Web related tools for CAI
"""

from .search_web import search_web, make_google_search
from .headers import check_headers
from .bug_bounty_platforms import (
    hackerone_get_programs,
    hackerone_get_program_details,
    hackerone_create_report,
    hackerone_get_report_status,
    bugcrowd_get_programs,
    bugcrowd_get_program_details,
    bugcrowd_create_submission,
    bugcrowd_get_submission_status
)
from .nuclei_tool import run_nuclei_scan
from .nikto_tool import run_nikto_scan

__all__ = [
    "search_web",
    "make_google_search",
    "check_headers",
    "hackerone_get_programs",
    "hackerone_get_program_details",
    "hackerone_create_report",
    "hackerone_get_report_status",
    "bugcrowd_get_programs",
    "bugcrowd_get_program_details",
    "bugcrowd_create_submission",
    "bugcrowd_get_submission_status",
    "run_nuclei_scan",
    "run_nikto_scan",
]