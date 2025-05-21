# API Keys and Setup Guide for CAI

This document provides information on how to obtain and configure API keys for all services supported by the CAI framework.

## LLM Model Providers

### OpenAI

1. Create or log into your account at [OpenAI Platform](https://platform.openai.com)
2. Navigate to [API Keys](https://platform.openai.com/api-keys)
3. Click on "Create new secret key"
4. Copy the generated key and add it to your `.env` file:
   ```
   OPENAI_API_KEY="your_api_key_here"
   ```

### Anthropic (Claude)

1. Create or log into your account at [Anthropic Console](https://console.anthropic.com)
2. Navigate to [API Keys](https://console.anthropic.com/settings/keys)
3. Create a new API key
4. Copy the key and add it to your `.env` file:
   ```
   ANTHROPIC_API_KEY="your_api_key_here"
   ```

### Google Gemini

1. Create or log into your account at [Google AI Studio](https://aistudio.google.com)
2. Navigate to [API Keys](https://aistudio.google.com/app/apikey)
3. Generate a new API key
4. Copy the key and add it to your `.env` file:
   ```
   GEMINI_API_KEY="your_api_key_here"
   ```

### DeepSeek

1. Create or log into your account at [DeepSeek Platform](https://platform.deepseek.com)
2. Navigate to [API Keys](https://platform.deepseek.com/api-keys)
3. Generate a new API key
4. Copy the key and add it to your `.env` file:
   ```
   DEEPSEEK_API_KEY="your_api_key_here"
   ```

### Ollama (Local Models)

Ollama doesn't require an API key, but you need to install and run the Ollama service:

1. Download and install Ollama from [ollama.com](https://ollama.com)
2. Start the Ollama service
3. Pull models using the Ollama CLI (e.g., `ollama pull llama3`)
4. In your `.env` file, you can specify a custom Ollama endpoint if needed:
   ```
   OLLAMA="http://localhost:11434/v1"
   ```

## Bug Bounty Platforms

### HackerOne

1. Create or log into your HackerOne account
2. Go to your [API token settings](https://hackerone.com/settings/api_token)
3. Generate a new API token with appropriate permissions
4. Add your username and API token to your `.env` file:
   ```
   HACKERONE_API_TOKEN="your_h1_api_token"
   HACKERONE_USERNAME="your_h1_username"
   ```

### Bugcrowd

1. Create or log into your Bugcrowd account
2. Request API access from Bugcrowd (via the [documentation portal](https://docs.bugcrowd.com/api/getting-started))
3. Once approved, generate an API token from your account settings
4. Add the token to your `.env` file:
   ```
   BUGCROWD_API_TOKEN="your_bugcrowd_api_token"
   ```

## Other API Services

### Shodan

1. Create or log into your account at [Shodan](https://account.shodan.io)
2. Your API key is displayed on the account overview page
3. Add the key to your `.env` file:
   ```
   SHODAN_API_KEY="your_shodan_api_key"
   ```

### Google Custom Search

1. Create or log into your Google Cloud account
2. Create a new project or select an existing one
3. Enable the [Custom Search API](https://console.cloud.google.com/apis/library/customsearch.googleapis.com)
4. Create API credentials at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
5. Create a Custom Search Engine at [Programmable Search Engine](https://programmablesearchengine.google.com/create/new)
6. Get your Search Engine ID (cx)
7. Add both to your `.env` file:
   ```
   GOOGLE_SEARCH_API_KEY="your_google_api_key"
   GOOGLE_SEARCH_CX="your_search_engine_id"
   ```

## Using Environment Variables

Once you've added your API keys to the `.env` file, CAI will automatically load them when you run the framework. You can also set them as environment variables in your terminal session:

```bash
export OPENAI_API_KEY="your_api_key_here"
export ANTHROPIC_API_KEY="your_api_key_here"
```

For more information on specific integrations, refer to the dedicated documentation files in the `docs/` directory:

- [Google Gemini Models](GEMINI_MODELS.md)
- [Bug Bounty Platforms](BUG_BOUNTY_PLATFORMS.md)
