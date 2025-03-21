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
    """Helper function to find the Easy Apply button by looking for buttons with 'Easy Apply' text.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Easy Apply button element or None if not found
    """
    try:
        # Get the current state of the page
        state = await browser.get_state()
        
        # Look for buttons with 'Easy Apply' text
        for element in state.elements:
            if element.tag_name.lower() == 'button' and 'easy apply' in element.text.lower():
                logger.info(f"Found Easy Apply button: {element.text}")
                return element
            
        # Also look for buttons with specific classes that might be Easy Apply buttons
        for element in state.elements:
            if element.tag_name.lower() == 'button' and ('jobs-apply-button' in element.attributes.get('class', '')):
                logger.info(f"Found Easy Apply button by class: {element.attributes.get('class')}")
                return element
        
        logger.info("No Easy Apply button found")
        return None
    except Exception as e:
        logger.error(f"Error finding Easy Apply button: {str(e)}")
        return None


async def find_next_button(browser: BrowserContext):
    """Helper function to find the Next button by looking for buttons with 'Next' text.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Next button element or None if not found
    """
    try:
        # Get the current state of the page
        state = await browser.get_state()
        
        # Look for buttons with 'Next' text or aria-label containing 'next step'
        for element in state.elements:
            if element.tag_name.lower() == 'button':
                # Check button text
                if 'next' in element.text.lower():
                    logger.info(f"Found Next button by text: {element.text}")
                    return element
                
                # Check aria-label attribute
                aria_label = element.attributes.get('aria-label', '').lower()
                if 'continue to next step' in aria_label:
                    logger.info(f"Found Next button by aria-label: {aria_label}")
                    return element
                
                # Check for data attribute
                if 'data-easy-apply-next-button' in element.attributes:
                    logger.info("Found Next button by data attribute")
                    return element
        
        logger.info("No Next button found")
        return None
    except Exception as e:
        logger.error(f"Error finding Next button: {str(e)}")
        return None


async def find_review_button(browser: BrowserContext):
    """Helper function to find the Review button by looking for buttons with 'Review' text.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Review button element or None if not found
    """
    try:
        # Get the current state of the page
        state = await browser.get_state()
        
        # Look for buttons with 'Review' text or relevant attributes
        for element in state.elements:
            if element.tag_name.lower() == 'button':
                # Check button text
                if 'review' in element.text.lower():
                    logger.info(f"Found Review button by text: {element.text}")
                    return element
                
                # Check aria-label attribute
                aria_label = element.attributes.get('aria-label', '').lower()
                if 'review your application' in aria_label:
                    logger.info(f"Found Review button by aria-label: {aria_label}")
                    return element
                
                # Check for data attribute
                if 'data-live-test-easy-apply-review-button' in element.attributes:
                    logger.info("Found Review button by data attribute")
                    return element
        
        logger.info("No Review button found")
        return None
    except Exception as e:
        logger.error(f"Error finding Review button: {str(e)}")
        return None


async def find_submit_button(browser: BrowserContext):
    """Helper function to find the Submit application button by looking for buttons with 'Submit' text.
    
    Args:
        browser: Browser context for interacting with the webpage
    
    Returns:
        The Submit button element or None if not found
    """
    try:
        # Get the current state of the page
        state = await browser.get_state()
        
        # Look for buttons with 'Submit' text or relevant attributes
        for element in state.elements:
            if element.tag_name.lower() == 'button':
                # Check button text
                if 'submit application' in element.text.lower():
                    logger.info(f"Found Submit button by text: {element.text}")
                    return element
                
                # Check aria-label attribute
                aria_label = element.attributes.get('aria-label', '').lower()
                if 'submit application' in aria_label:
                    logger.info(f"Found Submit button by aria-label: {aria_label}")
                    return element
        
        logger.info("No Submit button found")
        return None
    except Exception as e:
        logger.error(f"Error finding Submit button: {str(e)}")
        return None
