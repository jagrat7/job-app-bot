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
Also you have to install PyPDF2 to read pdf files: pip install PyPDF2
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
	# Alternative task definition (commented out) - for applying to jobs
	# ground_task = (
	# 	'You are a professional job finder. '
	# 	'1. Read my cv with read_cv'
	# 	'2. Read the saved jobs file '
	# 	'3. start applying to the first link of Amazon '
	# 	'You can navigate through pages e.g. by scrolling '
	# 	'Make sure to be on the english version of the page'
	# )
	
	# Define the base task for the AI agent - search for ML internships
	ground_task = (
		'You are a professional job finder. '
		'1. Read my cv with read_cv'
		'find ml internships in and save them to a file'
		'search at company:'
	)
	
	# Create a list of tasks - currently only searching Google
	# Other companies are commented out but can be enabled
	tasks = [
		ground_task + '\n' + 'Google',  # Search Google for ML internships
		# ground_task + '\n' + 'Amazon',
		# ground_task + '\n' + 'Apple',
		# ground_task + '\n' + 'Microsoft',
		# ground_task
		# + '\n'
		# + 'go to https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/Taiwan%2C-Remote/Fulfillment-Analyst---New-College-Graduate-2025_JR1988949/apply/autofillWithResume?workerSubType=0c40f6bd1d8f10adf6dae42e46d44a17&workerSubType=ab40a98049581037a3ada55b087049b7 NVIDIA',
		# ground_task + '\n' + 'Meta',
	]
	
	# Create agents for each task
	agents = []
	for task in tasks:
		# Each agent gets the task, language model, controller, and browser
		agent = Agent(task=task, llm=model, controller=controller, browser=browser )
		agents.append(agent)

	# Run all agents concurrently using asyncio
	# Each agent will execute its task independently
	await asyncio.gather(*[agent.run() for agent in agents])


# Entry point - run the main function when script is executed directly
if __name__ == '__main__':
	asyncio.run(main())  # Start the asyncio event loop with the main function