import os
import time
import logging
import telebot


from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from dotenv import load_dotenv
from Database import Database
import datetime as dt

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
logging.basicConfig(level=logging.INFO, filename="app_logs.log", filemode='w', format="%(asctime)s | %(levelname)s | %(message)s", encoding="UTF-8")
db = Database()
scheduler = BackgroundScheduler()


def kb_choice_time():
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton("Недельный отчет", callback_data="week_report")
    btn2 = InlineKeyboardButton("Месячный отчет", callback_data="month_report")
    markup.add(btn1, btn2)

    return markup


def add_all_reports():
    for user in db.get_users():
        for habit in db.get_habits(user[1]):
            db.add_report(user_id=user[0], habit_id=habit[0], status=False, day=date.today())


def kb_start():
    markup = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton("Начать", callback_data="btn_start")
    markup.add(btn)

    return markup


def kb_menu():
    markup = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton("📝 Отметить привычку", callback_data="btn_hab_habits")
    btn2 = InlineKeyboardButton("⚙️ Отредактировать привычки", callback_data="btn_edit_habits")
    btn3 = InlineKeyboardButton("📊 Отчет", callback_data="btn_report_all")
    markup.add(btn1, btn2, btn3)

    return markup


def kb_navigator_edit(page: int, user_id: int) -> InlineKeyboardMarkup:

    markup = InlineKeyboardMarkup(row_width=1)

    habits = db.get_habits(user_id)
    print(habits)

    max_elem = 2

    kolvo_habits = len(habits)
    total_pages = kolvo_habits // max_elem
    if kolvo_habits % max_elem != 0:
        total_pages += 1

    for habit in habits[(page * max_elem):((page + 1) * max_elem)]:
        btn1 = InlineKeyboardButton(text=habit[2], callback_data=f"habit_edit_{habit[0]}")
        print(habit[0])
        markup.add(btn1)

    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"navigator_edit_back_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"navigator_edit_forward_{page + 1}"))
    if nav_buttons:
        markup.row(*nav_buttons)

    btn3 = InlineKeyboardButton("➕ Добавить привычку", callback_data="add_new_habit")
    markup.add(btn3)

    return markup


def kb_navigator_hab(page: int, user_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)

    habits = db.get_habits(user_id)

    max_elem = 2


    kolvo_habits = len(habits)
    total_pages = kolvo_habits // max_elem
    if kolvo_habits % max_elem != 0:
        total_pages += 1


    for habit in habits[(page * max_elem):((page + 1) * max_elem)]:
        btn1 = InlineKeyboardButton(text=habit[2], callback_data=f"habit_hab_{habit[0]}")
        btn2 = InlineKeyboardButton(text= "✅️" if db.status(habit_id=habit[0])[0][0] == True else "⬜", callback_data=f"note_{habit[0]}")
        print(type(habit))
        print(db.status(habit_id=habit[0])[0][0])
        markup.add(btn1, btn2, row_width=2)


    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"navigator_hab_back_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"navigator_hab_forward_{page + 1}"))
    if nav_buttons:
        markup.row(*nav_buttons)

    return markup


@bot.message_handler(commands=['start'])
def cmd_start(message: Message):
    print(db.user_exists(user_id=message.chat.id))
    if db.user_exists(user_id=message.chat.id) == True:
        cmd_menu(message)
    else:
        db.create_user(user_id=message.chat.id, username=message.from_user.username)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Привет!\nЯ твой трекер привычек.\nБуду помогать тебе становится лучше! 🎯\nНачнем? 👇",
            reply_markup=kb_start()
        )


@bot.message_handler(commands=['menu'])
def cmd_menu(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f"🏠 Главное меню\nВыберите действие",
        reply_markup=kb_menu()
    )

@bot.message_handler(commands=['report_all'])
def cmd_report_all(message: Message):
    bot.send_message(chat_id=message.chat.id, text="Выберите временную метку 👇 ", reply_markup=kb_choice_time())


@bot.message_handler(commands=["hab_habits"])
def cmd_hab_habits(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Ваши привычки:",
        reply_markup=kb_navigator_hab(0, message.chat.id)
    )


@bot.message_handler(commands=["edit_habits"])
def cmd_edit_habits(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Чтобы отредактировать привычку нажмите на нее\nВаши привычки:",
        reply_markup=kb_navigator_edit(0, message.chat.id    )
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def button_start(call: CallbackQuery):
    if call.data == "btn_start":
        cmd_menu(call.message)
    elif call.data == "btn_hab_habits":
        cmd_hab_habits(call.message)
    elif call.data == "btn_edit_habits":
        cmd_edit_habits(call.message)
    elif call.data == "btn_report_all":
        cmd_report_all(call.message)



@bot.callback_query_handler(func=lambda call: call.data.startswith("navigator_hab"))
def button_navigator_hub(call: CallbackQuery):
    print(call.data)
    page = call.data.split("_")[3]
    page = int(page)

    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=kb_navigator_hab(page, call.message.chat.id)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("navigator_edit"))
def button_navigator_edit(call: CallbackQuery):
    print(call.data)
    page = call.data.split("_")[3]
    page = int(page)

    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=kb_navigator_edit(page, call.message.chat.id)
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_new_habit"))
def button_add_new_habit(call: CallbackQuery):
    msg = bot.send_message(call.from_user.id, "✍️ Введите название новой привычки")

    bot.register_next_step_handler(msg, add_new_habit)


def add_new_habit(message: Message):
    habit_name = message.text.strip()
    msg = bot.send_message(message.chat.id,f"✅ Привычка '{habit_name}'\nВведите, сколько раз в неделю её нужно выполнять:")

    bot.register_next_step_handler(msg, add_new_repeats, name=habit_name)


def add_new_repeats(message: Message, name: str):
    if message.text.isdigit() == True and int(message.text) <= 7:
        repeats = message.text.strip()
        db.add_habit(name=name, user_id=message.from_user.id, repeats=repeats)
        new_id = db.get_new_habit_id(user_id=message.from_user.id)
        if new_id is None:
            time.sleep(2)
        new_id = db.add_habit(name=name, user_id=message.from_user.id, repeats=repeats)
        db.add_report(habit_id=new_id, status=False,
                      day=date.today(), user_id=message.from_user.id)
        bot.send_message(message.chat.id, f"Привычка '{name}' сохранена {repeats}/7!")
    else:
        bot.send_message(message.chat.id, f"Привычка '{name}' не добавлена!\nВводите повторения корректно!")
#сделать проерку на len(name)


@bot.callback_query_handler(func=lambda call: call.data.startswith("note_"))
def button_note(call: CallbackQuery):
    db.note_habit(habit_id=int(call.data.split("_")[1]), status=True if db.status(int(call.data.split("_")[1])) == False else False)
    cmd_hab_habits(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("habit_edit_"))
def button_edit_habit(call: CallbackQuery):
    msg = bot.send_message(call.from_user.id, "✍️ Введите название обновленной привычки")

    bot.register_next_step_handler(msg, edit_habit, habit_id=int(call.data.split("_")[2]))


def edit_habit(message: Message, habit_id: int):
    habit_name = message.text.strip()
    msg = bot.send_message(message.chat.id,
                               f"✅ Привычка '{habit_name}'\nВведите, сколько раз в неделю её нужно выполнять:")


    bot.register_next_step_handler(msg, edit_repeats, name=habit_name, habit_id=habit_id)


def edit_repeats(message: Message, name: str, habit_id: int):
    if message.text.isdigit() == True and int(message.text) <= 7:
        repeats = int(message.text.strip())
        db.update_habit(habit_id=habit_id, name=str(name), repeats=repeats)
        bot.send_message(message.chat.id, f"Привычка '{name}' сохранена {repeats}/7!")
    else:
        bot.send_message(message.chat.id, f"Привычка '{name}' не обновлена!\nВводите повторения корректно!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("month_report"))
def button_month_report(call: CallbackQuery):
    cmd_month_report(message=call.message.text, habit_id=int(call.data.split("_")[1]))

@bot.message_handler(commands=["month_report"])
def cmd_month_report(message: Message):
    status_spisok = db.get_habits_status_for_month(message.from_user.id)
    formatted_rows = []
    agreement = {True:"🟩", False:"⬜️"}
    chunk_true = []
    for i in range(0, 30, 6):
        chunk = status_spisok[i:i + 6]
        for i in range(6):
            chunk_true.append(agreement[chunk[i]])
            print(chunk_true)
        row_str = "".join(map(str, chunk_true))
        formatted_rows.append(row_str)
        chunk_true.clear()
    text = "\n".join(formatted_rows)
    if db.get_len_habits_status_true_for_month(message.from_user.id) % 30 >= 15:
        state_message = "Так держать! Дальше - больше!"
    else:
        state_message = "Нужно постараться сильней!"
    print(text)
    bot.send_message(chat_id=message.from_user.id, text=
    f"Ваша успеваемость: 💾\n\n"
    f"{date.today() - dt.timedelta(days=30)} - {date.today()}\n"
    f"{text}\n\n"
    f"Всего выполненных дней: {db.get_len_habits_status_true_for_month(message.from_user.id)}🟩\n"
    f"Всего невыполненных дней: {30 - db.get_len_habits_status_true_for_month(message.from_user.id)}⬜️\n\n"
    f"Ваш процент успеваемости: {db.get_len_habits_status_true_for_month(message.from_user.id) % 30}%\n"
    f"{state_message}")

if "__main__" == __name__:
    scheduler.add_job(func=add_all_reports, trigger='cron', hour=00, minute=00)

    while True:
        try:
            if scheduler.state == 0:
                scheduler.start()

            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Произошла ошибка при работе бота, ошибка: {e}")