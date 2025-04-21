import os
from dotenv import load_dotenv
load_dotenv()
from pydantic import SecretStr  # For data validation and secure API key handling
from langchain_openai import ChatOpenAI  # For creating the LLM agent
from browser_use.browser.browser import Browser, BrowserConfig
from pathlib import Path
from langchain_core.caches import InMemoryCache  # Import for caching

# Initialize the language model using OpenRouter as a proxy to OpenAI
# Setup in-memory cache for prompt caching
cache = InMemoryCache()

# Initialize the language model
model = ChatOpenAI(
    # model='gpt-4.1-2025-04-14',
    model='anthropic/claude-3.7-sonnet',
    base_url = "https://openrouter.ai/api/v1",  # OpenRouter API endpoint
    default_headers = {
        "HTTP-Referer": "https://www.usemynt.com/",
        "X-Title": "Mynt"
    },
    api_key=SecretStr(os.getenv('OPENROUTER_API_KEY', '')),  # API key from environment variables
    # api_key=SecretStr(os.getenv('OPENAI_API_KEY', '')),  # API key from environment variables
    cache=cache  # Use our custom cache implementation
)

browser = Browser(
	config=BrowserConfig(
		disable_security=True,  # Disable security features that might block automation
	)
)
# Number of applications to be made
num_of_applications = 20

# Path to the resume/CV file
CV = Path.cwd() / 'data' / 'resume.pdf'

# Path to the data directory
data_dir = Path.cwd() / 'data'

