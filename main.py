import os
from dotenv import load_dotenv
import sys
import asyncio
import logging
from browser_use import Agent
from actions import controller
from config import model, browser, num_of_applications

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()
logger = logging.getLogger(__name__)


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
        "   a. Click/scroll down through the list of jobs to see if it has a quick apply button. You may have to scroll down on the list and navigate to the next page to see more jobs with quick apply.\n"
        # "   b. Only if the job has a quick apply button, click *quick apply* button and apply to the job. Otherwise, skip this job.\n"
        "   b. For multi-step applications, fill out forms using your CV information and 'Get common application answers' action to fill out questions. However if an input field is already filled, skip it.\n"
        "   c. Uncheck 'Follow company to stay up to date with their page.' before submitting the application. You may have to scroll down on the dialog to find this option and the submit button.\n"
        "   d. Close the confirmation dialog and use 'Save job information' action to save the job details\n"
        # f"5. Repeat this process for at least {num_of_applications} job listings. Only run 'done' action and quit when you have applied to {num_of_applications} jobs successfully\n"
        f"5. Repeat this process indefinitely until the user runs 'done' action and quits the program\n"

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
