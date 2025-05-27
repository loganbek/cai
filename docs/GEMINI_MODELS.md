# Google Gemini API Integration for CAI

This document provides information on how to use Google Gemini models with the CAI framework.

## Overview

The CAI framework supports Google's Gemini models through the integration with LiteLLM. Gemini models are optimized for multimodal tasks and reasoning capabilities.

## Available Gemini Models

The following Gemini models are supported in CAI:

| Model | Description | Use Case |
|-------|-------------|----------|
| `gemini/gemini-2.5-pro-exp-03-25` | Advanced model with enhanced reasoning capabilities | General-purpose, comparable to Claude 3.7 |

## Configuration

To use Gemini models with CAI, you need to:

1. **Get a Gemini API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to generate an API key
   - For more detailed instructions, see our [API Keys Guide](API_KEYS.md#google-gemini)
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to obtain your API key
   - Create an account if you don't have one already
   - Navigate to the API keys section and generate a new API key

2. **Add API Key to Environment**:
   - Add your API key to the `.env` file in your project:
     ```
     GEMINI_API_KEY="your_api_key_here"
     ```
   - Alternatively, export it in your terminal session:
     ```bash
     export GEMINI_API_KEY="your_api_key_here"
     ```

## Using Gemini Models

### Through the CLI

You can select a Gemini model in the CLI using:

```
CAI> /model gemini/gemini-2.5-pro-exp-03-25
```

### Programmatically

```python
from cai.core import CAI
from cai.agents import bug_bounter

# Create agent with Gemini model
agent = bug_bounter.create_agent(model="gemini/gemini-2.5-pro-exp-03-25")

# Initialize CAI
cai = CAI()

# Run the agent with a multi-turn conversation
messages = [
    {"role": "user", "content": "I need to perform a security assessment on a web application."},
    {"role": "assistant", "content": "I'll help you with that. What's the target web application?"},
    {"role": "user", "content": "The target is a demo e-commerce site at example.com. Focus on finding potential vulnerabilities."}
]

# Run the agent
response = cai.run(
    agent=agent,
    messages=messages
)

print(response)
```

## Special Considerations

- Gemini models have specific parameter requirements. The CAI framework automatically handles these differences (like removing unsupported parameters).
- Function calling works differently with Gemini compared to OpenAI models. The CAI framework handles the conversion process.
- If you encounter authentication errors, double-check that your `GEMINI_API_KEY` is set correctly.

## References

- [Google AI Studio Documentation](https://ai.google.dev/docs)
- [CAI Documentation](https://github.com/aliasrobotics/cai)
- [LiteLLM Documentation](https://docs.litellm.ai/docs/)
