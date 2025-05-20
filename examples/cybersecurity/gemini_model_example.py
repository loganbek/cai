"""
Example demonstrating the use of Google Gemini models with CAI.

This script shows how to configure and use Gemini models for cybersecurity tasks.
"""

import os
from dotenv import load_dotenv
from cai.core import CAI
from cai.agents import bug_bounter

# Load environment variables
load_dotenv()

# Check if Gemini API key is available
if not os.getenv("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY environment variable is not set.")
    print("Please set your Gemini API key in the .env file or export it in your terminal.")
    print("You can obtain an API key from: https://aistudio.google.com/app/apikey")
    exit(1)

def run_gemini_example():
    """
    Runs a cybersecurity example using a Gemini model-powered bug bounty agent with the CAI framework.
    
    The function initializes a bug bounty agent configured with the Gemini model, sends a user query about website reconnaissance techniques, and prints the model's response.
    """
    print("Initializing CAI with Gemini model...")
    
    # Create a bug bounty agent with Gemini model
    agent = bug_bounter.create_agent(model="gemini/gemini-2.5-pro-exp-03-25")
    
    # Initialize CAI
    client = CAI()
    
    # Create a message for the agent
    messages = [{
        "role": "user",
        "content": "I want to perform reconnaissance on a website example.com. "
                   "What tools and techniques would you recommend for the initial phase?"
    }]
    
    # Run the agent
    print("Running bug bounty agent with Gemini model...")
    response = client.run(
        agent=agent,
        messages=messages
    )
    
    # Print the response
    print("\nGemini Model Response:")
    print("-" * 80)
    print(response)
    print("-" * 80)

if __name__ == "__main__":
    run_gemini_example()
