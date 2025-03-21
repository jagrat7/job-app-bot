"""
HTML Element Utility Functions for Browser Automation.

This module provides helper functions for finding common HTML elements
in LinkedIn job application pages.
"""

import logging
from browser_use.browser.context import BrowserContext

# Configure logging
logger = logging.getLogger(__name__)


async def find_easy_apply_button(browser: BrowserContext):
    """Helper function to find the Easy Apply button using multiple selectors.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Easy Apply button element or None if not found
    """
    # Try multiple selectors to find the Easy Apply button
    easy_apply_button = await browser.query_selector('button.jobs-apply-button')
    if not easy_apply_button:
        easy_apply_button = await browser.query_selector('button.artdeco-button--primary:has-text("Easy Apply")')
    if not easy_apply_button:
        easy_apply_button = await browser.query_selector('button[aria-label*="Easy Apply"]')
    
    return easy_apply_button


async def find_next_button(browser: BrowserContext):
    """Helper function to find the Next button using multiple selectors.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Next button element or None if not found
    """
    next_button = await browser.query_selector('button[aria-label="Continue to next step"]')
    if not next_button:
        next_button = await browser.query_selector('button[data-easy-apply-next-button]')
    if not next_button:
        next_button = await browser.query_selector('button.artdeco-button--primary:has-text("Next")')
    if not next_button:
        next_button = await browser.query_selector('button:has-text("Next")')
    
    return next_button


async def find_review_button(browser: BrowserContext):
    """Helper function to find the Review button using multiple selectors.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Review button element or None if not found
    """
    review_button = await browser.query_selector('button[aria-label="Review your application"]')
    if not review_button:
        review_button = await browser.query_selector('button[data-live-test-easy-apply-review-button]')
    if not review_button:
        review_button = await browser.query_selector('button.artdeco-button--primary:has-text("Review")')
    if not review_button:
        review_button = await browser.query_selector('button:has-text("Review")')
    
    return review_button


async def find_submit_button(browser: BrowserContext):
    """Helper function to find the Submit application button using multiple selectors.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Submit button element or None if not found
    """
    submit_button = await browser.query_selector('button[aria-label="Submit application"]')
    if not submit_button:
        submit_button = await browser.query_selector('button.artdeco-button--primary:has-text("Submit application")')
    if not submit_button:
        submit_button = await browser.query_selector('button:has-text("Submit application")')
    
    return submit_button
