import telebot
import re

TOKEN = "7316126967:AAFY-bRZoKdu7YEFzRTuTzpHDJnyoQ_tuOg"
bot = telebot.TeleBot(TOKEN)


def parse_quiz(text):
    questions = []
    current_question = None

    for line in text.strip().split("\n"):
        line = line.strip()

        # يتحقق إذا كان السطر يحتوي على رقم في البداية (لتمييز الأسئلة)
        match = re.match(r"^(\d+)[).-]?\s*(.+)", line)
        if match:
            if current_question:
                questions.append(current_question)

            current_question = {
                "question": match.group(2),
                "options": [],
                "correct_index": None
            }
        elif current_question and line:
            # التحقق من وجود الإجابة الصحيحة بناءً على علامة *
            correct = "*" in line
            clean_option = line.replace("*", "").strip()
            current_question["options"].append(clean_option)

            if correct:
                current_question["correct_index"] = len(
                    current_question["options"]) - 1

    if current_question:
        questions.append(current_question)

    return questions


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    quiz_questions = parse_quiz(message.text)

    for q in quiz_questions:
        if len(q["options"]) == 4 and q["correct_index"] is not None:
            bot.send_poll(chat_id=message.chat.id,
                          question=q["question"],
                          options=q["options"],
                          type="quiz",
                          correct_option_id=q["correct_index"])


bot.polling()
