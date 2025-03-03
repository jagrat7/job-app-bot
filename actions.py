# Standard library imports
import csv
import logging
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
    """
    title: str
    link: str
    company: str
    fit_score: float
    location: Optional[str] = None
    salary: Optional[str] = None


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
	with open('./data/jobs.csv', 'a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow([job.title, job.company, job.link, job.salary, job.location])

	return 'Saved job to file'


@controller.action('Read jobs from file')
def read_jobs():
	"""Read previously saved job listings from the CSV file.
	
	This allows the AI to check what jobs have already been saved
	to avoid duplicates and to reference previously found positions.
	
	Returns:
		str: Contents of the jobs CSV file
	"""
	with open('./data/jobs.csv', 'r') as f:
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