"""Red Team Base Agent"""
import os
from dotenv import load_dotenv
from cai.types import Agent  # pylint: disable=import-error
from cai.util import load_prompt_template  # Add this import
from cai.tools.command_and_control.sshpass import (  # pylint: disable=import-error # noqa: E501
    run_ssh_command_with_credentials
)

from cai.tools.reconnaissance.generic_linux_command import (  # pylint: disable=import-error # noqa: E501
    generic_linux_command
)
from cai.tools.web.search_web import (  # pylint: disable=import-error # noqa: E501
    make_google_search
)

from cai.tools.reconnaissance.exec_code import (  # pylint: disable=import-error # noqa: E501
    execute_code
)

from cai.tools.reconnaissance.shodan import (  # pylint: disable=import-error # noqa: E501
    shodan_search,
    shodan_host_info
)

from cai.tools.web.bug_bounty_platforms import (  # pylint: disable=import-error # noqa: E501
    hackerone_get_programs,
    hackerone_get_program_details,
    hackerone_create_report,
    hackerone_get_report_status,
    bugcrowd_get_programs,
    bugcrowd_get_program_details,
    bugcrowd_create_submission,
    bugcrowd_get_submission_status
)

from cai.tools.misc.reasoning import think  # pylint: disable=import-error
load_dotenv()
# Prompts
bug_bounter_system_prompt = load_prompt_template("prompts/system_bug_bounter.md")
# Define functions list based on available API keys
functions = [
    generic_linux_command,
    execute_code,
    think,
    shodan_search,
    shodan_host_info
]

# Add HackerOne and Bugcrowd tools if API keys are provided
if os.getenv('HACKERONE_API_TOKEN') and os.getenv('HACKERONE_USERNAME'):
    functions.extend([
        hackerone_get_programs,
        hackerone_get_program_details,
        hackerone_create_report,
        hackerone_get_report_status
    ])

if os.getenv('BUGCROWD_API_TOKEN'):
    functions.extend([
        bugcrowd_get_programs,
        bugcrowd_get_program_details,
        bugcrowd_create_submission,
        bugcrowd_get_submission_status
    ])

if os.getenv('GOOGLE_SEARCH_API_KEY') and os.getenv('GOOGLE_SEARCH_CX'):
    functions.append(make_google_search)

bug_bounter_agent = Agent(
    name="Bug Bounter",
    instructions=bug_bounter_system_prompt,
    description="""Agent that specializes in bug bounty hunting and vulnerability discovery.
                   Expert in web security, API testing, and responsible disclosure.""",
    model=os.getenv('CAI_MODEL', "qwen2.5:14b"),
    functions=functions,
    parallel_tool_calls=False,
)