"""
Find and apply to jobs.

This script automates the process of finding and applying to machine learning internships
by using an AI agent to browse job sites, search for relevant positions, and save them.

The workflow:
1. Initialize environment and browser
2. Define actions the AI agent can perform (read CV, save jobs, etc.)
3. Create an AI agent with specific tasks
4. Agent browses job sites and saves relevant positions

@dev You need to add OPENROUTER_API_KEY to your environment variables.
"""

# Standard library imports
import os
from dotenv import load_dotenv

load_dotenv()
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import logging

# Browser automation imports
from browser_use import Agent
from actions import controller
from config import model, browser


# Configure logging
logger = logging.getLogger(__name__)


# Initialize the browser with security disabled for automation


async def main():
    """Main entry point for the job search automation.

    This function:
    1. Defines the task for the AI agent
    2. Creates the language model
    3. Creates and runs the agent(s)
    """


    # Create a task specifically for LinkedIn job search and application
    linkedin_task = (
        "You are a professional job finder and applicant. Follow these steps precisely:\n"
        "1. Use 'Login to LinkedIn' action to start the manual login process\n"
        "   - CRITICAL: DO NOT INTERACT with the login form at all! The user will manually enter credentials\n"
        "   - WAIT until the user completes the login process before proceeding to any other actions\n"
        "   - The login process may take up to 5 minutes - be patient and do not proceed until login is confirmed\n"
        "2. Use 'Read my cv for context to fill forms' action to understand my background and skills\n"
        "3. Use 'Browse LinkedIn jobs' action to view recommended job listings\n"
        "4. For each job listing:\n"
        "   a. Click on the job to view details\n"
        "   b. Use 'Apply to LinkedIn job' action to submit an application\n"
        "   c. The application will automatically handle both simple and multi-step applications\n"
        "   d. For multi-step applications, the system will automatically fill out forms using your CV information\n"
        "   e. Close the confirmation dialog\n"
        "5. After applying, the job will be automatically saved with 'Applied' or 'Failed' status\n"
        "6. Continue this process for at least 3 job listings. Only run 'done' when you have applied to 3 jobs successfully\n"
    )

    tasks = [
        linkedin_task,  # LinkedIn job search and application
    ]

    # Create agents for each task
    agents = []
    for task in tasks:
        # Each agent gets the task, language model, controller, and browser
        agent = Agent(task=task, llm=model, controller=controller, browser=browser)
        agents.append(agent)

    # Run all agents concurrently using asyncio
    # Each agent will execute its task independently
    await asyncio.gather(*[agent.run() for agent in agents])


# Entry point - run the main function when script is executed directly
if __name__ == "__main__":
    asyncio.run(main())  # Start the asyncio event loop with the main function
