# 🤖 LinkedIn Job Application Bot

## 🌟 Overview
This project is an application of the **[usebrowse](https://github.com/browser-use/browser-use)** library, which is the main star of this implementation. It creates an automated LinkedIn job application bot powered by AI agents that helps users find and apply to Software Engineer positions on LinkedIn using the Easy Apply feature, streamlining the job application process.

> 🚧 **Note:** This project is still a work in progress. Features and functionality may change as development continues. Contributions and feedback are welcome! 🚧

## ✨ Features
- 🧠 **Powered by usebrowse**: Built on the powerful usebrowse library for browser automation and AI agent integration
- 🔐 **Manual LinkedIn Authentication**: Securely log in to LinkedIn with manual credential entry
- 🔍 **Automated Job Search**: Searches specifically for Software Engineer positions
- 📝 **Automated Application Submission**: Completes and submits Easy Apply applications
- 📊 **Application Tracking**: Keeps track of applied jobs to avoid duplicates

## 📋 Requirements
- Python 3.11+
- [Playwright](https://playwright.dev/docs/intro) (used by usebrowse) for browser interactions
- Openrouter or any other LLM API provider (like OpenAI) for AI agent capabilities
- LinkedIn account

## 🛠️ Setup

### 1. Install uv (if not already installed)

First, install uv using the standalone installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the repository

```bash
git clone <repository-url>
cd job-app-bot
```
### 3. Install Playwright browsers

```bash
uv pip install pytest-playwright
```
```bash
playwright install
```

### 4. Install dependencies
Then install the project dependencies:

```bash
uv sync
```


### 5. Set up OpenRouter API key 🔑 

This project uses [OpenRouter](https://openrouter.ai/) as the LLM provider, which allows you to use any model from various providers (OpenAI, Anthropic, Google, etc.) through a single API.

**Alternativly you can use any other LLM provider of your choice**
1. Create an account at [https://openrouter.ai/](https://openrouter.ai/)
2. Generate an API key from your dashboard
3. Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_api_key_here
```

OpenRouter gives you flexibility to choose from a wide range of models without being locked into a single provider.

## 🚀 Usage

Run the main script to start the job application process:

```bash
uv run main.py
```

The bot will:
1. Open a browser and navigate to LinkedIn 🌐
2. Prompt you to manually sign in to your LinkedIn account 🔑
3. Search for positions relevant to your cv/resume 🔍
4. Apply to jobs with Easy Apply functionality ✅
5. Skip jobs that require multiple steps or don't have Easy Apply ⏭️
6. Track applied jobs to avoid duplicates 📝

## ⚙️ Configuration

You can customize the bot's behavior by modifying:
- 📄 `main.py`: Change the task instructions or agent configuration
- 🔧 `actions.py`: Modify the specific actions the bot can perform
- ⚙️ `config.py`: Update configuration settings

## 🔒 Security

This bot uses a manual login approach for LinkedIn to ensure your credentials are never stored in code or environment variables. You will need to manually enter your username and password when prompted.

## ⚠️ Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with LinkedIn's terms of service. Automated interactions with websites may violate terms of service.