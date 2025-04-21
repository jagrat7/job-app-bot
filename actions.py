# Standard library imports
import csv
import logging
import asyncio
import datetime
from PyPDF2 import PdfReader
from browser_use import ActionResult, Controller
from browser_use.browser.context import BrowserContext
from config import CV, data_dir
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()
# Configure logging
logger = logging.getLogger(__name__)
# Initialize the controller - this registers actions that the AI agent can perform
controller = Controller()

# Dictionary of common job application questions and answers
# This can be used by the AI to automatically fill out forms
COMMON_APPLICATION_ANSWERS = {
	# Work Authorization
	"authorized to work": "Yes",
	"require sponsorship": "Yes",
	"visa status": "F-1",
	
	# Job Preferences
	"desired salary": "$120,000 - $150,000",
	"willing to relocate": "Yes",
	"relocation preferences": "Any",
	"preferred work location": "Any",
	"come to office": "Yes",
	"notice period": "2 weeks",
	
}

# Global variable to store the last found Easy Apply button to avoid duplicate searches
_last_found_easy_apply_button = None

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


# Module-level variable to store the CSV file path for this run
csv_file_path = None

def _save_job_to_csv(job: Job, append: bool = True):
	"""Save job information to a CSV file.
	
	Args:
		job: Job object to save
		append: Whether to append to the existing file or create a new one
	
	Returns:
		None
	"""
	global csv_file_path
	if not csv_file_path:
		timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")
		csv_file_path = data_dir / f'jobs_{timestamp}.csv'
	file_path = csv_file_path
	file_exists = file_path.exists()
	
	# Create the data directory if it doesn't exist
	data_dir.mkdir(parents=True, exist_ok=True)
	
	# Define the CSV field names
	field_names = ['title', 'company', 'link', 'fit_score', 'location', 'salary', 'status']
	
	# Open the file in append mode if it exists and append is True, otherwise write mode
	mode = 'a' if file_exists and append else 'w'
	
	with open(file_path, mode, newline='') as f:
		writer = csv.DictWriter(f, fieldnames=field_names)
		
		# Write header if the file is new or we're not appending
		if not file_exists or not append:
			writer.writeheader()
		
		# Write the job data
		writer.writerow({
			'title': job.title,
			'company': job.company,
			'link': job.link,
			'fit_score': job.fit_score,
			'location': job.location or '',
			'salary': job.salary or '',
			'status': job.status or 'Saved'
		})

@controller.action('Save job information')
def save_job_information(title: str, company: str, link: str, status: str, fit_score: float = 1.0):
	"""Save information about a job to the jobs.csv file.
	
	This action saves details about a job to a CSV file for tracking purposes.
	
	Args:
		title: Job title
		company: Company name
		link: URL to the job posting
		status: Status of the application (e.g., 'Applied', 'Failed')
		fit_score: How well the job matches the candidate's profile (0-1)
	
	Returns:
		ActionResult: Success message or error information
	"""
	try:
		# Create and save the job
		job = Job(
			title=title,
			company=company.strip() if company else 'Unknown Company',
			link=link,
			fit_score=fit_score,
			status=status
		)
		
		_save_job_to_csv(job)
		
		return ActionResult(
			extracted_content=f"Successfully saved job information for {title} at {company}"
		)
		
	except Exception as e:
		logger.error(f"Error saving job information: {str(e)}")
		return ActionResult(error=f"Failed to save job information: {str(e)}")


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


@controller.registry.action('Login to LinkedIn', requires_browser=True)
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
		page = await browser.get_current_page()
		await page.goto('https://www.linkedin.com/login')
		await page.wait_for_load_state()
		
		# User needs to manually sign in
		msg = 'Please sign in to LinkedIn manually'
		logger.info(msg)
		
		# Wait for user to manually log in (max 300 seconds = 5 minutes)
		for i in range(60):  # 60 * 5 seconds = 300 seconds max wait time
			await asyncio.sleep(5)  # Sleep for 5 seconds
			page = await browser.get_current_page()
			current_url = page.url
			logger.info(f'Waiting for manual login, current URL: {current_url}')
			
			# Check if user has logged in by examining the URL
			if 'feed' in current_url or 'checkpoint' in current_url or 'dashboard' in current_url or 'home' in current_url:
				success_msg = '🔒 Successfully logged in to LinkedIn'
				logger.info(success_msg)
				return ActionResult(extracted_content=success_msg, include_in_memory=True)
				
			# Every 12 iterations (about 1 minute), remind the user to log in
			if i % 12 == 0 and i > 0:
				logger.info('Still waiting for manual login. Please complete the login process.')
		
		# If we get here, login timed out
		return ActionResult(
			extracted_content="Navigated to LinkedIn login page. Please sign in manually. The login process is taking longer than expected. Please complete the login to continue.",
			include_in_memory=True
		)
		
	except Exception as e:
		logger.error(f'Error during LinkedIn login process: {str(e)}')
		return ActionResult(error=f'Failed to navigate to LinkedIn login page: {str(e)}')


@controller.action('Get common application answers')
def get_common_application_answers():
	"""Get a dictionary of common job application questions and answers.
	
	This action returns a dictionary of common job application questions and answers
	that can be used to automatically fill out forms during the application process.
	
	Returns:
		str: JSON string of common application questions and answers
	"""
	return str(COMMON_APPLICATION_ANSWERS)


@controller.registry.action('Browse LinkedIn jobs', requires_browser=True)
async def search_linkedin_jobs(browser: BrowserContext):
	"""Browse recommended jobs on LinkedIn.
	
	This action navigates to LinkedIn's recommended jobs page to view job listings.
	
	Args:
		browser: Browser context for interacting with the webpage
	
	Returns:
		ActionResult: Success message or error information
	"""
	try:
		# Navigate to LinkedIn recommended jobs page
		page = await browser.get_current_page()
		# await page.goto('https://www.linkedin.com/jobs/collections/recommended')
		await page.goto('https://www.linkedin.com/jobs/collections/easy-apply/')
		await page.wait_for_load_state()
		
		msg = '🔍 Successfully navigated to LinkedIn recommended jobs'
		logger.info(msg)
		return ActionResult(extracted_content=msg, include_in_memory=True)
		
	except Exception as e:
		logger.debug(f'Error navigating to LinkedIn jobs: {str(e)}')
		return ActionResult(error=f'Failed to navigate to LinkedIn jobs: {str(e)}')


