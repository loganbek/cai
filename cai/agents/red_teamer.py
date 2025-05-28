"""Red Team Base Agent"""
import os
from cai.types import Agent  # pylint: disable=import-error
from cai.util import load_prompt_template  # Add this import
from cai.tools.command_and_control.sshpass import (  # pylint: disable=import-error # noqa: E501
    run_ssh_command_with_credentials
)

from cai.tools.reconnaissance.generic_linux_command import (  # pylint: disable=import-error # noqa: E501
    generic_linux_command
)
from cai.tools.web.search_web import (  # pylint: disable=import-error # noqa: E501
    make_web_search_with_explanation,
)

from cai.tools.reconnaissance.exec_code import (  # pylint: disable=import-error # noqa: E501
    execute_code
)

# RT Tools - Red Team Tools integration
from cai.tools.reconnaissance.gobuster_tool import (  # pylint: disable=import-error # noqa: E501
    gobuster_dir_scan,
    gobuster_dns_scan
)

from cai.tools.reconnaissance.feroxbuster_tool import (  # pylint: disable=import-error # noqa: E501
    feroxbuster_scan,
    feroxbuster_recursive_scan
)

from cai.tools.reconnaissance.dnsrecon_tool import (  # pylint: disable=import-error # noqa: E501
    dnsrecon_standard_scan,
    dnsrecon_bruteforce_scan,
    dnsrecon_axfr_scan,
    dnsrecon_comprehensive_scan
)

from cai.tools.reconnaissance.enum4linux_tool import (  # pylint: disable=import-error # noqa: E501
    enum4linux_basic_scan,
    enum4linux_comprehensive_scan,
    enum4linux_null_session_scan
)

from cai.tools.credential_access.hashcat_tool import (  # pylint: disable=import-error # noqa: E501
    hashcat_identify_hash,
    hashcat_crack_md5,
    hashcat_crack_ntlm,
    hashcat_crack_sha1,
    hashcat_crack_sha256
)

# Prompts
redteam_agent_system_prompt = load_prompt_template("prompts/system_red_team_agent.md")

# Define functions list - core tools
functions = [
    generic_linux_command,
    run_ssh_command_with_credentials,
    execute_code,
]

# Add RT Tools - Red Team Tools from loganbek/RedTeam-Tools
rt_tools = [
    # Directory/File Brute Forcing
    gobuster_dir_scan,
    gobuster_dns_scan,
    feroxbuster_scan,
    feroxbuster_recursive_scan,
    
    # DNS Enumeration
    dnsrecon_standard_scan,
    dnsrecon_bruteforce_scan,
    dnsrecon_axfr_scan,
    dnsrecon_comprehensive_scan,
    
    # SMB/Windows Enumeration  
    enum4linux_basic_scan,
    enum4linux_comprehensive_scan,
    enum4linux_null_session_scan,
    
    # Credential Access
    hashcat_identify_hash,
    hashcat_crack_md5,
    hashcat_crack_ntlm,
    hashcat_crack_sha1,
    hashcat_crack_sha256,
]

functions.extend(rt_tools)

# Add make_web_search_with_explanation function if PERPLEXITY_API_KEY environment variable is set
if os.getenv('PERPLEXITY_API_KEY'):
    functions.append(make_web_search_with_explanation)
    

redteam_agent = Agent(
    name="Red Team Agent",
    instructions=redteam_agent_system_prompt,
    description="""Agent that mimic pentester/red teamer in a security assessment.
                   Expert in cybersecurity and exploitation.""",
    model=os.getenv('CAI_MODEL', "qwen2.5:14b"),
    functions=functions,
    parallel_tool_calls=False,
)