# Agent Development and Configuration Guide

## Agent Architecture Overview

CAI agents are specialized AI components designed for specific cybersecurity domains. Each agent combines domain expertise, specialized tools, and ethical constraints to provide focused capabilities while maintaining safety and responsibility.

## Core Agent Types

### Bug Bounty Agent (`cai/agents/bug_bounter.py`)

**Purpose**: Web application security testing and responsible vulnerability disclosure

**Capabilities**:
- Web application reconnaissance and enumeration
- Vulnerability identification and proof-of-concept development
- HackerOne and Bugcrowd platform integration
- Automated report generation and submission

**Specialized Tools**:
- Web scanners (Nikto, Nuclei, directory busting)
- API testing and analysis
- Bug bounty platform APIs
- Google search and reconnaissance

**Configuration**:
```python
bug_bounty_agent = Agent(
    name="Bug Bounter",
    instructions=bug_bounter_system_prompt,
    description="Agent specializing in web security and responsible disclosure",
    model=os.getenv('CAI_MODEL', "gpt-4o"),
    functions=web_security_functions,
    parallel_tool_calls=False,
    temperature=0.2,  # Lower temperature for consistent security testing
)
```

**Ethical Constraints**:
- Only test targets within authorized bug bounty program scope
- Follow platform-specific disclosure policies
- Provide detailed reproduction steps and impact assessment
- Prioritize helping organizations improve security

### DFIR Agent (`cai/agents/dfir.py`)

**Purpose**: Digital forensics and incident response

**Capabilities**:
- System and network forensics analysis
- Malware analysis and threat hunting
- Evidence collection and preservation
- Timeline reconstruction and root cause analysis

**Specialized Tools**:
- File system analysis and artifact collection
- Network traffic analysis and protocol inspection
- Memory forensics and process analysis
- Log analysis and correlation

**Configuration**:
```python
dfir_agent = Agent(
    name="DFIR Agent",
    instructions=dfir_agent_system_prompt,
    description="Digital forensics and incident response specialist",
    model=os.getenv('CAI_MODEL', "gpt-4o"),
    functions=forensics_functions,
    parallel_tool_calls=True,  # Can analyze multiple artifacts simultaneously
)
```

**Ethical Constraints**:
- Maintain chain of custody for digital evidence
- Preserve original evidence integrity
- Follow legal requirements for evidence handling
- Respect privacy and data protection regulations

### Red Team Agent (`cai/agents/red_teamer.py`)

**Purpose**: Offensive security and penetration testing

**Capabilities**:
- Attack simulation and adversary emulation
- Penetration testing across multiple attack vectors
- Security control effectiveness assessment
- Attack path analysis and exploitation

**Specialized Tools**:
- Exploitation frameworks and payloads
- Lateral movement and privilege escalation
- Social engineering simulation
- Network penetration and wireless security

**Configuration**:
```python
red_team_agent = Agent(
    name="Red Team Agent",
    instructions=red_team_system_prompt,
    description="Offensive security and penetration testing specialist",
    model=os.getenv('CAI_MODEL', "gpt-4o"),
    functions=offensive_functions,
    parallel_tool_calls=False,  # Sequential testing for safety
    temperature=0.1,  # Very low temperature for careful exploitation
)
```

**Ethical Constraints**:
- Require explicit written authorization for all testing
- Maintain strict scope boundaries and limitations
- Minimize system disruption and data exposure
- Provide immediate remediation guidance

### Blue Team Agent (`cai/agents/blue_teamer.py`)

**Purpose**: Defensive security and threat hunting

**Capabilities**:
- Threat detection and analysis
- Security monitoring and alerting
- Defensive strategy development
- Security control implementation

**Specialized Tools**:
- SIEM analysis and log correlation
- Threat intelligence integration
- Security monitoring and alerting
- Incident response automation

**Configuration**:
```python
blue_team_agent = Agent(
    name="Blue Team Agent",
    instructions=blue_team_system_prompt,
    description="Defensive security and threat hunting specialist",
    model=os.getenv('CAI_MODEL', "gpt-4o"),
    functions=defensive_functions,
    parallel_tool_calls=True,  # Can monitor multiple sources
)
```

**Ethical Constraints**:
- Prioritize system protection and availability
- Respect privacy while maintaining security
- Focus on proactive defense and improvement
- Collaborate with security teams and stakeholders

### Network Traffic Analyzer (`cai/agents/networktraffic_analyzer.py`)

**Purpose**: Network security analysis and monitoring

**Capabilities**:
- Real-time traffic analysis and anomaly detection
- Protocol analysis and security assessment
- Network forensics and evidence collection
- Attack pattern identification and classification

**Specialized Tools**:
- Packet capture and analysis
- Protocol decoders and analyzers
- Network monitoring and alerting
- Traffic visualization and reporting

**Configuration**:
```python
network_analyzer_agent = Agent(
    name="Network Security Analyzer",
    instructions=network_security_analyzer_prompt,
    description="Network security analysis and monitoring specialist",
    model=os.getenv('CAI_MODEL', "gpt-4o"),
    functions=network_analysis_functions,
    parallel_tool_calls=True,  # Can analyze multiple streams
)
```

**Ethical Constraints**:
- Only monitor authorized network segments
- Respect privacy and data protection requirements
- Focus on security improvement and threat detection
- Maintain confidentiality of network architecture

### Code Agent (`cai/agents/codeagent.py`)

**Purpose**: Secure code generation and analysis

**Capabilities**:
- Secure code generation with built-in safety checks
- Code review and vulnerability analysis
- Automated testing and validation
- Security-focused refactoring and optimization

**Specialized Tools**:
- Code execution in sandboxed environments
- Static and dynamic analysis tools
- Security-focused linting and validation
- Automated test generation

**Configuration**:
```python
code_agent = CodeAgent(
    name="Code Agent",
    description="Secure code generation and analysis specialist",
    model=os.getenv('CAI_MODEL', "gpt-4o"),
    temperature=0.2,  # Lower temperature for consistent code quality
    max_steps=10,
    execution_timeout=150,
)
```

**Ethical Constraints**:
- Generate only secure, well-documented code
- Include comprehensive error handling
- Provide security-focused code reviews
- Emphasize defensive programming practices

## Agent Development Best Practices

### System Prompt Design

1. **Domain Expertise**: Include specific domain knowledge and methodologies
2. **Ethical Guidelines**: Embed responsibility and safety constraints
3. **Tool Integration**: Describe available tools and their appropriate usage
4. **Handoff Procedures**: Define when and how to delegate to other agents

**Example System Prompt Structure**:
```markdown
# Agent Role and Expertise
You are a [DOMAIN] specialist with expertise in [SPECIFIC_AREAS].

# Ethical Guidelines and Constraints
- Always verify authorization before any active testing
- Follow responsible disclosure practices
- Minimize system impact and disruption
- Provide remediation guidance with all findings

# Available Tools and Capabilities
[TOOL_DESCRIPTIONS_AND_USAGE_GUIDELINES]

# Agent Handoff Procedures
When encountering [SPECIFIC_SCENARIOS], hand off to:
- [AGENT_TYPE]: for [SPECIFIC_CAPABILITIES]

# Output Format and Documentation
Provide clear, actionable findings with:
- Detailed reproduction steps
- Impact assessment and risk rating
- Specific remediation recommendations
- References to industry standards and best practices
```

### Tool Integration Patterns

1. **Authorization-First Design**:
```python
def secure_tool_wrapper(func):
    """Decorator ensuring authorization before tool execution."""
    def wrapper(*args, **kwargs):
        if not kwargs.get('authorized', False):
            raise UnauthorizedException("Explicit authorization required")
        return func(*args, **kwargs)
    return wrapper
```

2. **Impact Assessment**:
```python
def assess_tool_impact(target: str, action: str) -> ImpactLevel:
    """Assess potential impact before tool execution."""
    # Implement risk assessment logic
    return impact_level
```

3. **Logging and Audit Trail**:
```python
def log_agent_activity(agent: str, action: str, target: str, result: Any):
    """Comprehensive activity logging for audit trail."""
    logger.info(f"Agent {agent} performed {action} on {target}", 
                extra={"result": result, "timestamp": datetime.now()})
```

### Agent Handoff Implementation

```python
def transfer_to_specialist_agent(context: Dict, target_domain: str) -> Agent:
    """
    Transfer control to specialized agent based on context and domain.
    
    Args:
        context: Current analysis context and findings
        target_domain: Target domain requiring specialized expertise
        
    Returns:
        Appropriate specialist agent for the domain
    """
    specialist_mapping = {
        "web_security": bug_bounty_agent,
        "network_analysis": network_analyzer_agent,
        "forensics": dfir_agent,
        "code_analysis": code_agent,
    }
    
    if target_domain not in specialist_mapping:
        raise ValueError(f"No specialist available for domain: {target_domain}")
    
    return specialist_mapping[target_domain]
```

## Configuration Management

### Environment-Based Configuration

```python
# Agent configuration from environment variables
AGENT_CONFIG = {
    "model": os.getenv('CAI_MODEL', 'gpt-4o'),
    "temperature": float(os.getenv('CAI_TEMPERATURE', '0.1')),
    "max_tokens": int(os.getenv('CAI_MAX_TOKENS', '4000')),
    "timeout": int(os.getenv('CAI_TIMEOUT', '300')),
    "tracing_enabled": os.getenv('CAI_TRACING', 'false').lower() == 'true',
}
```

### Safety Configuration

```python
SAFETY_CONFIG = {
    "require_authorization": True,
    "log_all_activities": True,
    "impact_assessment_required": True,
    "auto_remediation_suggestions": True,
    "responsible_disclosure_mode": True,
}
```

### Platform Integration Configuration

```python
PLATFORM_CONFIG = {
    "hackerone": {
        "api_token": os.getenv('HACKERONE_API_TOKEN'),
        "username": os.getenv('HACKERONE_USERNAME'),
        "rate_limit": 100,  # Requests per hour
    },
    "bugcrowd": {
        "api_token": os.getenv('BUGCROWD_API_TOKEN'),
        "rate_limit": 50,  # Requests per hour
    },
    "shodan": {
        "api_key": os.getenv('SHODAN_API_KEY'),
        "rate_limit": 100,  # Requests per month (free tier)
    },
}
```

This comprehensive agent guide ensures consistent development practices while maintaining the highest standards of security, ethics, and effectiveness across all CAI agent implementations.