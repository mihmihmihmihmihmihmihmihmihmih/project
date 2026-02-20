from asyncio import run
from logging import basicConfig, INFO
from sys import stdout
from aiogram import Bot, Dispatcher, types
from aiogram.methods import DeleteWebhook
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardBuilder
from psycopg2 import connect

TOKEN = "7837690924:AAHcZGx02aHnofa_Nq_TfMeHGmsin5DSK_c"

dp = Dispatcher()

conn = connect(dbname="pridumal", user="mihmih", password="mihmihmihmihmih", host="127.0.0.1", port="5432")
conn.autocommit = True
cur = conn.cursor()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


@dp.message(Command("start"))
async def start_quiz(message: Message):
    cur.execute(f"select tg_user_id from user_n where tg_user_id = {message.from_user.id}")
    rows = cur.fetchall()
    if rows:
        await bot.send_message(chat_id=message.from_user.id, text='Вы можете пройти тест ещё раз.')
        cur.execute(f"delete from user_n where tg_user_id = {message.from_user.id}; delete from user_a where tg_user_id = {message.from_user.id}; delete from user_cq where tg_user_id = {message.from_user.id};")
        # return 0
    cur.execute(f"insert into user_n (tg_user_id, username) values ({message.from_user.id}, '@{message.from_user.username}')")
    cur.execute(f"insert into user_a (tg_user_id, answers) values ({message.from_user.id}, '0')")
    cur.execute(f"insert into user_cq (tg_user_id, curr_q) values ({message.from_user.id}, 0)")
    await question(chat_id=message.from_user.id)


async def question(chat_id):
    cur.execute(f"select curr_q from user_cq where tg_user_id = {chat_id}")
    rows = cur.fetchall()[0]
    if rows[0] == 13:
        await finish_quiz(chat_id=chat_id)
        return 0

    cur.execute(f"select answers from user_a where tg_user_id = {chat_id}")
    rows0 = cur.fetchall()[0]

    if rows[0] == 0:
        cur.execute(f"update user_cq set curr_q = {1} where tg_user_id = {chat_id}")
        cur.execute(f"select ans_n from questions where question_id = {1}")
        rows0 = cur.fetchall()[0]
        cur.execute(f"select question, answer_1, answer_2, answer_3, answer_4 from questions where question_id = {1}")
        rows = cur.fetchall()[0]
    elif rows[0] in [3, 4]:
        cur.execute(f"update user_cq set curr_q = {5} where tg_user_id = {chat_id}")
        cur.execute(f"select ans_n from questions where question_id = {5}")
        rows0 = cur.fetchall()[0]
        cur.execute(f"select question, answer_1, answer_2, answer_3, answer_4 from questions where question_id = {5}")
        rows = cur.fetchall()[0]
    elif rows[0] == 6:
        cur.execute(f"update user_cq set curr_q = {11} where tg_user_id = {chat_id}")
        cur.execute(f"select ans_n from questions where question_id = {11}")
        rows0 = cur.fetchall()[0]
        cur.execute(f"select question, answer_1, answer_2, answer_3, answer_4 from questions where question_id = {11}")
        rows = cur.fetchall()[0]
    elif (rows[0] == 2) and (list(rows0[0])[len(list(rows0[0])) - 1] == '1'):
        cur.execute(f"update user_cq set curr_q = {4} where tg_user_id = {chat_id}")
        cur.execute(f"select ans_n from questions where question_id = {4}")
        rows0 = cur.fetchall()[0]
        cur.execute(f"select question, answer_1, answer_2, answer_3, answer_4 from questions where question_id = {4}")
        rows = cur.fetchall()[0]
    elif (rows[0] == 5) and (list(rows0[0])[len(list(rows0[0])) - 1] == '1'):
        cur.execute(f"update user_cq set curr_q = {7} where tg_user_id = {chat_id}")
        cur.execute(f"select ans_n from questions where question_id = {7}")
        rows0 = cur.fetchall()[0]
        cur.execute(f"select question, answer_1, answer_2, answer_3, answer_4 from questions where question_id = {7}")
        rows = cur.fetchall()[0]
    else:
        cur.execute(f"update user_cq set curr_q = {int(rows[0]) + 1} where tg_user_id = {chat_id}")
        cur.execute(f"select ans_n from questions where question_id = {int(rows[0]) + 1}")
        rows0 = cur.fetchall()[0]
        cur.execute(f"select question, answer_1, answer_2, answer_3, answer_4 from questions where question_id = {int(rows[0]) + 1}")
        rows = cur.fetchall()[0]

    if rows[0] in [2, 5]:
        cur.execute(f"update user_a set answers = answers || '-' where tg_user_id = {chat_id}")

    kb = KeyboardBuilder(button_type=InlineKeyboardButton)
    for _ in range(1, rows0[0]+1):
        kb.row(InlineKeyboardButton(text=str(rows[_]), callback_data=f'callquest_{_}'), width=1)
    await bot.send_message(chat_id=chat_id, text=rows[0], reply_markup=InlineKeyboardMarkup(inline_keyboard=kb.export()))


@dp.callback_query(F.data.split("_")[1] == '1')
async def callback(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    cur.execute(f"select curr_q from user_cq where tg_user_id = {callback_query.from_user.id}")
    rows = cur.fetchall()[0]
    cur.execute(f"update user_a set answers = answers || '1' where tg_user_id = {callback_query.from_user.id}")
    cur.execute(f"select ans_1 from questions where question_id = {int(rows[0])}")
    rows = cur.fetchall()[0]
    await bot.send_message(chat_id=callback_query.from_user.id, text=rows[0])
    await question(chat_id=callback_query.from_user.id)


@dp.callback_query(F.data.split("_")[1] == '2')
async def callback(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    cur.execute(f"select curr_q from user_cq where tg_user_id = {callback_query.from_user.id}")
    rows = cur.fetchall()[0]
    cur.execute(f"update user_a set answers = answers || '2' where tg_user_id = {callback_query.from_user.id}")
    cur.execute(f"select ans_2 from questions where question_id = {int(rows[0])}")
    rows = cur.fetchall()[0]
    await bot.send_message(chat_id=callback_query.from_user.id, text=rows[0])
    await question(chat_id=callback_query.from_user.id)


@dp.callback_query(F.data.split("_")[1] == '3')
async def callback(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    cur.execute(f"select curr_q from user_cq where tg_user_id = {callback_query.from_user.id}")
    rows = cur.fetchall()[0]
    cur.execute(f"update user_a set answers = answers || '3' where tg_user_id = {callback_query.from_user.id}")
    cur.execute(f"select ans_3 from questions where question_id = {int(rows[0])}")
    rows = cur.fetchall()[0]
    await bot.send_message(chat_id=callback_query.from_user.id, text=rows[0])
    await question(chat_id=callback_query.from_user.id)


@dp.callback_query(F.data.split("_")[1] == '4')
async def callback(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    cur.execute(f"select curr_q from user_cq where tg_user_id = {callback_query.from_user.id}")
    rows = cur.fetchall()[0]
    cur.execute(f"update user_a set answers = answers || '4' where tg_user_id = {callback_query.from_user.id}")
    cur.execute(f"select ans_4 from questions where question_id = {int(rows[0])}")
    rows = cur.fetchall()[0]
    await bot.send_message(chat_id=callback_query.from_user.id, text=rows[0])
    await question(chat_id=callback_query.from_user.id)


async def finish_quiz(chat_id):
    await bot.send_message(chat_id=chat_id, text=f"конец")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(level=INFO, stream=stdout)
    run(main())


