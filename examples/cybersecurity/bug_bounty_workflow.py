"""
Advanced Bug Bounty Workflow Example - CAI Framework
---------------------------------------------------
This script demonstrates a complete bug bounty workflow using CAI with
HackerOne and Bugcrowd integration.
"""

from cai.core import CAI
from cai.agents.bug_bounter import bug_bounter_agent

# Initialize the CAI client
client = CAI()

# Define a complete workflow
workflow_instructions = """
I want to conduct a comprehensive bug bounty workflow for web applications. Let's proceed step by step:

1. First, let's find HackerOne programs that focus on web applications and are in scope.

2. Select one program (preferably with a good reputation and generous rewards) and analyze its scope details.

3. For the selected target, I need you to:
   - Perform initial reconnaissance (domain discovery, technology stack identification)
   - Conduct a basic vulnerability scan
   - Look for common web vulnerabilities (XSS, CSRF, SQLi, etc.)
   - Check for sensitive information disclosure
   - Analyze authentication mechanisms

4. When you find potential vulnerabilities, document them clearly with:
   - Vulnerability title and type
   - Severity assessment (CVSS if possible)
   - Detailed reproduction steps
   - Potential impact
   - Screenshots or code snippets when relevant

5. Prepare a professional report for submission to the platform.

6. After this, let's also check Bugcrowd for any interesting programs and compare with what we found on HackerOne.

Remember to follow responsible disclosure practices and stay within the defined scope at all times.
"""

# Create the message
messages = [{
    "role": "user", 
    "content": workflow_instructions
}]

# Run with debugging enabled
print("Starting complete bug bounty workflow...")
try:
    response = client.run(
        agent=bug_bounter_agent,
        messages=messages,
        debug=1,
        max_turns=20  # Allow more turns for the comprehensive workflow
    )
    print("\n\nWorkflow complete! Check the above output for results and report details.")
except Exception as e:
    print(f"\n\nWorkflow failed with error: {e}")
    print("Check your environment variables and API credentials.")
