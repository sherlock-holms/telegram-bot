import telebot
import logging
import sys
import os
import socket
import time
from user_stats import UserStats
from question_parser import QuestionParser

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_single_instance():
    """Ensure only one instance of the bot is running"""
    lock_port = 12345  # Arbitrary port number for lock checking
    if is_port_in_use(lock_port):
        logger.error("Another instance of the bot is already running")
        sys.exit(1)

    # Create a socket to hold the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', lock_port))
    sock.listen(1)
    return sock

# Bot Configuration
TOKEN = "7316126967:AAFY-bRZoKdu7YEFzRTuTzpHDJnyoQ_tuOg"  # Your bot token

def main():
    """Main bot function"""
    try:
        # Check for other instances
        lock_socket = check_single_instance()

        # Initialize bot and stats
        logger.info("Initializing bot...")
        bot = telebot.TeleBot(TOKEN)
        stats = UserStats()
        parser = QuestionParser()

        # Test bot token
        bot_info = bot.get_me()
        logger.info(f"Bot connected successfully. Bot username: @{bot_info.username}")

        @bot.message_handler(commands=['start'])
        def handle_start(message):
            """Handle /start command"""
            try:
                welcome_message = """مرحباً! أرسل ملف TXT يحتوي على الأسئلة أو أرسل نص الأسئلة مباشرة.

شكل النص يجب أن يكون:
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

ملاحظات:
- يمكن وضع علامة * قبل أو بعد أو في وسط الإجابة الصحيحة
- يمكن ترقيم الأسئلة بأي طريقة (1. أو 1) أو السؤال الأول)
- يمكن إضافة مسافات بين السؤال والإجابات"""
                stats.record_user_activity(message.from_user.id, message.from_user.username)
                bot.reply_to(message, welcome_message)
                logger.info(f"Start command handled for user {message.from_user.id}")
            except Exception as e:
                logger.error(f"Error handling start command: {e}")
                bot.reply_to(message, "عذراً، حدث خطأ ما. الرجاء المحاولة مرة أخرى.")

        @bot.message_handler(commands=['stats'])
        def handle_stats(message):
            """Handle /stats command"""
            try:
                stats_message = stats.get_stats_message()
                bot.reply_to(message, stats_message)
                logger.info(f"Stats requested by user {message.from_user.id}")
            except Exception as e:
                logger.error(f"Error handling stats command: {e}")
                bot.reply_to(message, "عذراً، حدث خطأ في عرض الإحصائيات. الرجاء المحاولة مرة أخرى.")

        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            """Handle quiz messages with improved error handling"""
            try:
                logger.info(f"Received message from user {message.from_user.id}: {message.text[:50]}...")
                stats.record_user_activity(message.from_user.id, message.from_user.username)

                # Parse quiz using QuestionParser
                quiz_questions = parser.parse_questions(message.text)

                if not quiz_questions:
                    error_msg = """عذراً، تنسيق النص غير صحيح. يجب أن يكون شكل النص كالتالي:

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
٣. يجب أن تكون هناك إجابة صحيحة واحدة فقط لكل سؤال"""
                    bot.reply_to(message, error_msg)
                    return

                # Record successful quiz creation
                stats.record_quiz_creation(message.from_user.id)

                for question, options, correct_index in quiz_questions:
                    try:
                        bot.send_poll(
                            chat_id=message.chat.id,
                            question=question,
                            options=options,
                            type="quiz",
                            correct_option_id=correct_index,
                            is_anonymous=True
                        )
                        logger.info(f"Quiz sent successfully for user {message.from_user.id}")
                    except Exception as e:
                        logger.error(f"Error sending poll: {str(e)}")
                        bot.reply_to(message, "عذراً، حدث خطأ في إرسال السؤال. الرجاء المحاولة مرة أخرى.")

            except Exception as e:
                logger.error(f"Error handling message: {str(e)}", exc_info=True)
                bot.reply_to(message, "عذراً، حدث خطأ في معالجة النص. يرجى التأكد من صحة التنسيق والمحاولة مرة أخرى.")

        # Start bot with improved error handling
        logger.info("Starting bot polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if 'lock_socket' in locals():
            lock_socket.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
