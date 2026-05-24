import random
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import database as db

router = Router()

# База данных РП-команд (Сюда можно дописывать любые команды бесконечно)
RP_DATA = {
    "поцеловать": {
        "solo": "❤️ {user} поцеловал(а) {target}",
        "pair": "💖 {user} нежно поцеловал(а) свою вторую половинку {target}!",
        "image": "https://i.postimg.cc/85zX7pYg/kiss.jpg"
    },
    "обнять": {
        "solo": "🫂 {user} крепко обнял(а) {target}",
        "pair": "💞 {user} прижал(а) к себе свою любовь — {target}",
        "image": "https://i.postimg.cc/L8M3gfq3/hug.jpg"
    }
}

# МИДЛВАРЬ ДЛЯ АВТОРЕГИСТРАЦИИ
@router.message()
async def register_middleware(message: Message):
    # Автоматически регистрируем того, кто пишет, и того, на кого ответили
    db.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        db.get_or_create_user(
            message.reply_to_message.from_user.id, 
            message.reply_to_message.from_user.username, 
            message.reply_to_message.from_user.first_name
        )
    return

# --- КОМАНДА: ФАРМА ---
@router.message(F.text.lower() == "фарма")
async def farm_quese(message: Message):
    user = db.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    now = datetime.now()
    
    if user['last_farm']:
        last_farm_time = datetime.strptime(user['last_farm'], "%Y-%m-%d %H:%M:%S")
        next_farm = last_farm_time + timedelta(hours=4)
        if now < next_farm:
            remains = next_farm - now
            minutes, seconds = divmod(remains.seconds, 60)
            hours, minutes = divmod(minutes, 60)
            await message.reply(f"❌ Рано! Фармить коины Quese можно раз в 4 часа.\nЖдать еще: {hours}ч {minutes}м.")
            return

    earned = random.randint(50, 250)
    new_balance = user['quese_balance'] + earned
    db.update_farm(user['tg_id'], new_balance, now.strftime("%Y-%m-%d %H:%M:%S"))
    await message.reply(f"🚜 Ты успешно пофармил и получил **{earned} Quese**! 🎉\nБаланс: {new_balance} Quese.")

# --- КОМАНДА: БРАК ---
@router.message(F.text.lower() == "брак")
async def propose_marriage(message: Message):
    if not message.reply_to_message:
        await message.reply(" Ответь сообщением на того, с кем хочешь заключить брак!")
        return
        
    target = message.reply_to_message.from_user
    user_id = message.from_user.id

    if target.id == user_id:
        await message.reply("❌ Нельзя жениться на самом себе!")
        return
    if target.is_bot:
        await message.reply("❌ Нельзя жениться на боте!")
        return

    user_data = db.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    target_data = db.get_or_create_user(target.id, target.username, target.first_name)

    if user_data['partner_id'] or target_data['partner_id']:
        await message.reply("❌ Кто-то из вас уже состоит в отношениях!")
        return

    # Клавиатура предложения
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💍 Согласен", callback_data=f"marry_yes_{user_id}_{target.id}"),
            InlineKeyboardButton(text="❌ Отказ", callback_data=f"marry_no_{user_id}_{target.id}")
        ]
    ])
    await message.answer(f"💍 [{target.first_name}](tg://user?id={target.id}), тебе предложили брак! Ты согласен(а)?", reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data.startswith("marry_"))
async def process_marriage_decision(callback: CallbackQuery):
    data = callback.data.split("_")
    action, suitor_id, target_id = data[1], int(data[2]), int(data[3])

    if callback.from_user.id != target_id:
        await callback.answer("❌ Это предложение не тебе!", show_alert=True)
        return

    suitor = db.get_or_create_user(suitor_id, "", "")
    target = db.get_or_create_user(target_id, "", "")

    if action == "yes":
        db.create_marriage(suitor_id, target_id)
        await callback.message.edit_text(f"🎉 Поздравляем! ❤️ {suitor['first_name']} и {target['first_name']} теперь официальная пара! 🎉")
    else:
        await callback.message.edit_text(f"💔 {target['first_name']} разбивает сердце {suitor['first_name']} и отвергает предложение.")
    await callback.answer()

# --- ОБРАБОТЧИК РП И ОТНОШЕНИЙ ---
@router.message()
async def process_rp_commands(message: Message):
    if not message.text or not message.reply_to_message:
        return

    raw_text = message.text.strip().lower()
    user_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id

    user_data = db.get_or_create_user(user_id, message.from_user.username, message.from_user.first_name)
    target_data = db.get_or_create_user(target_id, message.reply_to_message.from_user.username, message.reply_to_message.from_user.first_name)

    # 1. СЕМЕЙНЫЕ КОМАНДЫ (С ТОЧКОЙ)
    if raw_text.startswith(".отн "):
        cmd = raw_text.replace(".отн ", "").strip()
        if cmd in RP_DATA:
            if user_data['partner_id'] != target_id:
                await message.reply("❌ Вы можете использовать семейные команды только со своей половинкой!")
                return
            
            caption_text = RP_DATA[cmd]["pair"].format(user=user_data['first_name'], target=target_data['first_name'])
            await message.answer_photo(photo=RP_DATA[cmd]["image"], caption=caption_text)

    # 2. ОБЫЧНЫЕ РП КОМАНДЫ (БЕЗ ТОЧКИ)
    elif raw_text in RP_DATA:
        caption_text = RP_DATA[raw_text]["solo"].format(user=user_data['first_name'], target=target_data['first_name'])
        await message.answer_photo(photo=RP_DATA[raw_text]["image"], caption=caption_text)
