# 🤖 LinkedIn Job Application Bot

## 🌟 Overview
This project creates an automated LinkedIn job application bot powered by AI agents that helps users find and apply to  positions based on your CV/resume on LinkedIn using the Easy Apply feature.

> 🚧 **Note:** This project is still a work in progress. Features and functionality may change as development continues. Contributions and feedback are welcome! 🚧

## ✨ Features
- **Powered by usebrowse**: Built on **[usebrowse](https://github.com/browser-use/browser-use)** library for browser automation and AI agent integration
- **Manual LinkedIn Authentication**: Securely log in to LinkedIn with manual credential entry
- **Automated Job Search**: Searches specifically for Software Engineer positions
- **Automated Application Submission**: Completes and submits Easy Apply applications
- **Application Tracking**: Keeps track of applied jobs to avoid duplicates

## 📋 Requirements
- Python 3.11+
- [Playwright](https://playwright.dev/python/docs/intro) (used by usebrowse) for browser interactions
- [OpenRouter](https://openrouter.ai/) or any other LLM API provider (like OpenAI) for AI agent capabilities
- LinkedIn account

## 🛠️ Setup

### 1. Install uv (if not already installed)

[uv](https://github.com/astral-sh/uv) is on of the best things to happen to Python package management - it's the equivalent of npm for JavaScript. 

**Alternatively, you can use any package manager of your choice like conda or Poetry. The dependencies are in the toml file.**

First, install uv using the standalone installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
### 2. Install Playwright browsers

```bash
uv pip install pytest-playwright
```
```bash
playwright install
```

### 3. Clone the repository

```bash
git clone <repository-url>
cd job-app-bot
```

### 4. Install dependencies
Then install the project dependencies:

```bash
uv sync
```
Create a folder called `data` in the root directory of the project.
```bash
mkdir data
```
Add your resume/CV pdf to the `data` folder under the name `resume.pdf`.


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

### 6. Set up environment variables

Set the model name and other environment variables in the `.env` file, use `env.example` as a template.

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
6. Save successful job applications to a CSV file 📝

## ⚙️ Configuration

You can customize the bot's behavior by modifying:
- 📄 `main.py`: Change the task instructions or agent configuration
- 🔧 `actions.py`: Modify the specific actions the bot can perform
- ⚙️ `config.py`: Update configuration settings
