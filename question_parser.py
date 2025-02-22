from typing import List, Tuple, Optional
from utils import logger, clean_text, format_option
from config import MAX_OPTIONS, MIN_OPTIONS, QUESTION_PATTERNS, OPTION_MARKERS, MESSAGES
import re

class QuestionParser:
    @staticmethod
    def parse_questions(content: str) -> List[Tuple[str, List[str], int]]:
        """
        Parse questions from the content and return them in a structured format
        """
        if not content or not content.strip():
            logger.error("Empty content received")
            return []

        questions = []
        try:
            # Clean and normalize content
            content = clean_text(content)
            logger.info(f"Processing content of length: {len(content)}")

            # Split into blocks based on question patterns
            blocks = QuestionParser._split_into_blocks(content)
            logger.info(f"Found {len(blocks)} potential question blocks")

            # Process each block
            for i, block in enumerate(blocks, 1):
                try:
                    question_data = QuestionParser._parse_question_block(block)
                    if question_data:
                        questions.append(question_data)
                        logger.info(f"Successfully parsed question {i}: {question_data[0][:50]}...")
                    else:
                        logger.warning(f"Failed to parse block {i}: {block[:50]}...")
                except Exception as e:
                    logger.error(f"Error parsing block {i}: {str(e)}")
                    continue

            logger.info(f"Successfully parsed {len(questions)} questions")
            return questions

        except Exception as e:
            logger.error(f"Error in parse_questions: {str(e)}")
            return []

    @staticmethod
    def _split_into_blocks(content: str) -> List[str]:
        """
        Split content into question blocks
        """
        blocks = []
        current_block = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Check if this line starts a new question
            is_question = any(re.match(pattern, line) for pattern in QUESTION_PATTERNS)

            if is_question and current_block:
                # Save current block and start new one
                blocks.append('\n'.join(current_block))
                current_block = []

            current_block.append(line)

        # Add the last block
        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks

    @staticmethod
    def _parse_question_block(block: str) -> Optional[Tuple[str, List[str], int]]:
        """
        Parse a single question block into question, options, and correct answer index
        """
        lines = [line.strip() for line in block.split('\n') if line.strip()]

        if len(lines) < MIN_OPTIONS + 1:
            logger.error(f"Not enough lines in block. Expected at least {MIN_OPTIONS + 1}, got {len(lines)}")
            return None

        # Extract question text
        question = lines[0]
        # Remove any question numbering
        for pattern in QUESTION_PATTERNS:
            if match := re.match(pattern, question):
                question = question[match.end():].strip()
                break

        # Process options
        options = []
        correct_option_index = None

        for line in lines[1:]:
            if len(options) >= MAX_OPTIONS:
                break

            # Check for correct answer marker
            is_correct = '*' in line
            clean_line = line.replace('*', '').strip()

            # Remove option markers
            for marker in OPTION_MARKERS:
                if clean_line.startswith(marker):
                    clean_line = clean_line[len(marker):].strip()
                    break

            # Set correct answer index
            if is_correct and correct_option_index is None:
                correct_option_index = len(options)

            options.append(clean_line)

        # Validate the parsed question
        if len(options) != MAX_OPTIONS:
            logger.error(f"Invalid number of options. Expected {MAX_OPTIONS}, got {len(options)}")
            return None

        if correct_option_index is None:
            logger.error("No correct answer marked with *")
            return None

        return question, options, correct_option_index