# Tool Development Standards and Security Guidelines

## Overview

CAI tools are the fundamental building blocks that enable agents to perform cybersecurity tasks. All tools must adhere to strict security, ethical, and quality standards to ensure responsible and effective operation.

## Tool Architecture and Organization

### Kill Chain Organization

Tools are organized according to the Cyber Kill Chain methodology:

1. **Reconnaissance** (`cai/tools/reconnaissance/`): Passive and active information gathering
2. **Weaponization** (`cai/tools/exploitation/`): Exploit development and payload preparation  
3. **Delivery** (`cai/tools/web/`): Web application and service testing
4. **Exploitation** (`cai/tools/exploitation/`): Controlled vulnerability exploitation
5. **Installation** (`cai/tools/lateral_movement/`): Persistence and privilege escalation
6. **Command & Control** (`cai/tools/command_and_control/`): Remote access and management
7. **Actions on Objectives** (`cai/tools/data_exfiltration/`): Data analysis and evidence collection

### Supporting Categories

- **Network Tools** (`cai/tools/network/`): Network analysis and monitoring
- **Utility Tools** (`cai/tools/misc/`): Common functions and utilities
- **Platform Integration** (`cai/tools/web/bug_bounty_platforms.py`): External platform APIs

## Tool Development Standards

### Base Tool Template

```python
"""
Tool: [TOOL_NAME]
Category: [KILL_CHAIN_PHASE]
Description: [BRIEF_DESCRIPTION]
Safety Level: [passive|controlled|authorized_only]
"""

import os
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime

from cai.tools.common import ToolResult, require_authorization, log_activity, assess_impact

logger = logging.getLogger(__name__)

@dataclass
class ToolConfig:
    """Configuration for the security tool."""
    timeout: int = 30
    max_retries: int = 3
    safety_level: str = "controlled"
    authorization_required: bool = True

@require_authorization
@log_activity
def security_tool(
    target: str,
    options: Optional[Dict[str, Any]] = None,
    authorized: bool = False,
    **kwargs
) -> ToolResult:
    """
    [DETAILED_TOOL_DESCRIPTION]
    
    Args:
        target: Target system, IP, or URL for analysis
        options: Tool-specific configuration options
        authorized: Explicit authorization flag (required for active tools)
        **kwargs: Additional tool parameters
        
    Returns:
        ToolResult containing findings, evidence, and remediation guidance
        
    Raises:
        UnauthorizedException: If authorization not provided for active tools
        ValidationException: If target or parameters are invalid
        SecurityException: If safety checks fail
        
    Security Considerations:
        - [SPECIFIC_SECURITY_CONSIDERATIONS]
        - [IMPACT_ASSESSMENT]
        - [REMEDIATION_REQUIREMENTS]
        
    Example:
        >>> result = security_tool("192.168.1.1", authorized=True)
        >>> print(result.findings)
        >>> print(result.remediation)
    """
    
    # Validate inputs and authorization
    _validate_authorization(authorized)
    _validate_target(target)
    _validate_options(options or {})
    
    # Assess potential impact
    impact = assess_impact(target, "security_tool", options)
    if impact.level > ImpactLevel.LOW and not authorized:
        raise SecurityException(f"High impact operation requires explicit authorization: {impact.description}")
    
    try:
        # Tool implementation
        findings = _execute_tool_logic(target, options, **kwargs)
        
        # Generate remediation guidance
        remediation = _generate_remediation(findings)
        
        # Create audit trail
        _create_audit_entry(target, findings, remediation)
        
        return ToolResult(
            success=True,
            findings=findings,
            remediation=remediation,
            metadata={
                "tool": "security_tool",
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "impact_level": impact.level.value,
            }
        )
        
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", extra={"target": target, "error": str(e)})
        return ToolResult(
            success=False,
            error=str(e),
            remediation="Review tool configuration and target accessibility"
        )

def _validate_authorization(authorized: bool) -> None:
    """Validate that proper authorization is provided."""
    if not authorized:
        raise UnauthorizedException("Explicit authorization required for security tool execution")

def _validate_target(target: str) -> None:
    """Validate target format and accessibility."""
    if not target or not isinstance(target, str):
        raise ValidationException("Valid target string required")
    
    # Add target-specific validation logic
    # e.g., IP address format, domain validation, scope checking

def _validate_options(options: Dict[str, Any]) -> None:
    """Validate tool options and parameters."""
    # Add option-specific validation logic
    pass

def _execute_tool_logic(target: str, options: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Execute the core tool functionality."""
    # Implement tool-specific logic here
    findings = {}
    
    return findings

def _generate_remediation(findings: Dict[str, Any]) -> List[str]:
    """Generate specific remediation guidance based on findings."""
    remediation = []
    
    # Generate finding-specific remediation steps
    
    return remediation

def _create_audit_entry(target: str, findings: Dict[str, Any], remediation: List[str]) -> None:
    """Create comprehensive audit trail entry."""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": "security_tool",
        "target": target,
        "findings_count": len(findings),
        "remediation_provided": len(remediation) > 0,
        "user": os.getenv("USER", "unknown"),
    }
    
    logger.info("Security tool executed", extra=audit_entry)
```

### Safety and Authorization Framework

#### Authorization Decorators

```python
def require_authorization(func):
    """Decorator requiring explicit authorization for tool execution."""
    def wrapper(*args, **kwargs):
        if not kwargs.get('authorized', False):
            raise UnauthorizedException(
                f"Tool {func.__name__} requires explicit authorization. "
                f"Set authorized=True to confirm permission for this operation."
            )
        return func(*args, **kwargs)
    return wrapper

def passive_tool(func):
    """Decorator for passive tools that don't require authorization."""
    def wrapper(*args, **kwargs):
        # Log passive tool usage but don't require authorization
        logger.info(f"Passive tool {func.__name__} executed", extra={"args": args})
        return func(*args, **kwargs)
    return wrapper
```

#### Impact Assessment

```python
from enum import Enum

class ImpactLevel(Enum):
    PASSIVE = "passive"      # No direct interaction with target
    LOW = "low"              # Minimal interaction, no system changes
    MEDIUM = "medium"        # Active testing, potential for detection
    HIGH = "high"            # Intrusive testing, potential for disruption
    CRITICAL = "critical"    # High risk of system impact

@dataclass
class ImpactAssessment:
    level: ImpactLevel
    description: str
    risks: List[str]
    mitigations: List[str]

def assess_impact(target: str, tool: str, options: Dict[str, Any]) -> ImpactAssessment:
    """Assess potential impact of tool execution."""
    
    # Tool-specific impact assessment logic
    impact_mapping = {
        "nmap_scan": ImpactLevel.LOW,
        "vulnerability_scan": ImpactLevel.MEDIUM,
        "exploit_execution": ImpactLevel.HIGH,
        "payload_delivery": ImpactLevel.CRITICAL,
    }
    
    level = impact_mapping.get(tool, ImpactLevel.MEDIUM)
    
    return ImpactAssessment(
        level=level,
        description=f"Impact assessment for {tool} on {target}",
        risks=_identify_risks(tool, target, options),
        mitigations=_identify_mitigations(tool, target, options)
    )
```

## Tool Categories and Examples

### Reconnaissance Tools

**Purpose**: Information gathering with minimal target interaction

**Examples**:
- `nmap_scan.py`: Network enumeration and service discovery
- `shodan_search.py`: Internet-wide asset discovery
- `dns_enumeration.py`: DNS record analysis and subdomain discovery
- `google_search.py`: OSINT and passive information gathering

**Safety Level**: Passive to Low Impact

**Template**:
```python
@passive_tool  # Most reconnaissance tools are passive
def reconnaissance_tool(target: str, scan_type: str = "basic") -> ToolResult:
    """
    Passive reconnaissance tool for information gathering.
    
    This tool performs passive information gathering without directly
    interacting with the target system.
    """
    pass
```

### Web Security Tools

**Purpose**: Web application security testing and analysis

**Examples**:
- `nikto_scan.py`: Web server vulnerability scanning
- `nuclei_scan.py`: Template-based vulnerability detection
- `directory_busting.py`: Hidden directory and file discovery
- `api_testing.py`: API endpoint testing and analysis

**Safety Level**: Low to Medium Impact

**Template**:
```python
@require_authorization
def web_security_tool(url: str, test_type: str, authorized: bool = False) -> ToolResult:
    """
    Web application security testing tool.
    
    Performs controlled security testing on web applications
    with explicit authorization requirements.
    """
    pass
```

### Exploitation Tools

**Purpose**: Controlled vulnerability exploitation for proof-of-concept

**Examples**:
- `exploit_framework.py`: Controlled exploit execution
- `payload_generator.py`: Security payload generation
- `vulnerability_validator.py`: Proof-of-concept validation

**Safety Level**: High to Critical Impact

**Template**:
```python
@require_authorization
@assess_impact
def exploitation_tool(target: str, exploit_type: str, authorized: bool = False) -> ToolResult:
    """
    Controlled exploitation tool for proof-of-concept validation.
    
    SECURITY WARNING: This tool can potentially disrupt target systems.
    Only use with explicit written authorization and in controlled environments.
    """
    pass
```

### Network Analysis Tools

**Purpose**: Network security analysis and monitoring

**Examples**:
- `traffic_capture.py`: Network traffic capture and analysis
- `protocol_analysis.py`: Protocol-specific security analysis
- `network_monitoring.py`: Real-time network security monitoring

**Safety Level**: Medium Impact

**Template**:
```python
@require_authorization
def network_analysis_tool(interface: str, analysis_type: str, authorized: bool = False) -> ToolResult:
    """
    Network security analysis and monitoring tool.
    
    Performs network traffic analysis and security monitoring
    with appropriate authorization and privacy protections.
    """
    pass
```

## Quality Assurance and Testing

### Unit Testing Standards

```python
import pytest
from unittest.mock import patch, MagicMock
from cai.tools.reconnaissance.example_tool import reconnaissance_tool
from cai.tools.common import UnauthorizedException, ToolResult

class TestReconnaissanceTool:
    """Comprehensive test suite for reconnaissance tools."""
    
    def test_tool_requires_valid_target(self):
        """Test that tool validates target input."""
        with pytest.raises(ValidationException):
            reconnaissance_tool("")
            
    def test_tool_authorization_enforcement(self):
        """Test authorization requirement for active tools."""
        with pytest.raises(UnauthorizedException):
            active_security_tool("target.example.com", authorized=False)
    
    def test_tool_successful_execution(self):
        """Test successful tool execution with proper inputs."""
        result = reconnaissance_tool("target.example.com")
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.findings is not None
        
    @patch('external_service.api_call')
    def test_tool_external_api_integration(self, mock_api):
        """Test external API integration with mocking."""
        mock_api.return_value = {"status": "success", "data": {}}
        
        result = reconnaissance_tool("target.example.com")
        assert result.success is True
        mock_api.assert_called_once()
        
    def test_tool_error_handling(self):
        """Test proper error handling and recovery."""
        with patch('external_service.api_call', side_effect=Exception("API Error")):
            result = reconnaissance_tool("target.example.com")
            assert result.success is False
            assert "API Error" in result.error
```

### Integration Testing

```python
class TestToolIntegration:
    """Integration tests for tool coordination and handoffs."""
    
    def test_agent_tool_integration(self):
        """Test agent and tool integration."""
        agent = BugBountyAgent()
        result = agent.run(["Scan target.example.com for vulnerabilities"])
        
        assert any("reconnaissance_tool" in msg for msg in result.messages)
        assert any("vulnerability_scan" in msg for msg in result.messages)
        
    def test_tool_handoff_workflow(self):
        """Test tool handoff between different categories."""
        # Test reconnaissance -> web security -> exploitation workflow
        pass
```

### Security Testing

```python
class TestToolSecurity:
    """Security-focused tests for tool safety mechanisms."""
    
    def test_authorization_bypass_prevention(self):
        """Test that authorization cannot be bypassed."""
        # Attempt various authorization bypass techniques
        pass
        
    def test_input_validation_security(self):
        """Test input validation against malicious inputs."""
        malicious_inputs = [
            "../../../etc/passwd",
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValidationException):
                reconnaissance_tool(malicious_input)
                
    def test_output_sanitization(self):
        """Test that tool outputs are properly sanitized."""
        result = reconnaissance_tool("target.example.com")
        
        # Verify no sensitive information in outputs
        assert "password" not in str(result.findings).lower()
        assert "api_key" not in str(result.findings).lower()
```

## Documentation Standards

### Tool Documentation Template

```python
"""
Tool: [TOOL_NAME]
Version: [VERSION]
Author: [AUTHOR]
Category: [KILL_CHAIN_PHASE]
Safety Level: [SAFETY_LEVEL]

Description:
    [DETAILED_DESCRIPTION_OF_TOOL_PURPOSE_AND_FUNCTIONALITY]

Capabilities:
    - [CAPABILITY_1]
    - [CAPABILITY_2]
    - [CAPABILITY_N]

Security Considerations:
    - [SECURITY_CONSIDERATION_1]
    - [SECURITY_CONSIDERATION_2]
    - [SECURITY_CONSIDERATION_N]

Usage Examples:
    Basic usage:
        >>> result = tool_function("target.example.com", authorized=True)
        >>> print(result.findings)

    Advanced usage:
        >>> options = {"scan_type": "comprehensive", "timeout": 60}
        >>> result = tool_function("target.example.com", options=options, authorized=True)

Dependencies:
    - [DEPENDENCY_1]: [PURPOSE]
    - [DEPENDENCY_2]: [PURPOSE]

References:
    - [REFERENCE_1]: [URL_OR_CITATION]
    - [REFERENCE_2]: [URL_OR_CITATION]
"""
```

## Platform Integration Guidelines

### Bug Bounty Platform Integration

```python
def submit_to_platform(finding: Dict[str, Any], platform: str) -> ToolResult:
    """
    Submit security finding to bug bounty platform.
    
    Handles platform-specific formatting and submission requirements
    while maintaining responsible disclosure practices.
    """
    
    platform_handlers = {
        "hackerone": _submit_to_hackerone,
        "bugcrowd": _submit_to_bugcrowd,
    }
    
    if platform not in platform_handlers:
        raise ValueError(f"Unsupported platform: {platform}")
    
    # Validate finding completeness
    _validate_finding_for_submission(finding)
    
    # Submit with appropriate rate limiting
    return platform_handlers[platform](finding)
```

### External API Integration

```python
class ExternalAPIClient:
    """Base class for external API integrations."""
    
    def __init__(self, api_key: str, rate_limit: int = 100):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.session = requests.Session()
        
    def make_request(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make rate-limited API request with proper error handling."""
        
        # Implement rate limiting
        self._enforce_rate_limit()
        
        try:
            response = self.session.get(endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise APIException(f"API request failed: {e}")
```

This comprehensive tool development guide ensures that all CAI tools maintain the highest standards of security, quality, and ethical operation while providing powerful capabilities for cybersecurity professionals.