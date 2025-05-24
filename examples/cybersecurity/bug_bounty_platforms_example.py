"""
Bug Bounty Platform Integration Example - CAI Framework
------------------------------------------------------
This script demonstrates using CAI with HackerOne and Bugcrowd integration for bug bounty hunting.
"""

from cai.core import CAI
from cai.agents.bug_bounter import bug_bounter_agent

# Initialize the CAI client
client = CAI()

# Define your bug bounty operations
messages = [{
    "role": "user", 
    "content": """I need to manage my bug bounty hunting activities with both HackerOne and Bugcrowd.

First, list all active HackerOne programs I can participate in.
Then, for the top program, get detailed information about its scope.

After that, help me analyze the target website in the scope for potential vulnerabilities.
Once we find something, prepare a report for submission to the platform.

Similarly, I want to check Bugcrowd for programs and prepare submissions there as well.
"""
}]

# Run with debugging enabled
print("Starting bug bounty platform integration...")
response = client.run(
    agent=bug_bounter_agent,
    messages=messages,
    debug=1,
    max_turns=15
)

print("\n\nIntegration test complete!")
