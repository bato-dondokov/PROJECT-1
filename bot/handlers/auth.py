from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database.requests as rq 
import keyboards.keyboards as kb
from states.authantication import Authentication
from states.labelling import Labelling
from states.administration import Administration
from config import (
    RESIDENT_PASSWORD, 
    TEACHER_PASSWORD,
    ADMIN_PASSWORD, 
    PHONE_NUMBERS
)
from messages import (
    AUTH_INSTRUCTIONS, 
    HELP_MESSAGE, 
    WRONG_NUMBER_MESSAGE,
    CORRECT_NUMBER_MESSAGE
)

auth_router = Router()


"""Обработчик авторизации."""


@auth_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """
    Обрабатывает команду /start. Отправляет пользователю сообщение с просьбой
    поделиться номером.
    """
    await state.set_state(Authentication.waiting_contact)
    await message.reply(
        text=(
            'Здравствуйте!\n'
            'Пожалуйста, поделитесь своим контактом, нажав кнопку ниже.'
        ),
        reply_markup=kb.contact_keyboard
    )


@auth_router.message(Command("help"))
async def help(message: Message, state: FSMContext):
    """
    Обрабатывает команду /help. 
    Отправляет пользователю сообщение с инструкцией по использованию бота.
    """
    await message.reply(
        text=HELP_MESSAGE
    )


@auth_router.message(Authentication.waiting_contact,
                     F.contact)
async def check_contact(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение с контактом пользователя.
    Извлекает номер телефона. 
    Если номер разрешён позволяет выбрать роль.
    Иначе, отправляет сообщение с информацией об отсутствии доступа;
    """
    contact = message.contact
    phone = contact.phone_number
    if phone in PHONE_NUMBERS:
        await message.answer(
            text=CORRECT_NUMBER_MESSAGE,
            reply_markup=kb.role_keyboard
        )
        await state.set_state(Authentication.waiting_user_role)
    else:
        await message.answer(WRONG_NUMBER_MESSAGE)
        return


@auth_router.message(Authentication.waiting_user_role)
async def set_role(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания статуса пользователя. 
    Определяет статус пользователя, если пользователь Эксперт и он ранее уже
    проходил авторизацию, то изменяет состояние на ожидание команд эксперта и
    добавляет ReplyKeyboard для выбора команды.  
    В остальных случаях изменяет статус на ожидание пароля и отправляет
    сообщение с просьбой ввести пароль.
    """
    user_role = message.text
    user_tg_id = message.from_user.id

    if user_role in ("Админ", "Преподаватель", "Ординатор"):
        await state.update_data(user_role=user_role)
        await state.update_data(user_tg_id=user_tg_id)
        
        await state.set_state(Authentication.waiting_password)
        await message.reply(
            text=AUTH_INSTRUCTIONS,
            reply_markup=kb.keyboard_remove
        )


@auth_router.message(Authentication.waiting_password)
async def auth(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидании пароля. Если пользователь
    вводит верный пароль, то изменяет состояние на ожидание команд и добавляет 
    ReplyKeyboard с командами, иначе отправляет сообщение с просьбой ввести 
    пароль повторно.
    """
    password = message.text
    data = await state.get_data()
    user_role = data["user_role"]
    user_tg_id = data["user_tg_id"]

    if (user_role == 'Преподаватель' and password == TEACHER_PASSWORD) or \
       (user_role == 'Ординатор' and password == RESIDENT_PASSWORD):
        print( f"User {user_tg_id} authenticated as {user_role}" )

        await rq.set_user(
            user_tg_id, 
            message.from_user.first_name, 
            user_role
        )
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer(
            text="Выберите команду.",
            reply_markup=kb.expert_commands
        )
        
    elif user_role == "Админ" and password == ADMIN_PASSWORD:
        await rq.set_user(
            user_tg_id, 
            message.from_user.first_name, 
            user_role
        )
        await state.set_state(Administration.waiting_admin_command)
        await message.answer(
            text='Выберите команду.', 
            reply_markup=kb.admin_commands
        )
    else:
        await message.reply('Неверный пароль, введите еще раз.')