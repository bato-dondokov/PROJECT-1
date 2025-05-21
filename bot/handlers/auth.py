from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboards.keyboards as kb
from states.authantication import Authentication
from states.labelling import Labelling
from states.administration import Administration
import database.requests as rq 


auth_router = Router()


@auth_router.message(CommandStart())
async def set_user_status(message: Message, state: FSMContext):
    await state.set_state(Authentication.waiting_user_status)
    await message.reply(f'Здравствуйте!\nВыберите ваш статус.',
                        reply_markup=kb.main)


@auth_router.message(Authentication.waiting_user_status)
async def password_request(message: Message, state: FSMContext):
    await state.update_data(user_status=message.text)
    is_user_exist = await rq.check_user(message.from_user.id, message.text)
    if message.text == "Эксперт" and is_user_exist:
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer("Выберите команду.",
                                reply_markup=kb.expert_commands)
    else:
        await state.set_state(Authentication.waiting_password)
        await message.reply('Введите пароль.\nЕсли выбрали не верный статус перезапустите бота командой /start',
                            reply_markup=kb.keyboard_remove)


@auth_router.message(Authentication.waiting_password)
async def auth(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    if data["user_status"] == 'Эксперт' and data["password"] == '111':
        await rq.set_user(message.from_user.id, message.from_user.first_name, data["user_status"])
        await state.set_state(Labelling.waiting_expert_command)
        await message.answer("Выберите команду.",
                             reply_markup=kb.expert_commands)
    elif data["user_status"] == "Админ" and data["password"] == '222':
        await rq.set_user(message.from_user.id, message.from_user.first_name, data["user_status"])
        await state.set_state(Administration.waiting_admin_command)
        await message.answer('Выберите команду.', reply_markup=kb.admin_commands)
    else:
        await message.reply('Неверный пароль, введите еще раз.')