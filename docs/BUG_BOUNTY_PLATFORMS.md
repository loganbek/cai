# HackerOne and Bugcrowd Integration for CAI

This document provides information on how to set up and use the HackerOne and Bugcrowd API integration within the CAI (Cybersecurity AI) framework for bug bounty hunting.

## Setup

### 1. API Credentials

First, you need to acquire API credentials from the respective platforms:

#### HackerOne

1. Create or log into your HackerOne account
2. Go to your [API token settings](https://hackerone.com/settings/api_token)
3. Generate a new API token with appropriate permissions
4. Note your username and API token
5. For more detailed instructions, see our [API Keys Guide](API_KEYS.md#hackerone)

#### Bugcrowd

1. Create or log into your Bugcrowd account
2. Request API access from Bugcrowd (as of 2023, API access requires approval)
3. For more detailed instructions, see our [API Keys Guide](API_KEYS.md#bugcrowd)
4. Once approved, generate an API token from your account settings
5. Save your API token

### 2. Environment Configuration

Add your API credentials to your `.env` file:

```bash
# HackerOne Credentials
HACKERONE_API_TOKEN="your_h1_api_token"
HACKERONE_USERNAME="your_h1_username"

# Bugcrowd Credentials
BUGCROWD_API_TOKEN="your_bugcrowd_api_token"
```

## Available Functions

### HackerOne Functions

| Function | Description |
|----------|-------------|
| `hackerone_get_programs` | Fetch available programs on HackerOne |
| `hackerone_get_program_details` | Get detailed information about a specific program |
| `hackerone_create_report` | Submit a vulnerability report to a program |
| `hackerone_get_report_status` | Check the status of a submitted report |

### Bugcrowd Functions

| Function | Description |
|----------|-------------|
| `bugcrowd_get_programs` | Fetch available programs on Bugcrowd |
| `bugcrowd_get_program_details` | Get detailed information about a specific program |
| `bugcrowd_create_submission` | Submit a vulnerability finding to a program |
| `bugcrowd_get_submission_status` | Check the status of a submitted finding |

## Example Usage

Here's a basic example of how to use these functions within the CAI framework:

```python
from cai.core import CAI
from cai.agents.bug_bounter import bug_bounter_agent

# Initialize CAI
client = CAI()

# Create a message that uses the platform integration
messages = [{
    "role": "user",
    "content": "Find active HackerOne programs that include web applications in scope."
}]

# Run the bug bounty agent
response = client.run(
    agent=bug_bounter_agent,
    messages=messages
)

# Process the response
print(response)
```

## Workflow Example

A typical bug bounty workflow using these integrations might look like:

1. List available programs with scope matching your expertise:

   ```python
   hackerone_get_programs()
   ```

2. Get detailed information about an interesting program:

   ```python
   hackerone_get_program_details("program-handle")
   ```

3. Conduct testing on in-scope targets using CAI's other tools

4. When a vulnerability is found, prepare and submit a report:

   ```python
   hackerone_create_report(
       program_handle="program-handle",
       title="XSS in Search Function",
       vulnerability_type="xss",
       severity="medium",
       summary="Cross-site scripting vulnerability in the search function",
       reproduction_steps="1. Go to /search\n2. Enter payload: <script>alert(1)</script>"
   )
   ```

5. Check the status of your submission:

   ```python
   hackerone_get_report_status("report-id")
   ```

## Best Practices

- Always verify that your target is within the scope of the program
- Follow each program's disclosure policy
- Provide clear, detailed reproduction steps
- Include appropriate impact assessment
- Be professional in all communications
- Follow security best practices for handling API tokens

## Troubleshooting

- **401 Errors**: Check that your API credentials are correctly set in the `.env` file
- **Not Found Errors**: Verify that program handles or report IDs are correct
- **Permission Errors**: Ensure your API token has the necessary permissions
- **Rate Limiting**: Some APIs have rate limits; implement delays between calls if needed

## Advanced Usage

For advanced usage, you can create custom workflows that combine these API functions with other CAI tools:

```python
# Example of combining reconnaissance with HackerOne submission
# First use shodan and other tools to find vulnerabilities
# Then prepare and submit the finding to HackerOne
```

## References

- [HackerOne API Documentation](https://docs.hackerone.com/reference/)
- [Bugcrowd API Documentation](https://docs.bugcrowd.com/reference)
- [CAI Documentation](https://github.com/aliasrobotics/cai)
