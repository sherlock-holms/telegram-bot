import re

# Bot token validation
TOKEN = "7316126967:AAFY-bRZoKdu7YEFzRTuTzpHDJnyoQ_tuOg"

# Validate token format
if not re.match(r'^\d+:[\w-]+$', TOKEN):
    raise ValueError("Invalid bot token format. Please check your token.")

# Configuration settings for question parsing
MAX_OPTIONS = 4
MIN_OPTIONS = 4

# Question patterns for improved recognition
QUESTION_PATTERNS = [
    r'^\d+[\.\)]\s*',  # Arabic/English numbers with . or )
    r'^[١٢٣٤٥٦٧٨٩٠]+[\.\)]\s*',  # Arabic numerals
    r'^[Qq]uestion\s*\d+[\:\.\)]\s*',  # "Question n" format
    r'^سؤال\s*\d+[\:\.\)]\s*',  # Arabic "Question n" format
    r'^س\s*\d+[\:\.\)]\s*',  # Arabic "Q n" format
    r'^[\(\[\{]?\d+[\)\]\}]?\s*',  # Numbers in brackets/parentheses
    r'^\d+[\-\:\)]\s*',  # Numbers with different separators
    r'^.*\?$'  # Any line ending with question mark
]

# Option markers
OPTION_MARKERS = [
    'A)', 'B)', 'C)', 'D)',
    'أ)', 'ب)', 'ج)', 'د)',
    '1)', '2)', '3)', '4)',
    '١)', '٢)', '٣)', '٤)',
    'a)', 'b)', 'c)', 'd)',
    'A-', 'B-', 'C-', 'D-',
    'A.', 'B.', 'C.', 'D.'
]

# Message templates in Arabic
MESSAGES = {
    'start': 'مرحباً! أرسل ملف TXT يحتوي على الأسئلة أو أرسل نص الأسئلة مباشرة.\n\nشكل النص يجب أن يكون:\n1. السؤال الأول\nإجابة خاطئة\n*الإجابة الصحيحة\nإجابة خاطئة\nإجابة خاطئة',
    'file_error': 'عذراً، حدث خطأ في معالجة الملف. يرجى التأكد من أن الملف بتنسيق TXT وبترميز UTF-8.',
    'invalid_format': """عذراً، تنسيق النص غير صحيح. يجب أن يكون شكل النص كالتالي:

1. السؤال الأول
إجابة خاطئة
*الإجابة الصحيحة
إجابة خاطئة
إجابة خاطئة

2. السؤال الثاني
إجابة خاطئة
إجابة خاطئة
الإجابة الصحيحة*
إجابة خاطئة

ملاحظات مهمة:
١. يمكنك وضع علامة * في أي مكان من الإجابة الصحيحة
٢. كل سؤال يجب أن يحتوي على ٤ إجابات بالضبط
٣. يجب أن تكون هناك إجابة صحيحة واحدة فقط لكل سؤال""",
    'processing': 'جاري معالجة الأسئلة...',
    'no_questions': 'لم يتم العثور على أسئلة صالحة في النص.',
    'processing_error': 'عذراً، حدث خطأ في معالجة النص. يرجى التأكد من صحة التنسيق والمحاولة مرة أخرى.'
}