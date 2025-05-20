# CAI Setup Guide for Windows Bug Bounty Hunters

This guide explains how to set up CAI (Cybersecurity AI) on Windows for bug bounty hunting.

## Prerequisites

- Windows 10 or 11
- Windows Subsystem for Linux (WSL) with a Linux distribution (Ubuntu recommended)
- Python 3.12 or higher
- Basic familiarity with command line operations

## Installation Steps

### 1. Install WSL (Windows Subsystem for Linux)

If you don't have WSL installed, open PowerShell as Administrator and run:

```powershell
wsl --install
```

After installation, restart your computer to complete the setup.

### 2. Setup WSL Environment 

Open your WSL terminal and run:

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git python3-pip python3-venv python3.12-venv

# Create a working directory
mkdir -p ~/cai_workspace && cd ~/cai_workspace
```

### 3. Install CAI Framework

```bash
# Create a virtual environment
python3 -m venv cai_env

# Activate the environment
source cai_env/bin/activate

# Install CAI
pip install cai-framework
```

If you already have the codebase cloned (like in your case):

```bash
# Navigate to the code directory
cd /mnt/c/Users/logan/code/cai

# Install in development mode
pip install -e .
```

### 4. Configure Environment Variables

Create a `.env` file in your project directory:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys
nano .env
```

At minimum, set these variables:

```
OPENAI_API_KEY="your-openai-api-key"
CAI_MODEL="gpt-4o"  # Or your preferred model
PROMPT_TOOLKIT_NO_CPR=1
```

For enhanced bug bounty capabilities, consider adding:

```
SHODAN_API_KEY="your-shodan-api-key"
GOOGLE_SEARCH_API_KEY="your-google-api-key"
GOOGLE_SEARCH_CX="your-google-search-cx"
```

### 5. Install Additional Security Tools

For comprehensive bug bounty hunting, install these tools:

```bash
# Common security tools
sudo apt install -y nmap dirb gobuster wfuzz sqlmap

# Additional tools
sudo apt install -y nikto hydra whois dnsutils
```

## Running CAI for Bug Bounty

### Command Line Interface

```bash
# Start CAI's interactive shell
cai

# Within the shell, select the bug bounty agent
/agent bug_bounter

# Then input your target instructions
```

### Python Script Execution

Create a Python script like `bug_bounty_run.py` (already created in examples/cybersecurity/) and run:

```bash
# Navigate to the examples directory
cd /mnt/c/Users/logan/code/cai/examples/cybersecurity

# Run the script
python bug_bounty_run.py
```

## Troubleshooting

### API Key Issues

If you encounter errors about missing API keys:

1. Check your `.env` file to ensure keys are properly formatted
2. Verify the keys are valid and have sufficient credits
3. Try setting the keys as environment variables directly:

```bash
export OPENAI_API_KEY="your-key-here"
```

### Installation Problems

If you encounter issues with Python packages:

```bash
# Upgrade pip
pip install --upgrade pip

# Install required dependencies
pip install requests litellm openai anthropic
```

### Model Selection Issues

If your preferred model isn't working:

1. Check if you have access to the model in your API account
2. Try a different model by changing the CAI_MODEL environment variable
3. Consider using Ollama for local models if API access is problematic

## Best Practices for Bug Bounty

1. **Always stay within scope** - Only test targets where you have explicit permission
2. **Document findings thoroughly** - Keep detailed notes of vulnerabilities
3. **Follow responsible disclosure** - Report findings according to program guidelines
4. **Start with reconnaissance** - Gather information before attempting exploits
5. **Respect rate limits** - Don't overwhelm target systems with requests

## Additional Resources

- Check out `/examples/cybersecurity/` for more scripts
- Read through the CAI documentation in the README
- Visit the tools directory to understand available capabilities

## Need Help?

- Join the Discord community: https://discord.gg/fnUFcTaQAC
- Check the GitHub repository: https://github.com/aliasrobotics/cai
- Report issues or suggest improvements
