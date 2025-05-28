# GitHub Copilot Repository Instructions

## Repository Information

- **Project**: Cybersecurity AI (CAI)
- **Purpose**: A production-ready, lightweight framework for building enterprise-grade cybersecurity AI agents
- **Version**: 0.3.14
- **License**: Dual-licensed under MIT and Proprietary

## Project Architecture

CAI is built on a modular architecture implementing the cyber kill chain methodology through 7 core pillars:

### Core Components

1. **Agents**: Specialized AI components with domain expertise
   - Bug Bounty Agent: Web application security and responsible disclosure
   - DFIR Agent: Digital forensics and incident response
   - Red Team Agent: Offensive security and penetration testing
   - Blue Team Agent: Defensive security and threat hunting
   - Network Analyzer: Network traffic analysis and monitoring
   - Code Agent: Secure code generation and analysis

2. **Tools**: Kill-chain organized security functions
   - **Reconnaissance**: Information gathering (nmap, Shodan, DNS enumeration)
   - **Exploitation**: Controlled vulnerability testing and proof-of-concept
   - **Lateral Movement**: Network traversal and privilege escalation assessment
   - **Command & Control**: Remote access and session management
   - **Data Analysis**: Evidence collection and impact assessment
   - **Web Security**: Application testing (Nikto, Nuclei, directory busting)
   - **Network Security**: Traffic capture, protocol analysis, monitoring

3. **Handoffs**: Inter-agent delegation and coordination mechanisms
4. **Patterns**: Structured design paradigms (Swarm, Hierarchical, Chain-of-Thought)
5. **State Management**: Memory systems (episodic, semantic, contextual)
6. **Tracing**: OpenTelemetry integration with Phoenix for full observability
7. **HITL**: Human-in-the-loop controls and approval mechanisms

### Integration Capabilities

- **LLM Providers**: OpenAI, Anthropic, Google Gemini, Ollama, DeepSeek via LiteLLM
- **Bug Bounty Platforms**: HackerOne and Bugcrowd API integration
- **Memory Systems**: Vector storage with Qdrant for semantic memory
- **Observability**: OpenTelemetry tracing with Phoenix dashboard
- **Deployment**: Docker, local, and cloud-native deployment options

## Coding Standards and Best Practices

### Python Development Standards

1. **Code Style**:
   - Follow PEP 8 guidelines strictly
   - Use pylint for code quality (respect existing pylint directives)
   - Maximum line length: 120 characters
   - Use autopep8 for automatic formatting

2. **Type Safety**:
   - Use type hints for all new functions and methods
   - Include proper return type annotations
   - Leverage Pydantic for data validation and serialization
   - Use Union types and Optional for nullable parameters

3. **Documentation**:
   - Write comprehensive docstrings for all public functions
   - Document complex algorithms and security considerations
   - Include parameter descriptions and return value explanations
   - Provide usage examples for complex tools

4. **Error Handling**:
   - Implement comprehensive error handling for external API calls
   - Use specific exception types rather than generic Exception
   - Provide clear, actionable error messages
   - Log errors with appropriate context for debugging

### Security-Specific Development

1. **Tool Development**:
   ```python
   def security_tool(target: str, authorized: bool = False) -> ToolResult:
       """
       Security tool template with safety checks.
       
       Args:
           target: Target system or application
           authorized: Explicit authorization flag (required)
       
       Returns:
           ToolResult with findings and remediation guidance
       
       Raises:
           UnauthorizedException: If authorization not provided
           SecurityException: If safety checks fail
       """
       if not authorized:
           raise UnauthorizedException("Explicit authorization required")
       
       # Tool implementation with safety checks
       return ToolResult(findings=findings, remediation=remediation)
   ```

2. **Agent Development**:
   - Implement handoff functions for specialized tasks
   - Include system prompts that emphasize ethical constraints
   - Provide clear capability descriptions
   - Implement proper state management

3. **API Integration**:
   - Never hardcode API keys or credentials
   - Use environment variables for all sensitive configuration
   - Implement proper rate limiting and retry logic
   - Validate all external API responses

### Testing Standards

1. **Test Categories**:
   - **Unit Tests**: Individual function and method testing
   - **Integration Tests**: Component interaction testing
   - **Architecture Tests**: Agent coordination and handoff testing
   - **Security Tests**: Safety mechanism validation

2. **Test Structure**:
   ```python
   def test_security_tool_authorization():
       """Test that tools require explicit authorization."""
       with pytest.raises(UnauthorizedException):
           security_tool("target.example.com", authorized=False)
   
   def test_security_tool_with_authorization():
       """Test tool functionality with proper authorization."""
       result = security_tool("target.example.com", authorized=True)
       assert result.findings is not None
       assert result.remediation is not None
   ```

3. **Mock Strategy**:
   - Use unittest.mock for external API dependencies
   - Mock network calls and system interactions in tests
   - Validate API call parameters without making real requests

## File Organization and Module Structure

### Core Structure
- `cai/core.py`: Agent orchestration and execution engine
- `cai/types.py`: Type definitions and data models
- `cai/util.py`: Utility functions and common operations
- `cai/graph.py`: Agent dependency and workflow graphs

### Agent Architecture
- `cai/agents/`: Specialized agent implementations
  - `basic.py`: Base agent template and core functionality
  - `bug_bounter.py`: Bug bounty hunting and platform integration
  - `dfir.py`: Digital forensics and incident response
  - `red_teamer.py`: Offensive security and penetration testing
  - `blue_teamer.py`: Defensive security and threat hunting
  - `networktraffic_analyzer.py`: Network security analysis
  - `codeagent.py`: Secure code generation and analysis

### Tools Organization (Kill Chain Based)
- `cai/tools/reconnaissance/`: Information gathering tools
- `cai/tools/exploitation/`: Controlled vulnerability testing
- `cai/tools/lateral_movement/`: Network traversal assessment
- `cai/tools/command_and_control/`: Remote access management
- `cai/tools/data_exfiltration/`: Evidence collection tools
- `cai/tools/web/`: Web application security testing
- `cai/tools/network/`: Network analysis and monitoring
- `cai/tools/misc/`: Utility and support functions

### Supporting Infrastructure
- `cai/prompts/`: System prompts for different agent types
- `cai/state/`: State management and persistence
- `cai/rag/`: Retrieval-augmented generation and memory
- `examples/`: Usage examples and workflow demonstrations
- `tests/`: Comprehensive test suite with security validation
- `docs/`: Documentation and integration guides

## Development Workflows

### Feature Development Process

1. **Design Phase**:
   - Define security requirements and constraints
   - Identify authorization and safety requirements
   - Design with defensive security in mind

2. **Implementation Phase**:
   - Follow established coding standards
   - Implement comprehensive error handling
   - Include security validation at each step

3. **Testing Phase**:
   - Write unit tests with security scenarios
   - Test authorization and safety mechanisms
   - Validate error handling and edge cases

4. **Documentation Phase**:
   - Document security considerations and limitations
   - Provide clear usage examples and warnings
   - Include remediation guidance where applicable

5. **Review Phase**:
   - Peer review for security implications
   - Validate ethical guidelines compliance
   - Ensure proper authorization mechanisms

### Agent Development Guidelines

When creating new agents:

1. **Base Template**: Start with `cai/agents/basic.py`
2. **Required Components**:
   - Comprehensive system prompt with ethical constraints
   - Specialized tool integration
   - Handoff functions to other agents
   - Proper state management

3. **Security Considerations**:
   - Implement authorization checks
   - Define scope limitations
   - Include safety mechanisms
   - Provide clear capability descriptions

### Tool Development Guidelines

When creating new tools:

1. **Base Template**: Follow patterns in `cai/tools/common.py`
2. **Required Components**:
   - Type hints and comprehensive documentation
   - Authorization verification mechanisms
   - Impact assessment and safety checks
   - Comprehensive error handling and logging

3. **Safety Implementation**:
   ```python
   @require_authorization
   @log_activity
   def security_tool(target: str, **kwargs) -> ToolResult:
       """Tool with built-in safety mechanisms."""
       validate_target_scope(target)
       assess_potential_impact(target, kwargs)
       
       try:
           result = perform_security_action(target, **kwargs)
           provide_remediation_guidance(result)
           return result
       except SecurityException as e:
           log_security_event(e, target)
           raise
   ```

## Recent Features and Integrations

### Bug Bounty Platform Integration
- HackerOne API: Program discovery, report submission, status tracking
- Bugcrowd API: Program management and submission workflow
- Automated workflow: Discovery → Testing → Documentation → Submission

### Advanced Agent Capabilities
- Multi-agent coordination with specialized handoffs
- Memory systems: Episodic, semantic, and contextual memory
- State persistence across sessions and workflows
- Real-time collaboration between offensive and defensive agents

### Enterprise Features
- OpenTelemetry integration for comprehensive tracing
- Phoenix dashboard for execution monitoring and debugging
- Vector storage with Qdrant for intelligent knowledge retrieval
- Multi-provider LLM support with fallback mechanisms

### Deployment and Infrastructure
- Docker containerization with security hardening
- Cloud-native deployment with scalability considerations
- Environment-based configuration management
- Comprehensive logging and audit trail capabilities

## API and Integration Guidelines

### LLM Provider Integration
- Use LiteLLM for unified interface across providers
- Implement graceful fallbacks between providers
- Monitor token usage and implement cost controls
- Cache responses where appropriate for efficiency

### External API Integration
- Always use environment variables for credentials
- Implement comprehensive rate limiting
- Validate all external responses for security
- Provide detailed error messages and retry logic

### Platform-Specific Considerations
- **HackerOne**: Follow platform disclosure policies
- **Bugcrowd**: Respect program-specific requirements
- **Shodan**: Use responsibly and within API limits
- **Google Search**: Implement appropriate usage patterns

This comprehensive framework ensures CAI remains a responsible, effective, and ethically-driven cybersecurity AI platform while providing powerful capabilities for security professionals and researchers.

## Security and Ethical Framework

### Fundamental Principles

1. **Authorization First**: Never perform active testing without explicit written permission
2. **Scope Adherence**: Strictly maintain testing boundaries and authorized targets
3. **Impact Minimization**: Minimize system disruption and avoid data exposure
4. **Responsible Disclosure**: Follow coordinated vulnerability disclosure processes
5. **Documentation**: Maintain detailed logs and provide remediation guidance
6. **Legal Compliance**: Adhere to all applicable laws and regulations

### Ethical Guidelines for AI Development

- **Defensive Focus**: Prioritize helping organizations improve security posture
- **Educational Purpose**: Emphasize learning and security awareness over exploitation
- **Constructive Outcomes**: Focus on building security improvements
- **Collaboration**: Promote cooperation with security teams and stakeholders
- **Transparency**: Document capabilities, limitations, and potential impacts

### Safety by Design

All security tools must implement:
- **Authorization Checks**: Verify permission before execution
- **Impact Assessment**: Evaluate potential system effects
- **Minimal Proof-of-Concept**: Demonstrate vulnerabilities with minimum impact
- **Remediation Guidance**: Provide specific fix recommendations
- **Audit Logging**: Comprehensive activity tracking
