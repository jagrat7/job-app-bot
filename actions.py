# Standard library imports
import csv
import logging
import asyncio
from PyPDF2 import PdfReader
from browser_use import ActionResult, Controller
from browser_use.browser.context import BrowserContext
from config import CV, data_dir
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Import utility functions for finding HTML elements
from utils.html_elements import (
    find_easy_apply_button,
    find_next_button,
    find_review_button,
    find_submit_button
)


load_dotenv()
# Configure logging
logger = logging.getLogger(__name__)
# Initialize the controller - this registers actions that the AI agent can perform
controller = Controller()

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
		await page.goto('https://www.linkedin.com/jobs/collections/recommended')
		await page.wait_for_load_state()
		
		msg = '🔍 Successfully navigated to LinkedIn recommended jobs'
		logger.info(msg)
		return ActionResult(extracted_content=msg, include_in_memory=True)
		
	except Exception as e:
		logger.debug(f'Error navigating to LinkedIn jobs: {str(e)}')
		return ActionResult(error=f'Failed to navigate to LinkedIn jobs: {str(e)}')


@controller.registry.action('Apply to LinkedIn job', requires_browser=True)
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
		job_title_elem = await browser.query_selector('h1.t-24.t-bold a')
		if not job_title_elem:
			job_title_elem = await browser.query_selector('h1.t-24')
		company_elem = await browser.query_selector('div.job-details-jobs-unified-top-card__company-name a')
		if not company_elem:
			company_elem = await browser.query_selector('a.company-name')
		
		job_title = await job_title_elem.text_content() if job_title_elem else 'Unknown Job Title'
		company = await company_elem.text_content() if company_elem else 'Unknown Company'
		
		logger.info(f'Attempting to apply to: {job_title} at {company}')
		
		# Check if the job has Easy Apply using the check_quick_apply function
		quick_apply_result = await check_quick_apply(browser)
		
		if quick_apply_result.extracted_content != 'true':
			# Save the job with Failed status
			save_jobs(Job(
				title=job_title,
				company=company.strip() if company else 'Unknown Company',
				link=current_url,
				fit_score=0.5,  # Medium fit score for jobs we couldn't apply to
				status='Failed - No Easy Apply'
			))
			return ActionResult(error='This job does not have Easy Apply option')
		
		# Use the Easy Apply button that was already found
		global _last_found_easy_apply_button  # Declare global variable
		easy_apply_button = _last_found_easy_apply_button
		
		# Click Easy Apply button
		await easy_apply_button.click()
		await browser.wait_for_load_state('networkidle')
		await browser.wait_for_timeout(2000)  # Wait for dialog to fully appear
		
		# Check for next button or submit application button
		next_button = await find_next_button(browser)
		
		# Look for review button
		review_button = await find_review_button(browser)
		
		# Look for submit application button
		submit_button = await find_submit_button(browser)
		
		# If there's a review button, click it first
		if review_button:
			logger.info('Found review application button - clicking it')
			await review_button.click()
			await browser.wait_for_load_state('networkidle')
			await browser.wait_for_timeout(2000)  # Wait for dialog to update
			
			# After review, look for submit button again
			submit_button = await find_submit_button(browser)
		
		# If there's a submit button, click it
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
		
		# If there's a next button but no review or submit button, this is a multi-step application
		elif next_button and not review_button:
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





@controller.registry.action('Check if job has Quick Apply', requires_browser=True)
async def check_quick_apply(browser: BrowserContext):
	"""Check if the currently open job posting has a Quick Apply option.
	
	This action checks if the job that is currently open in the browser
	has LinkedIn's Easy Apply feature available.
	
	Args:
		browser: Browser context for interacting with the webpage
	
	Returns:
		ActionResult: Boolean indicating if Quick Apply is available and the button element
		            in the metadata field if found
	"""
	try:
		# Declare global variable at the beginning of the function
		global _last_found_easy_apply_button
		
		# Look for Easy Apply button using the helper function
		easy_apply_button = await find_easy_apply_button(browser)
		
		if easy_apply_button:
			# Store the button in a global variable to avoid finding it again
			_last_found_easy_apply_button = easy_apply_button
			return ActionResult(extracted_content='true')
		else:
			# Clear the global variable if no button is found
			_last_found_easy_apply_button = None
			return ActionResult(extracted_content='false')
		
	except Exception as e:
		logger.debug(f'Error checking for Quick Apply: {str(e)}')
		return ActionResult(error=f'Failed to check for Quick Apply: {str(e)}')