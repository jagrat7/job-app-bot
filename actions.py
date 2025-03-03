# Standard library imports
import csv
import logging
import os
from pathlib import Path

# Third-party imports
from PyPDF2 import PdfReader

# Browser automation imports
from browser_use import ActionResult, Controller
from browser_use.browser.context import BrowserContext

# Initialize the controller - this registers actions that the AI agent can perform
controller = Controller()

# Configure logging
logger = logging.getLogger(__name__)

# Path to the resume/CV file
CV = Path.cwd() / 'data' / 'Jagrat Rao-Software Engineer-2025.pdf'
data_dir = Path.cwd() / 'data'
from dotenv import load_dotenv

load_dotenv()
# No longer using LinkedIn credentials from environment variables
# Using manual login instead


# Define the Job model here to avoid circular imports
from typing import Optional
from pydantic import BaseModel

class Job(BaseModel):
    """Represents a job listing with relevant details.
    
    Attributes:
        title: Job title/position
        link: URL to the job posting
        company: Company offering the job
        fit_score: How well the job matches the candidate's profile (0-1)
        location: Optional job location
        salary: Optional salary information
        status: Optional status of the job application (e.g., 'Applied', 'Saved', etc.)
    """
    title: str
    link: str
    company: str
    fit_score: float
    location: Optional[str] = None
    salary: Optional[str] = None
    status: Optional[str] = 'Saved'  # Default status is 'Saved'


# Register actions that the AI agent can perform
@controller.action(
	'Save jobs to file - with a score how well it fits to my profile', param_model=Job
)
def save_jobs(job: Job):
	"""Save a job listing to the CSV file.
	
	This action allows the AI to save job listings it finds to a CSV file
	for later review by the user.
	
	Args:
		job: Job model containing details about the position
	
	Returns:
		str: Confirmation message
	"""
	# Create data directory if it doesn't exist
	data_dir.mkdir(exist_ok=True)
	
	# Create jobs.csv with headers if it doesn't exist
	if not (data_dir / 'jobs.csv').exists():
		with open(data_dir / 'jobs.csv', 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(['Title', 'Company', 'Link', 'Salary', 'Location', 'Fit Score', 'Status'])
	
	# Append the job to the CSV file
	with open(data_dir / 'jobs.csv', 'a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow([job.title, job.company, job.link, job.salary, job.location, job.fit_score, job.status])

	return 'Saved job to file'


@controller.action('Read jobs from file')
def read_jobs():
	"""Read previously saved job listings from the CSV file.
	
	This allows the AI to check what jobs have already been saved
	to avoid duplicates and to reference previously found positions.
	
	Returns:
		str: Contents of the jobs CSV file
	"""
	with open(data_dir / 'jobs.csv', 'r') as f:
		return f.read()


@controller.action('Read my cv for context to fill forms')
def read_cv():
	"""Extract text from the resume/CV file.
	
	This action allows the AI to understand the user's background,
	skills, and experience to better match job listings and
	potentially fill out application forms.
	
	Returns:
		ActionResult: CV text content with memory flag set to True
		             so it stays in the AI's context
	"""
	pdf = PdfReader(CV)
	text = ''
	for page in pdf.pages:
		text += page.extract_text() or ''
	logger.info(f'Read cv with {len(text)} characters')
	return ActionResult(extracted_content=text, include_in_memory=True)


@controller.action(
	'Upload cv to element - call this function to upload if element is not found, try with different index of the same upload element',
	requires_browser=True,
)
async def upload_cv(index: int, browser: BrowserContext):
	"""Upload the resume/CV to a file input element on a webpage.
	
	This action is used during the job application process when the AI
	needs to upload the user's resume to an application form.
	
	Args:
		index: The DOM element index to try uploading to
		browser: Browser context for interacting with the webpage
	
	Returns:
		ActionResult: Success message or error information
	"""
	# Get the absolute path to the CV file
	path = str(CV.absolute())
	
	# Get the DOM element at the specified index
	dom_el = await browser.get_dom_element_by_index(index)

	# Check if the element exists
	if dom_el is None:
		return ActionResult(error=f'No element found at index {index}')

	# Get the file upload element from the DOM element
	file_upload_dom_el = dom_el.get_file_upload_element()

	# Check if it's a file upload element
	if file_upload_dom_el is None:
		logger.info(f'No file upload element found at index {index}')
		return ActionResult(error=f'No file upload element found at index {index}')

	# Locate the element in the browser
	file_upload_el = await browser.get_locate_element(file_upload_dom_el)

	# Check if the element was located
	if file_upload_el is None:
		logger.info(f'No file upload element found at index {index}')
		return ActionResult(error=f'No file upload element found at index {index}')

	# Try to upload the file
	try:
		await file_upload_el.set_input_files(path)
		msg = f'Successfully uploaded file to index {index}'
		logger.info(msg)
		return ActionResult(extracted_content=msg)
	except Exception as e:
		logger.debug(f'Error in set_input_files: {str(e)}')
		return ActionResult(error=f'Failed to upload file to index {index}')


@controller.action('Login to LinkedIn', requires_browser=True)
async def login_to_linkedin(browser: BrowserContext):
	"""Login to LinkedIn by prompting the user to sign in manually.
	
	This action navigates to LinkedIn login page and displays a prompt
	for the user to manually sign in, then waits for successful login.
	
	Args:
		browser: Browser context for interacting with the webpage
	
	Returns:
		ActionResult: Success message or error information
	"""
	try:
		# Navigate to LinkedIn login page
		logger.info('Navigating to LinkedIn login page')
		await browser.goto('https://www.linkedin.com/login')
		await browser.wait_for_load_state('networkidle')
		await browser.wait_for_timeout(3000)  # Wait for page to fully load
		
		# Display a message to the user to sign in manually
		await browser.evaluate(
			'''
			const div = document.createElement('div');
			div.style.position = 'fixed';
			div.style.top = '0';
			div.style.left = '0';
			div.style.width = '100%';
			div.style.padding = '20px';
			div.style.backgroundColor = '#0077b5';
			div.style.color = 'white';
			div.style.zIndex = '9999';
			div.style.textAlign = 'center';
			div.style.fontSize = '16px';
			div.innerHTML = '<b>PLEASE SIGN IN TO LINKEDIN</b><br>Enter your email and password manually, then click Sign In';
			document.body.appendChild(div);
			'''
		)
		
		logger.info('Waiting for user to sign in manually')
		
		# Wait for user to manually log in (max 120 seconds)
		for i in range(24):  # 24 * 5 seconds = 120 seconds max wait time
			await browser.wait_for_timeout(5000)
			current_url = await browser.current_url()
			logger.info(f'Waiting for manual login, current URL: {current_url}')
			
			if 'feed' in current_url or 'checkpoint' in current_url or 'dashboard' in current_url or 'home' in current_url:
				logger.info('Manual login successful')
				return ActionResult(extracted_content='Successfully logged in to LinkedIn')
		
		# If we get here, login timed out
		return ActionResult(error='Manual login timed out. Please try again and sign in within 2 minutes.')
		
	except Exception as e:
		logger.debug(f'Error during LinkedIn login process: {str(e)}')
		return ActionResult(error=f'Failed to complete LinkedIn login: {str(e)}')


@controller.action('Search LinkedIn jobs', requires_browser=True)
async def search_linkedin_jobs(query: str, browser: BrowserContext):
	"""Search for jobs on LinkedIn based on the given query.
	
	This action navigates to LinkedIn jobs page and performs a search
	using the provided query string.
	
	Args:
		query: Job search query (e.g., "Software Engineer")
		browser: Browser context for interacting with the webpage
	
	Returns:
		ActionResult: Success message or error information
	"""
	try:
		# Navigate to LinkedIn jobs page
		await browser.goto('https://www.linkedin.com/jobs/')
		await browser.wait_for_load_state('networkidle')
		
		# Input search query
		search_input = await browser.query_selector('input[aria-label="Search by title, skill, or company"]')
		if not search_input:
			search_input = await browser.query_selector('input[placeholder*="Search job titles"]')
		
		if search_input:
			await search_input.fill(query)
			await search_input.press('Enter')
			await browser.wait_for_load_state('networkidle')
			return ActionResult(extracted_content=f'Successfully searched for "{query}" jobs on LinkedIn')
		else:
			return ActionResult(error='Could not find job search input field')
		
	except Exception as e:
		logger.debug(f'Error searching LinkedIn jobs: {str(e)}')
		return ActionResult(error=f'Failed to search LinkedIn jobs: {str(e)}')


@controller.action('Apply to LinkedIn job', requires_browser=True)
async def apply_to_linkedin_job(browser: BrowserContext):
	"""Apply to the currently open LinkedIn job posting using Easy Apply.
	
	This action attempts to apply to the job that is currently open
	in the browser using LinkedIn's Easy Apply feature.
	
	Args:
		browser: Browser context for interacting with the webpage
	
	Returns:
		ActionResult: Success message with job details or error information
	"""
	try:
		# Check if we're on a job page
		current_url = await browser.current_url()
		if 'jobs/view' not in current_url:
			return ActionResult(error='Not on a LinkedIn job details page')
		
		# Get job title and company
		job_title_elem = await browser.query_selector('h1.job-title')
		company_elem = await browser.query_selector('a.company-name')
		
		job_title = await job_title_elem.text_content() if job_title_elem else 'Unknown Job Title'
		company = await company_elem.text_content() if company_elem else 'Unknown Company'
		
		logger.info(f'Attempting to apply to: {job_title} at {company}')
		
		# Look for Easy Apply button
		easy_apply_button = await browser.query_selector('button[data-control-name="easy_apply_btn"]')
		if not easy_apply_button:
			easy_apply_button = await browser.query_selector('button:has-text("Easy Apply")')
		
		if not easy_apply_button:
			# Save the job with Failed status
			save_jobs(Job(
				title=job_title,
				company=company.strip() if company else 'Unknown Company',
				link=current_url,
				fit_score=0.5,  # Medium fit score for jobs we couldn't apply to
				status='Failed - No Easy Apply'
			))
			return ActionResult(error='This job does not have Easy Apply option')
		
		# Click Easy Apply button
		await easy_apply_button.click()
		await browser.wait_for_load_state('networkidle')
		await browser.wait_for_timeout(2000)  # Wait for dialog to fully appear
		
		# Check for next button or submit application button
		next_button = await browser.query_selector('button:has-text("Next")')
		submit_button = await browser.query_selector('button:has-text("Submit application")')
		
		# If there's a submit button right away, click it
		if submit_button:
			logger.info('Found submit application button - clicking it')
			await submit_button.click()
			await browser.wait_for_load_state('networkidle')
			await browser.wait_for_timeout(2000)  # Wait for confirmation
			
			# Check for success indicators
			success_element = await browser.query_selector('h2:has-text("Application submitted")')
			if not success_element:
				success_element = await browser.query_selector('div:has-text("Your application was sent")')
			
			if success_element:
				# Save the successfully applied job
				save_jobs(Job(
					title=job_title,
					company=company.strip() if company else 'Unknown Company',
					link=current_url,
					fit_score=1.0,  # Assuming a good fit since we're applying
					status='Applied'
				))
				return ActionResult(extracted_content=f'Successfully applied to {job_title} at {company.strip() if company else "Unknown Company"}')
			else:
				# Save as failed application
				save_jobs(Job(
					title=job_title,
					company=company.strip() if company else 'Unknown Company',
					link=current_url,
					fit_score=0.7,  # Higher fit score for jobs we attempted to apply to
					status='Failed - Submission Error'
				))
				return ActionResult(error='Application submission may have failed - no confirmation received')
		
		# If there's a next button, this is a multi-step application
		elif next_button:
			# Save as failed due to multi-step
			save_jobs(Job(
				title=job_title,
				company=company.strip() if company else 'Unknown Company',
				link=current_url,
				fit_score=0.8,  # High fit score for jobs that look promising but need multi-step
				status='Failed - Multi-step Application'
			))
			return ActionResult(error='This job requires a multi-step application which is not supported yet')
		
		else:
			# Save as failed due to unknown issue
			save_jobs(Job(
				title=job_title,
				company=company.strip() if company else 'Unknown Company',
				link=current_url,
				fit_score=0.6,  # Medium fit score
				status='Failed - No Submit Button'
			))
			return ActionResult(error='Could not find next or submit buttons in the application')
		
	except Exception as e:
		logger.debug(f'Error applying to LinkedIn job: {str(e)}')
		
		# Get job details even in case of exception
		try:
			current_url = await browser.current_url()
			# Save as failed due to exception
			save_jobs(Job(
				title=job_title if 'job_title' in locals() else 'Unknown Job',
				company=company.strip() if 'company' in locals() and company else 'Unknown Company',
				link=current_url,
				fit_score=0.4,  # Lower fit score for jobs that caused errors
				status=f'Failed - Error: {str(e)[:50]}'
			))
		except:
			pass  # If we can't even save the job, just continue
		
		return ActionResult(error=f'Failed to apply to LinkedIn job: {str(e)}')


@controller.action('Check if job has Quick Apply', requires_browser=True)
async def check_quick_apply(browser: BrowserContext):
	"""Check if the currently open job posting has a Quick Apply option.
	
	This action checks if the job that is currently open in the browser
	has LinkedIn's Easy Apply feature available.
	
	Args:
		browser: Browser context for interacting with the webpage
	
	Returns:
		ActionResult: Boolean indicating if Quick Apply is available
	"""
	try:
		# Look for Easy Apply button
		easy_apply_button = await browser.query_selector('button[data-control-name="easy_apply_btn"]')
		if not easy_apply_button:
			easy_apply_button = await browser.query_selector('button:has-text("Easy Apply")')
		
		if easy_apply_button:
			return ActionResult(extracted_content='true')
		else:
			return ActionResult(extracted_content='false')
		
	except Exception as e:
		logger.debug(f'Error checking for Quick Apply: {str(e)}')
		return ActionResult(error=f'Failed to check for Quick Apply: {str(e)}')