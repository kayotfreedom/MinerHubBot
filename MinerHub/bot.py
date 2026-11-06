import time

print('[START] Version: 1.1')

import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message

from telethon import TelegramClient, events
import os
import sys
import importlib


from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, KeyboardButton, InlineKeyboardButton

from database import *
from settings import *
from casedatabase import *
from auto_bur_database import *

from aiogram.filters.callback_data import CallbackData



logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
router = Router()
last_press_time = {}
last_oil_time = {}


class AdminState(StatesGroup):
    waiting_for_user_id_add_stars = State()
    waiting_for_stars_amount_add = State()
    waiting_for_user_id_remove_stars = State()
    waiting_for_stars_amount_remove = State()
    waiting_for_mailing_text = State()
    waiting_for_channel_id_add = State()
    waiting_for_channel_id_delete = State()
    waiting_for_promocode_activation = State()
    waiting_for_promo_details_add = State()
    waiting_for_promocode_delete = State()





def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Копать"),
        KeyboardButton(text="Руда"),
        KeyboardButton(text="Инвентарь")
    )
    builder.row(
        KeyboardButton(text="Баланс"),
        KeyboardButton(text="Меню")
    )
    return builder.as_markup(resize_keyboard=True)

def get_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Назад"),
        KeyboardButton(text="Уровень"),
        KeyboardButton(text="Магазин"),
        KeyboardButton(text="Кейсы")
    )
    builder.row(
        KeyboardButton(text="Автобур"),
        KeyboardButton(text='Донат'),
        KeyboardButton(text="Профиль")
    )
    return builder.as_markup(resize_keyboard=True)

def get_auto_bur_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Мой авто-бур")
    return builder.as_markup(resize_keyboard=True)

@router.message(StateFilter(AdminState.waiting_for_user_id_add_stars))
async def process_add_stars_user_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id_add_stars=message.text)
    await bot.send_message(message.chat.id, "<b>Введите количество звезд для добавления:</b>", parse_mode='HTML')
    await state.set_state(AdminState.waiting_for_stars_amount_add)

@router.message(StateFilter(AdminState.waiting_for_stars_amount_add))
async def process_add_stars_amount(message: types.Message, state: FSMContext):
    try:
        stars = int(message.text)
        data = await state.get_data()
        user_id = int(data.get("user_id_add_stars"))
        increment_donate(user_id, stars)
        await bot.send_message(message.chat.id, f"<b>✅ {stars} звезд успешно добавлено пользователю с ID {user_id}</b>", parse_mode='HTML')
        await bot.send_message(user_id, f"✅ Администратор добавил вам {stars} звезд!", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат. Пожалуйста, введите число.</b>", parse_mode='HTML')
    except TypeError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат ID.</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_user_id_remove_stars))
async def process_remove_stars_user_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id_remove_stars=message.text)
    await bot.send_message(message.chat.id, "<b>Введите количество звезд для удаления:</b>", parse_mode='HTML')
    await state.set_state(AdminState.waiting_for_stars_amount_remove)

@router.message(StateFilter(AdminState.waiting_for_stars_amount_remove))
async def process_remove_stars_amount(message: types.Message, state: FSMContext):
    try:
        stars = int(message.text)
        data = await state.get_data()
        user_id = int(data.get("user_id_add_stars"))
        deincrement_donate(user_id, stars)
        await bot.send_message(message.chat.id, "<b>✅ Звезды успешно удалены!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат. Пожалуйста, введите число.</b>", parse_mode='HTML')
    except TypeError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат ID.</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_mailing_text))
async def process_mailing_text(message: types.Message, state: FSMContext):
    text = message.text
    users = get_users()
    counter = 0

    for user in users:
        user_id = user[0]
        ref_link = f"\n\nПерешли ссылку всем своим друзьям — https://t.me/{ (await bot.me()).username }?start={user_id}"
        full_text = f"{text}{ref_link}"

        try:
            counter += 1
            await bot.send_message(user_id, f"<b>{full_text}</b>", parse_mode='HTML')
            print(f"[РАССЫЛКА] Отправлено: {user_id}")
        except Exception as e:
            print(f"[РАССЫЛКА] Не отправлено: {user_id}")

    await bot.send_message(message.chat.id, f"<b>✅ Рассылка успешно отправлена!\n\nОтправлено: {counter}/{str(len(users))} пользователю</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_channel_id_add))
async def process_add_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id_to_add = int(message.text)
        if channel_id_to_add not in channel_ids:
            channel_ids.append(channel_id_to_add)
            await bot.send_message(message.chat.id, "<b>✅ Канал успешно добавлен!</b>", parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, "<b>⚠️ Этот канал уже есть в списке.</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ID канала!</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_channel_id_delete))
async def process_delete_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id_to_delete = int(message.text)
        if channel_id_to_delete in channel_ids:
            channel_ids.remove(channel_id_to_delete)
            await bot.send_message(message.chat.id, "<b>✅ Канал успешно удален!</b>", parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, "<b>❌ Канал не найден!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ID канала!</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_promocode_activation))
async def process_promocode_activation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    promocode = message.text
    success, result = use_promocode(promocode, user_id)
    if success:
        await bot.send_message(message.chat.id, f"<b>✅ Промокод успешно активирован!\nВам начислено {result} ⭐️</b>", parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f"<b>❌ Ошибка: {result}</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_promo_details_add))
async def process_add_promo_details(message: types.Message, state: FSMContext):
    try:
        promocode, stars_str, uses_str = message.text.split(",")
        stars = int(stars_str.strip())
        uses = int(uses_str.strip())
        add_promocode(promocode.strip(), stars, uses)
        await bot.send_message(message.chat.id, "<b>✅ Промокод успешно добавлен!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ввод! Введите промокод, количество звезд, количество использований через запятую.</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_promocode_delete))
async def process_delete_promo(message: types.Message, state: FSMContext):
    try:
        promocode = message.text.strip()
        deactivate_promocode(promocode)
        await bot.send_message(message.chat.id, "<b>✅ Промокод успешно удален!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ввод!</b>", parse_mode='HTML')
    await state.clear()


@router.message(CommandStart())
async def handle_start(message: types.Message, bot: Bot):
    args = message.text.split()
    user_id = message.from_user.id
    username = message.from_user.username or f"User{user_id}"
    ref_link = f"https://t.me/{ (await bot.me()).username }?start={user_id}"

    builder = InlineKeyboardBuilder()
    builder.button(text="Поделиться ссылкой", url=f"https://t.me/share/url?url={ref_link}")
    markup = builder.as_markup()

    start_command = BotCommand(command='start', description='♻️ Перезапустить бота')
    why_command = BotCommand(command='why', description='🌟 Зачем нужны звезды?')
    await bot.set_my_commands([start_command, why_command])
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonCommands()
    )

    if not user_exists(user_id):
        referral_id = None
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
        if len(args) > 1 and args[1].isdigit():
            referral_id = int(args[1])
            if user_exists(referral_id):
                await bot.send_message(referral_id, f"<b>☑️ По вашей реферальной ссылке перешел новый пользователь: {user_id}.\n\nНа ваш баланс зачислено 0.3 мк!\n\nПерешли ссылку — {ref_link}</b>", parse_mode='HTML')
                await bot.send_message(admins, text=f"Новый пользователь! рефер: {referral_id}, пользователь: {user_id}", parse_mode='HTML')
                increment_referrals(referral_id)
                increment_stars(referral_id, 3)
        add_user(user_id, username, referral_id)
        add_user2(user_id, 1)
        add_bur(user_id, username)
        await bot.send_message(user_id, "⭐", reply_markup=get_main_keyboard())
        await bot.send_message(user_id, f"<b>Добро пожаловать в MineHub!\nБот где вы можете отдохнуть от работы, учебы, тренировок!\nЖмите кнопки!</b>", parse_mode='HTML')
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
        await bot.send_message(user_id, "⭐", reply_markup=get_main_keyboard())
        await bot.send_message(user_id, f"<b>Добро пожаловать в MineHub!\nБот где вы можете отдохнуть от работы, учебы, тренировок!\nЖмите кнопки!\n\n🔗 Ваша ссылка - {ref_link}</b>", parse_mode='HTML', reply_markup=markup)

@router.message(Command("why"))
async def handle_why_command(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    ref_link = f"https://t.me/{ (await bot.me()).username }?start={user_id}"
    if user_exists(user_id):
        await bot.send_message(user_id, f"🌟Звезды — <b>официальная</b> валюта Telegram\n\nПриглашай друзей и получай 3⭐️ за 1 друга\n<pre>‼️Их можно продать и получить деньги. Также за счет звезд можно дарить подарки друзьям.\n\nИспользовать звезды еще можно в качестве оплат за услуги в ботах/тапалках</pre>\n\n<i>Пересылай свою ссылку — {ref_link}</i>", parse_mode='HTML')
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
        await bot.send_message(user_id, "Сначала используйте команду /start, чтобы зарегистрироваться.")
@router.message(Command("admin"))
async def adminpanel_command(message: types.Message, bot: Bot):
    if message.from_user.id in admins:
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="⭐️ Выдать звезды", callback_data="add_stars"),
            InlineKeyboardButton(text="⭐️ Снять звезды", callback_data="remove_stars")
        )
        builder.row(
            InlineKeyboardButton(text="📨 Рассылка", callback_data="mailing")
        )
        builder.row(
            InlineKeyboardButton(text="📚 Добавить канал", callback_data="add_channel"),
            InlineKeyboardButton(text="🚫 Удалить канал", callback_data='delete_channel')
        )
        builder.row(
            InlineKeyboardButton(text="📨 Рассылка 0 реф", callback_data='mailing_zero_refs')
        )
        builder.row(
            InlineKeyboardButton(text="🎁 Добавить промокод", callback_data='add_promo_code'),
            InlineKeyboardButton(text="🚫 Удалить промокод", callback_data='remove_promo_code')
        )
        markup = builder.as_markup()
        await bot.send_message(message.chat.id, f"<b>📊 Админ-панель\n\n👥 Пользователей: {get_user_count()}\n💸 Выплачено: {get_total_withdrawn()} ⭐️</b>", parse_mode='HTML', reply_markup=markup)

@router.message()
async def handle_reply_buttons(message: types.Message, bot: Bot):
    global stars, kirkaa, ruda, user_ruda, iran, stone, zem, vsego, obich, redkiy, mif, uluch, ekip, predmetniy, obichniy, level, cash, status_pokupki_bura, pupka_bura_status, pokupka_bura_status, inv
    user_id = message.from_user.id
    username = message.from_user.username or f"User{user_id}"
    ref_link = f"https://t.me/{ (await bot.me()).username }?start={user_id}"
    if message.text == "Баланс":
        ls = get_cash(user_id)
        stars = ls[2]
        await bot.send_message(user_id, text=f"Ваш баланс: {stars}")
    if message.text == "Руда":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Земля", callback_data="zem")
        )
        builder.row(
            InlineKeyboardButton(text="Камень", callback_data="stone")
        )
        builder.row(
            InlineKeyboardButton(text="Железо", callback_data="iran")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, text="Выберите руду:", reply_markup=markup)
    if message.text == "Копать":
        global kirkaa, ruda
        user_kirka = get_kirka(user_id)
        user_ruda = get_vibor_ruda(user_id)
        # Получаем текущее время
        current_time = time.time()
        if user_id in last_press_time:
            # Вычисляем промежуток времени с последнего нажатия
            elapsed_time = current_time - last_press_time[user_id]
            if elapsed_time <= 2:
                await bot.send_message(user_id, text="В данном боте можно копать только раз в 2 секунды!\nЧтобы копать с меньшим промежутком воспользуйтесь ботами:\n...\n...\n...")
                return

        last_press_time[user_id] = current_time
        if user_kirka:
            kirkaa = user_kirka[3]
        if user_ruda:
            ruda = user_ruda[6]
            if kirkaa == "1":
                rud = [1, 2, 3]
                template = random.choice(rud)
                if ruda == 1:
                    increment_ruda_zemlya(user_id, template)
                    await bot.send_message(user_id,
                                                text=f"Ура! Вы выкопали {template} земли! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
                    pop_cash(user_id, 999999999)
                elif ruda == 2:
                    increment_ruda_stone(user_id, template)
                    await bot.send_message(user_id,
                                            text=f"Ура! Вы выкопали {template} камня! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
                elif ruda == 3:
                    increment_ruda_iran(user_id, template)
                    await bot.send_message(user_id,
                                            text=f"Ура! Вы выкопали {template} железа! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
            elif kirkaa == "2":
                rud = [2, 3, 4, 5, 6]
                template = random.choice(rud)
                if ruda == 1:
                    increment_ruda_zemlya(user_id, template)
                    await bot.send_message(user_id,
                                           text=f"Ура! Вы выкопали {template} земли! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
                elif ruda == 2:
                    increment_ruda_stone(user_id, template)
                    await bot.send_message(user_id,
                                           text=f"Ура! Вы выкопали {template} камня! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
                elif ruda == 3:
                    increment_ruda_iran(user_id, template)
                    await bot.send_message(user_id,
                                           text=f"Ура! Вы выкопали {template} железа! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
            elif kirkaa == "3":
                rud = [4, 5, 6, 7, 8, 9, 10, 11, 12]
                template = random.choice(rud)
                if ruda == 1:
                    increment_ruda_zemlya(user_id, template)
                    await bot.send_message(user_id,
                                           text=f"Ура! Вы выкопали {template} земли! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
                elif ruda == 2:
                    increment_ruda_stone(user_id, template)
                    await bot.send_message(user_id,
                                           text=f"Ура! Вы выкопали {template} камня! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
                elif ruda == 3:
                    increment_ruda_iran(user_id, template)
                    await bot.send_message(user_id,
                                           text=f"Ура! Вы выкопали {template} железа! Продолжайте в том же духе!")
                    vsego_ruda(user_id, template)
                    set_vsego_dobito(user_id, template)
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
    if message.text == "Инвентарь":
        user_zem = get_ruda_zemlya(user_id)
        user_stone = get_ruda_stone(user_id)
        user_iran = get_ruda_iran(user_id)
        user_vsego = get_vsego_ruda(user_id)
        builder = InlineKeyboardBuilder()
        builder.button(text="Продать все", callback_data="prodat_bce")
        markup = builder.as_markup()
        if user_vsego:
            vsego = user_vsego[7]
        if user_zem:
            zem = user_zem[1]
        if user_stone:
            stone = user_stone[4]
        if user_iran:
            iran = user_iran[5]
        await bot.send_message(user_id, text=f"В вашем инвентаре:\nЗемля: {zem}\nКамень: {stone}\nЖелезо: {iran}\n\nВсего руды: {vsego}", reply_markup=markup)
    if message.text == "Магазин":
        global level
        user_data = get_cash(user_id)
        user_level = get_level(user_id)
        builder = InlineKeyboardBuilder()
        builder.button(text="Инструменты:", callback_data="p")
        builder.row(
            InlineKeyboardButton(text="Каменная кирка", callback_data="stone_kirka"),
            InlineKeyboardButton(text="Железная кирка", callback_data="iran_kirka")
        )
        one_level_markup = builder.as_markup()
        builder = InlineKeyboardBuilder()
        builder.button(text="Инструменты:", callback_data="p")
        builder.row(
            InlineKeyboardButton(text="Каменная кирка", callback_data="stone_kirka"),
            InlineKeyboardButton(text="Железная кирка", callback_data="iran_kirka")
        )
        builder.row(
            InlineKeyboardButton(text="Алмазная кирка", callback_data="almaz_kirka"),
            InlineKeyboardButton(text="Золотая кирка", callback_data="zolotaya_kirka")
        )
        two_level_markup = builder.as_markup()
        if user_data:
            stars = user_data[2]
            level = user_level[6]
        if level == 1:
            await bot.send_message(user_id, text=f"У вас на балансе: {stars}\nВаш уровень: 1\nНа продаже:", reply_markup=one_level_markup)
        if level == 2:
            await bot.send_message(user_id, text=f"У вас на балансе: {stars}\nВаш уровень: 1\nНа продаже:", reply_markup=two_level_markup)
    if message.text == "Донат":
        user_data = get_user(user_id)
        builder = InlineKeyboardBuilder()
        builder.button(text="🎁 Активировать промокод", callback_data="promocode")
        builder.button(text="Пополнить донат", callback_data="aq")
        markup_profile = builder.as_markup()
        if user_data:
            withdrawed = user_data[5]
            stars = user_data[2]
            await bot.send_message(user_id, f'<b>У тебя на счету: {stars} хаб-коинов\nПотрачено хаб-коинов: {withdrawed}</b>', parse_mode='HTML', reply_markup=markup_profile)
        else:
            await bot.send_message(user_id, "<b>❌ Ваш профиль не найден. Используйте /start для регистрации.</b>", parse_mode='HTML')
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
    if message.text == "Меню":
        await bot.send_message(user_id, text="Вы попали в меню!", reply_markup=get_menu_keyboard())
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
    if message.text == "Назад":
        await bot.send_message(user_id, text="🔙", reply_markup=get_main_keyboard())
    if message.text == "Кейсы":
        await user_case(user_id)
    if message.text == "Уровень":
        user_level = get_level(user_id)
        user_vsego = get_vsego_ruda(user_id)
        user_cash = get_cash(user_id)
        if user_level:
            level = user_level[6]
        if user_cash:
            cash = user_cash[2]
        if user_vsego:
            vsego = user_vsego[8]
        if level == 1:
            ruda_proc1 = (vsego / 500) * 100
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Улучшить уровень", callback_data="upgrade_level")
            )
            one_markup = builder.as_markup()
            await bot.send_message(user_id, text=f"Ваш уровень: 1\nПроцесс:\nРуда: {vsego} ({ruda_proc1}%) / 500\nДеньги: {cash}$ / 600\n\nЧтобы улучшить нажмите кнопку ниже", reply_markup=one_markup)
        if level == 2:
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Улучшить уровень", callback_data="upgrade_level")
            )
            one_markup = builder.as_markup()
            await bot.send_message(user_id,
                                   text=f"Ваш уровень: 2\nПроцесс:\nРуда: {vsego} / 500\nДеньги: {cash}$ / 600\n\nЧтобы улучшить нажмите кнопку ниже",
                                   reply_markup=one_markup)
    if message.text == "Автобу":
        await bot.send_message(user_id,
                               text="Авто-бур находиться в разработке, воспользуйтесь нашим юзер-ботом для авто-копания!")
    if message.text == "Автобур":
        await bot.send_message(user_id, text="Меню авто-бура:", reply_markup=get_auto_bur_menu_keyboard())
    if message.text == "Мой авто-бур":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="")
        )

@router.callback_query()
async def handle_stars_callback(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    global stars, zemlya, stoni, irani, vsegoo, vibor, kirka, cash, level, status_bura, kol_vo_ruda_bur, oil, bagaj_uluch, inv, oil_uluch
    user_id = call.from_user.id
    username = call.from_user.username
    user_data = get_user(user_id)
    if call.data == "inv_bur":
        user_inv = get_inv(user_id)
        if user_inv:
            inv = user_inv[8]
        await bot.send_message(user_id, text=f"В инвентаре вашего бура:\nРуда: {inv} ед.")
    if call.data == "upr_bur":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Топливо", callback_data="oil_bur"),
            InlineKeyboardButton(text="Улучшение бура", callback_data="uluch_bura")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, text="Вы попали в меню управления авто-буром!\nВыберите пункт:", reply_markup=markup)
    if call.data == "oil_bur":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Качать топливо", callback_data="kachat_oil")
        )
        builder.row(
            InlineKeyboardButton(text="Хранилище топлива", callback_data="hran_oil")
        )
        markup2 = builder.as_markup()
        await bot.send_message(user_id, text="Меню топлива:", reply_markup=markup2)
    if call.data == "kachat_oil":
        user_oil_uluch = get_oil_uluch(user_id)
        if user_oil_uluch:
            oil_uluch = user_oil_uluch[6]
        if oil_uluch == 1:
            # Получаем текущее время
            current_time = time.time()
            if user_id in last_oil_time:
                # Вычисляем промежуток времени с последнего нажатия
                elapsed_time = current_time - last_oil_time[user_id]
                if elapsed_time <= 86400:
                    await bot.send_message(user_id,
                                           text=f"Вы уже добывали топливо сегодня! Приходите завтра в это же время!")
                    return

            last_oil_time[user_id] = current_time

            add_oil(user_id, 40)
            await bot.send_message(user_id, text="Вы успешно добыли 40 ед. топлива!")
    if call.data == "start_bur":
        user_status_bura = get_status_bur(user_id)
        user_kol_vo_ruda_bur = get_kol_vo_ruda_uluch_bur(user_id)
        user_bagaj_uluch = get_bagaj_uluch(user_id)
        bur_oil = get_bur_oil(user_id)
        bur_inv = get_inv(user_id)
        if user_status_bura:
            status_bura = user_status_bura[3]
        if bur_inv:
            inv = bur_inv[8]
        if user_kol_vo_ruda_bur:
            kol_vo_ruda_bur = user_kol_vo_ruda_bur[5]
        if user_bagaj_uluch:
            bagaj_uluch = user_bagaj_uluch[4]
        if bur_oil:
            oil = bur_oil[7]
        if status_bura == 0:
            if oil == 0:
                await bot.send_message(user_id, text="В буре недостаточно топлива!")
            if oil > 0:
                start_bur(user_id, 1)

        elif status_bura < 0:
            print("Число с -")
            clear_status_bur(user_id, 0)
        elif status_bura > 1:
            print("Число больше 1")
            clear_status_bur(user_id, 0)
        print(status_bura)



    if call.data == "buy_bur":
        user_cash = get_cash(user_id)
        if user_cash:
            cash = user_cash[2]
        if cash < 100000:
            await bot.send_message(user_id, text="У вас недостаточно денег для покупки!")
        elif cash >= 100000:
            add_status_pokupki(user_id)
            minus_cash(user_id, 100000)
            await bot.send_message(user_id, text="Вы упешно приобрели авто-бур!")
    if call.data == "upgrade_level":
        user_level = get_level(user_id)
        user_cash = get_cash(user_id)
        user_vsego = get_vsego_dobito(user_id)
        if user_vsego:
            vsegoo = user_vsego[8]
        if user_cash:
            cash = user_cash[2]
        if user_level:
            level = user_level[6]
        if level == 1:
            if vsegoo >= 500:
                if cash >= 600:
                    minus_vsego_dobito(user_id, 500)
                    minus_cash(user_id, 600)
                    add_level(user_id, 1)
                    await bot.send_message(user_id, text="Поздравляем! Ваш уровень успешно улучшен до 2-го!")
            else:
                await bot.answer_callback_query(call.id, text="У вас недостаточно добытой руды для прокачки уровня!\nДобудьте еще руды и попробуйте!")
    if call.data == "zem":
        user_vibor = get_vibor_ruda(user_id)
        if user_vibor:
            vibor = user_vibor[6]
        clear_vibor_ruda(user_id)
        set_vibor_ruda(user_id, 1)
        await bot.send_message(user_id, text=f"Вы изменили руду на землю")
    if call.data == "stone":
        clear_vibor_ruda(user_id)
        set_vibor_ruda(user_id, 2)
        await bot.send_message(user_id, text=f"Вы изменили руду на камень")
    if call.data == "iran":
        clear_vibor_ruda(user_id)
        set_vibor_ruda(user_id, 3)
        await bot.send_message(user_id, text=f"Вы изменили руду на железо")
    if call.data == "iran_kirka":
        user_kirka = get_kirka(user_id)
        user_cash = get_cash(user_id)
        if user_cash:
            cash = user_cash[2]
        if user_kirka:
            kirka = user_kirka[3]
        if kirka == 3:
            await bot.send_message(user_id, text="Вы и так уже имеете железную кирку!")
        else:
            if 450 > cash:
                await bot.answer_callback_query(call.id, "❌ У вас недостаточно валюты для покупки!", show_alert=True)
            else:
                minus_cash(user_id, 450)
                kirka = 3
                delete_kirka(user_id)
                set_kirka(user_id, kirka)
                await bot.send_message(user_id, text="Вы успешно купили железную кирку!")
    if call.data == "stone_kirka":
        user_kirka = get_kirka(user_id)
        user_cash = get_cash(user_id)
        if user_cash:
            cash = user_cash[2]
        if user_kirka:
            kirka = user_kirka[3]
        if kirka == 2:
            await bot.send_message(user_id, text="Вы и так уже имеете каменную кирку!")
        else:
            if 150 > cash:
                await bot.answer_callback_query(call.id, "❌ У вас недостаточно валюты для покупки!", show_alert=True)
            else:
                minus_cash(user_id, 150)
                kirka = 2
                delete_kirka(user_id)
                set_kirka(user_id, kirka)
                await bot.send_message(user_id, text="Вы успешно купили каменную кирку!")
    if call.data == "prodat_bce":
        zem = get_ruda_zemlya(user_id)
        stone = get_ruda_stone(user_id)
        iran = get_ruda_iran(user_id)
        vsego = get_vsego_ruda(user_id)
        if vsego:
            vsegoo = vsego[7]
        if zem:
            zemlya = zem[1]
        if stone:
            stoni = stone[4]
        if iran:
            irani = iran[5]
        prod_ruda_zemlya(user_id, zemlya)
        prod_ruda_stone(user_id, stoni)
        prod_ruda_iran(user_id, irani)
        p = (zemlya * 0.5) + stoni + (irani * 1.5)
        minus_vsego(user_id, vsegoo)
        pop_cash(user_id, p)
        await bot.send_message(user_id, text=f"Успешно продано {vsegoo} руды!\nНа баланс зачисленно: {p}")
    if call.data == "ne_viveli_zvezdi":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/ABTOSOUND")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, text="Не вывелись звезды?\n\n1.Проверьте достаточно ли у вас звезд на балансе для вывода\n2.Напишите в поддержку если вы уверены что вы сделали все правильно", reply_markup=markup)
    if call.data == "ne_zaschitali_referala":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/ABTOSOUND")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, text="Не засчитали реферала?\n\n1.Проверьте зашел ли он по ВАШЕЙ реферальной ссылке, запустил бота, подписался на всех спонсоров - если это не сделано реферал не засчитается!\n2.Если реферал был в боте то не засчитается!\n3.Если все условия выполнены, но вам не зачислили реферала, то нажмите кнопку ниже и сообщите это администратору", reply_markup=markup)
    if call.data == "add_stars":
        await bot.send_message(user_id, "<b>Введите ID пользователя:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_user_id_add_stars)
    if call.data == "remove_stars":
        await bot.send_message(user_id, "<b>Введите ID пользователя:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_user_id_remove_stars)
    if call.data == "mailing":
        await bot.send_message(user_id, "<b>Введите текст для рассылки:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_mailing_text)
    if call.data == "add_channel":
        await bot.send_message(user_id, "<b>Введите ID канала:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_channel_id_add)
    if call.data == 'delete_channel':
        await bot.send_message(user_id, "<b>Введите ID канала:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_channel_id_delete)
    if call.data == 'mailing_zero_refs':
        text = "⁉️🤨Мы заметили, что вы не пригласили ни 1 друга!\n\nПерешли ссылку своим друзьям, а также по чатам, 3 ⭐️ за 1 приглашенного⤵️"
        users = get_user_zero_referrals()

        for user in users:
            user_id = user[0]
            ref_link = f"\n\nТвоя персональная ссылка — https://t.me/{ (await bot.me()).username }?start={user_id}"
            full_text = f"{text}{ref_link}"

            try:
                await bot.send_message(user_id, f"<b>{full_text}</b>", parse_mode='HTML')
                print(f"[РАССЫЛКА 1.0] Отправлено: {user_id}")
            except Exception as e:
                print(f"[РАССЫЛКА 1.0] Не отправлено: {user_id}")

        await bot.send_message(call.message.chat.id, "<b>✅ Рассылка успешно отправлена!</b>", parse_mode='HTML')
    if call.data == "check_subs":
        if await check_subscription(user_id, channel_ids, bot):
            await bot.send_message(user_id, "<b>⚠️ Подпишитесь на каналы, чтобы продолжить!</b>", parse_mode='HTML')
        else:
            reff_link = f"https://t.me/{ (await bot.me()).username }?start={user_id}"
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Поделиться ссылкой", url="https://t.me/share/url?url=" + reff_link)
            )
            markup = builder.as_markup()
            await bot.send_message(user_id, "⭐", reply_markup=get_main_keyboard())
            await bot.send_message(user_id, f"<b>✨ Добро пожаловать!\n\nРаспространяй свою ссылку и получи 3 ⭐️ телеграма за 1 приглашенного друга\n\n🔗 Ваша ссылка - {reff_link}</b>", parse_mode='HTML', reply_markup=markup)
    if call.data == "promocode":
        await bot.send_message(user_id, "<b>🎄 Введите промокод:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_promocode_activation)
    if call.data == "add_promo_code":
        await bot.send_message(user_id, "<b>Введите промокод, количество звезд, количество использований через запятую:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_promo_details_add)
    if call.data == "delete_promo_code":
        await bot.send_message(user_id, "<b>Введите промокод:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_promocode_delete)
    await call.answer()


async def check_subscription(user_id, channel_ids, bot: Bot):
    if not channel_ids:
        return True

    builder = InlineKeyboardBuilder()
    show_join_button = False
    for channel_id in channel_ids:
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator', 'restricted']:
                invite_link = (await bot.create_chat_invite_link(channel_id, member_limit=1)).invite_link
                builder.button(text="Подписаться", url=invite_link)
                show_join_button = True
        except Exception as e:
            print(f"Ошибка при проверке подписки: {e}")
            await bot.send_message(user_id, "Ошибка при проверке подписки. Пожалуйста, попробуйте позже.")
            return False

    if show_join_button:
        builder.row(
            InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subs")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, "<b>👋🏻 Добро пожаловать\n\nПодпишитесь на каналы, чтобы продолжить!</b>", parse_mode='HTML', reply_markup=markup)
        return True

    return False

async def user_case(user_id):
    global obichniy, redkiy, mif, ekip, predmetniy, uluch
    user_obich = get_obich(user_id)
    user_redkiy = get_redkiy(user_id)
    user_mif = get_mif(user_id)
    user_predmetniy = get_predmetniy(user_id)
    user_ekip = get_ekip(user_id)
    user_uluch = get_uluch(user_id)
    if user_obich:
        obichniy = user_obich[2]
    if user_redkiy:
        redkiy = user_redkiy[2]
    if user_mif:
        mif = user_mif[2]
    if user_predmetniy:
        predmetniy = user_predmetniy[2]
    if user_ekip:
        ekip = user_ekip[2]
    if user_uluch:
        uluch = user_uluch[2]

    await bot.send_message(user_id,
                           text=f"Ваши кейсы\n📦|Обычный кейс: {obichniy}\n🗳️|Редкий кейс: {redkiy}\n🕋|Мифический кейс: {mif}\n🧰|Кейс экипировки: {ekip}\n|Предметный кейс: {predmetniy}\n🗄️|Кейс улучшений: {uluch}")

async def start_bur_function(user_id, status_bura, inv, kol_vo_ruda_bur, bagaj_uluch, bot: Bot):
    start_bur(user_id, 1)
    while status_bura == 1:
        await bot.send_message(user_id, text="Авто-бур запущен!")
        if kol_vo_ruda_bur == 1:
            if bagaj_uluch == 1:
                while inv < 40000:
                    add_ruda_bur(user_id, 10000)
                    minus_oil(user_id, 1)
                    time.sleep(1)
                    print(inv)
                else:
                    await bot.send_message(user_id, text="Инвентарь бура переполнен! Бур остановлен!")



dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    from handlers.ignore_blocked import ignore_blocked_messages
    ignore_blocked_messages(dp)
    executor.start_polling(dp, skip_updates=True)
    client.run_until_disconnected()