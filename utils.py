import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_valid_utf8(text: str) -> bool:
    """
    Verify if the text is valid UTF-8
    """
    try:
        text.encode('utf-8').decode('utf-8')
        return True
    except UnicodeError:
        return False

def validate_file_content(content: str) -> bool:
    """
    Validate if file content is not empty and is valid UTF-8
    """
    if not content or not content.strip():
        return False
    return is_valid_utf8(content)

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing line endings
    """
    # Remove BOM if present
    text = text.replace('\ufeff', '')
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Remove extra whitespace while preserving empty lines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_line = line.strip()
        cleaned_lines.append(cleaned_line)
    return '\n'.join(cleaned_lines)

def format_option(option: str) -> str:
    """
    Format quiz option by removing markers and extra whitespace
    """
    # Remove asterisk from anywhere in the option
    option = option.replace('*', '')
    return option.strip()