"""
HackerOne and Bugcrowd API integration tools for bug bounty hunting.
These tools enable fetching information about bug bounty programs, scope,
submitting findings and checking submission status through the respective platforms.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union, Any

def hackerone_get_programs(filter_type: str = "active", ctf=None) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Fetch programs from HackerOne API.
    
    Args:
        filter_type: Type of programs to fetch ("active", "eligible", "enrolled", etc)
        ctf: CTF object to use for context
        
    Returns:
        JSON string with program information
    """
    api_token = os.getenv("HACKERONE_API_TOKEN")
    api_username = os.getenv("HACKERONE_USERNAME")
    
    if not api_token or not api_username:
        return "Error: Missing HackerOne API credentials. Set HACKERONE_API_TOKEN and HACKERONE_USERNAME environment variables."
    
    url = "https://api.hackerone.com/v1/hackers/programs"
    headers = {
        "Accept": "application/json"
    }
    
    params = {}
    if filter_type:
        params["filter[type]"] = filter_type
        
    try:
        response = requests.get(
            url, 
            auth=(api_username, api_token),
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def hackerone_get_program_details(program_handle: str, ctf=None) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Fetch details of a specific HackerOne program including scope and policy.
    
    Args:
        program_handle: The handle/slug of the program
        ctf: CTF object to use for context
        
    Returns:
        JSON string with program details
    """
    api_token = os.getenv("HACKERONE_API_TOKEN")
    api_username = os.getenv("HACKERONE_USERNAME")
    
    if not api_token or not api_username:
        return "Error: Missing HackerOne API credentials. Set HACKERONE_API_TOKEN and HACKERONE_USERNAME environment variables."
    
    url = f"https://api.hackerone.com/v1/hackers/programs/{program_handle}"
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            url, 
            auth=(api_username, api_token),
            headers=headers
        )
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def hackerone_create_report(
    program_handle: str, 
    title: str,
    vulnerability_type: str,
    severity: str, 
    summary: str,
    reproduction_steps: str,
    impact: str = "",
    attachments: List[str] = None,
    ctf=None
) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Create a new vulnerability report on HackerOne.
    
    Args:
        program_handle: The handle/slug of the program
        title: Report title
        vulnerability_type: Type of vulnerability
        severity: Severity rating (none, low, medium, high, critical)
        summary: Brief summary of the vulnerability
        reproduction_steps: Detailed steps to reproduce
        impact: Impact of the vulnerability
        attachments: List of file paths to attach
        ctf: CTF object to use for context
        
    Returns:
        JSON string with report submission result
    """
    api_token = os.getenv("HACKERONE_API_TOKEN")
    api_username = os.getenv("HACKERONE_USERNAME")
    
    if not api_token or not api_username:
        return "Error: Missing HackerOne API credentials. Set HACKERONE_API_TOKEN and HACKERONE_USERNAME environment variables."
    
    url = f"https://api.hackerone.com/v1/hackers/reports"
    # Use multipart/form-data for file attachments
    headers = {
        "Accept": "application/json"
    }
    
    data = {
        "data": {
            "type": "report",
            "attributes": {
                "team_handle": program_handle,
                "title": title,
                "vulnerability_information": summary,
                "impact": impact,
                "steps_to_reproduce": reproduction_steps,
                "severity_rating": severity,
                "weakness_id": vulnerability_type,
                # attachments handled via multipart upload
                "attachments": []
            }
        }
    }
    
    try:
        if attachments:
            # Prepare multipart form data: JSON 'data' field and file uploads
            multipart_data = {"data": json.dumps(data)}
            files_payload = []
            for path in attachments:
                files_payload.append(("attachments[]", open(path, "rb")))
            response = requests.post(
                url,
                auth=(api_username, api_token),
                headers=headers,
                data=multipart_data,
                files=files_payload
            )
        else:
            # Standard JSON request when no files
            response = requests.post(
                url,
                auth=(api_username, api_token),
                headers={**headers, "Content-Type": "application/json"},
                json=data
            )
        
        if response.status_code in [200, 201]:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def hackerone_get_report_status(report_id: str, ctf=None) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Get the status of a submitted report on HackerOne.
    
    Args:
        report_id: The ID of the report
        ctf: CTF object to use for context
        
    Returns:
        JSON string with report status
    """
    api_token = os.getenv("HACKERONE_API_TOKEN")
    api_username = os.getenv("HACKERONE_USERNAME")
    
    if not api_token or not api_username:
        return "Error: Missing HackerOne API credentials. Set HACKERONE_API_TOKEN and HACKERONE_USERNAME environment variables."
    
    url = f"https://api.hackerone.com/v1/hackers/reports/{report_id}"
    headers = {
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            url, 
            auth=(api_username, api_token),
            headers=headers
        )
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def bugcrowd_get_programs(ctf=None) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Fetch programs from Bugcrowd API.
    
    Args:
        ctf: CTF object to use for context
        
    Returns:
        JSON string with program information
    """
    api_token = os.getenv("BUGCROWD_API_TOKEN")
    
    if not api_token:
        return "Error: Missing Bugcrowd API token. Set BUGCROWD_API_TOKEN environment variable."
    
    url = "https://api.bugcrowd.com/programs"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {api_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def bugcrowd_get_program_details(program_uuid: str, ctf=None) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Fetch details of a specific Bugcrowd program including scope and targets.
    
    Args:
        program_uuid: The UUID of the program
        ctf: CTF object to use for context
        
    Returns:
        JSON string with program details
    """
    api_token = os.getenv("BUGCROWD_API_TOKEN")
    
    if not api_token:
        return "Error: Missing Bugcrowd API token. Set BUGCROWD_API_TOKEN environment variable."
    
    url = f"https://api.bugcrowd.com/programs/{program_uuid}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {api_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def bugcrowd_create_submission(
    program_uuid: str,
    title: str,
    vulnerability_type: str,
    description: str,
    severity: str,
    steps: str,
    impact: str = "",
    attachments: List[str] = None,
    ctf=None
) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Create a new submission on Bugcrowd.
    
    Args:
        program_uuid: The UUID of the program
        title: Submission title
        vulnerability_type: Type of vulnerability
        description: Description of the vulnerability
        severity: Severity rating (1-5, where 5 is critical)
        steps: Steps to reproduce
        impact: Impact of the vulnerability
        attachments: List of file paths to attach
        ctf: CTF object to use for context
        
    Returns:
        JSON string with submission result
    """
    api_token = os.getenv("BUGCROWD_API_TOKEN")
    
    if not api_token:
        return "Error: Missing Bugcrowd API token. Set BUGCROWD_API_TOKEN environment variable."
    
    url = f"https://api.bugcrowd.com/programs/{program_uuid}/submissions"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {api_token}"
    }
      # Validate severity - must be a valid integer between 1 and 5
    if not severity.isdigit():
        return "Error: Severity must be a valid integer between 1 and 5."
    
    severity_int = int(severity) if severity.isdigit() else 0
     # Check if severity is within the valid range
    if severity_int < 1 or severity_int > 5:
        return "Error: Severity must be between 1 and 5, where 5 is critical."
        
    data = {
        "data": {
            "type": "submission",
            "attributes": {
                "title": title,
                "vulnerability_type": vulnerability_type,
                "description": description,
                "severity": severity_int,
                "steps_to_reproduce": steps,
                "impact": impact
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def bugcrowd_get_submission_status(program_uuid: str, submission_uuid: str, ctf=None) -> str:  # pylint: disable=unused-argument  # noqa: E501
    """
    Get the status of a submitted report on Bugcrowd.
    
    Args:
        program_uuid: The UUID of the program
        submission_uuid: The UUID of the submission
        ctf: CTF object to use for context
        
    Returns:
        JSON string with submission status
    """
    api_token = os.getenv("BUGCROWD_API_TOKEN")
    
    if not api_token:
        return "Error: Missing Bugcrowd API token. Set BUGCROWD_API_TOKEN environment variable."
    
    url = f"https://api.bugcrowd.com/programs/{program_uuid}/submissions/{submission_uuid}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {api_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"
