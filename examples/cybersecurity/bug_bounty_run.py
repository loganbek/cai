"""
Bug Bounty Script - CAI Framework
--------------------------------
This script uses the CAI framework to conduct a bug bounty assessment on a target website.
Replace the target URL with the actual target within your authorized scope.
"""

from cai.types import Agent
from cai.core import CAI
from cai.agents.bug_bounter import bug_bounter_agent

# Initialize the CAI client
client = CAI()

# Define your target and instructions
target_url = "https://example.com"  # Replace with your actual target within scope
messages = [{
    "role": "user", 
    "content": f"""I need you to help me analyze potential vulnerabilities in {target_url}
                 
                 Focus on:
                 1. Web application security (XSS, CSRF, injection)
                 2. API endpoints discovery and testing
                 3. Exposed sensitive information
                 4. Authentication/authorization flaws
                 5. Security misconfigurations
                 
                 Please start with reconnaissance and proceed systematically.
                 Document all findings carefully and suggest remediation steps.
                 """
}]

# Run the bug bounty agent
print(f"Starting bug bounty analysis on {target_url}...")
response = client.run(
    agent=bug_bounter_agent,
    messages=messages,
    debug=1,  # Set to 0 to reduce verbosity
    max_turns=10  # Limit the number of turns to prevent excessive API usage
)

print("\n\nAnalysis complete! Review the findings above.")
