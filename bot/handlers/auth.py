from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database.requests as rq 
import keyboards.keyboards as kb
from states.authantication import Authentication
from states.labelling import Labelling
from states.administration import Administration
from config import EXPERT_PASSWORD, ADMIN_PASSWORD
from messages import AUTH_INSTRUCTIONS, HELP_MESSAGE

auth_router = Router()


"""
Обработчик авторизации.
"""


@auth_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """
    Обрабатывает команду /start. Отправляет пользователю сообщение и добавляет  
    ReplyKeyboard для выбора статуса.
    """
    await state.set_state(Authentication.waiting_user_status)
    await message.reply(
        text=f'Здравствуйте!\nВыберите ваш статус.',
        reply_markup=kb.main
    )


@auth_router.message(Command("help"))
async def start(message: Message, state: FSMContext):
    """
    Обрабатывает команду /help. Отправляет пользователю сообщение с инструкцией
    по использованию бота.
    """
    await message.reply(
        text=HELP_MESSAGE
    )


@auth_router.message(Authentication.waiting_user_status)
async def set_status(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания статуса пользователя. 
    Определяет статус пользователя, если пользователь Эксперт и он ранее уже
    проходил авторизацию, то изменяет состояние на ожидание команд эксперта и
    добавляет ReplyKeyboard для выбора команды.  
    В остальных случаях изменяет статус на ожидание пароля и отправляет
    сообщение с просьбой ввести пароль.
    """
    user_status = message.text
    if user_status in ("Эксперт", "Админ"):
        await state.update_data(user_status=user_status)
        
        is_user_exists = await rq.check_user(message.from_user.id, message.text)
        if user_status == "Эксперт" and is_user_exists:
            await state.set_state(Labelling.waiting_expert_command)
            await message.answer(
                text="Выберите команду.",
                reply_markup=kb.expert_commands
            )
        else:
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
    user_status = data["user_status"]

    if user_status == 'Эксперт' and password == EXPERT_PASSWORD:
        await rq.set_user(
            message.from_user.id, 
            message.from_user.first_name, 
            user_status
        )
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer(
            text="Выберите команду.",
            reply_markup=kb.expert_commands
        )
    elif user_status == "Админ" and password == ADMIN_PASSWORD:
        await rq.set_user(
            message.from_user.id, 
            message.from_user.first_name, 
            user_status
        )
        await state.set_state(Administration.waiting_admin_command)
        await message.answer(
            text='Выберите команду.', 
            reply_markup=kb.admin_commands
        )
    else:
        await message.reply('Неверный пароль, введите еще раз.')