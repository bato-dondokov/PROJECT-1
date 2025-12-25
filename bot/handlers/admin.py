from aiogram import F, Router, Bot
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

import database.requests as rq 
import keyboards.keyboards as kb
from states.administration import Administration

from config import XRAYS_DIR, TEETH_DIR, DB_FILE
from queue_manager import inference_queue
from logger import logger
import re
import os
import pandas as pd

admin_router = Router()


"""Обработчики сообщений администратора."""


@admin_router.message(Administration.waiting_admin_command)
async def get_admin_command(message: Message, state: FSMContext):
    """
    Обрабатывает сообщения в состоянии ожидания команд администратора:
        1) "Посмотреть прогресс экспертов": отправляет сообщение с прогрессом
        экспертов.
        2) "Добавить класс разметки": изменяет состояние, отправляет сообщение
        и меняет кнопки.
        3) "Добавить снимок": изменяет состояние, отправляет сообщение и 
        меняет кнопки.
        4) "Выгрузить БД": отправляет пользователю файл БД и сообщение.
    """
    logger.info(f"Начинаю обработку")
    command = message.text
    if command == "Посмотреть прогресс экспертов":
        experts, progress = await rq.get_answers_count_by_user()
        if experts:
            text = ""
            for i, expert in enumerate(experts):
                text += f"{i+1}. {expert[1]}: {expert[0]}\n"
                bar = "█" * int(expert[2]) + "—" * (10 - int(expert[2]))
                text += (f"Размечено: [{bar}]" 
                        f"{round((expert[2]) * 10)}%\n\n ")
                        # f"({expert[2]}/{progress[i][1]})\n\n")
            await message.answer(text)
        else:
            await message.answer('Отсутствуют результаты разметки.')
        
    # if command == "Добавить класс разметки":
    #     await state.set_state(Administration.waiting_new_label_class)
    #     await message.answer(
    #         text='Введите название нового класса разметки',
    #         reply_markup=kb.go_back
    #     )
    if command == "Добавить номер для доступа":
        await state.set_state(Administration.waiting_new_access_number)
        await message.answer(
            text=('Введите ФИО и номер телефона в формате:\n'
            'Иванов Иван Иванович - 79991234567\n'
            'номер телефона должен начинаться с 7 и содержать 11 цифр.'),
            reply_markup=kb.go_back
        )
    if command == "Добавить таблицу с номерами для доступа":
        await state.set_state(Administration.waiting_new_access_number_table)
        await message.answer(
            text=('Отправьте файл с номерами для доступа в формате .xlsx.'
                  '\nВ таблице ОБЯЗАТЕЛЬНО должны быть два столбца: '
                  '"ФИО" и "Телефон". Иначе файл не будет обработан.'),
            reply_markup=kb.go_back
        )
    if command == "Добавить снимок":
        await state.set_state(Administration.waiting_new_xray)
        await message.answer(
            text='Отправьте снимок.',
            reply_markup=kb.go_back
        )
    if command == "Выгрузить БД":
        db_file = FSInputFile(DB_FILE)
        await message.answer_document(
            document=db_file, 
            caption="БД выгружена успешно."
        )
        await message.answer('Выберите нужную команду.')
   

# @admin_router.message(Administration.waiting_new_label_class)
# async def get_new_label_class(message: Message, state: FSMContext):
#     """
#     Обрабатывает сообщение в состоянии ожидания названия нового класса 
#     разметки. Отправляет пользователю сообщение и добавляет InlineKeyboard 
#     для подтверждения.

#     Если пользователь отправил сообщение с текстом "Вернуться назад", то
#     переходит в состояние ожидания команды эксперта.
#     """
#     logger.info(f"Начинаю обработку")
#     await state.set_state(Administration.confirming_new_label_class)
#     if message.text == "Вернуться назад":
#         await state.set_state(Administration.waiting_admin_command)
#         await message.answer(
#             text='Выберите нужную команду.', 
#             reply_markup=kb.admin_commands
#         )
#     else:
#         label_name = message.text
#         await state.update_data(label_name=label_name)
#         await message.reply(
#             text=f'Подтвердите добавление класса: "{label_name}".',
#             reply_markup=kb.confirming
#         )


# @admin_router.callback_query(
#         Administration.confirming_new_label_class, 
#         F.data == "confirm"
# )
# async def confirm_new_label_class(callback: CallbackQuery, state: FSMContext):
#     """
#     Обрабатывает callback в состоянии подтверждения названия нового класса, 
#     если callback_data == 'confirm'. Добавляет новый класс в БД, удаляет 
#     inlineInlineKeyboard и переходит в состояние ожидания команды эксперта.
#     """
#     logger.info(f"Начинаю обработку")
#     data = await state.get_data()
#     label_name = data["label_name"]
#     await rq.add_label(label_name)

#     await callback.message.edit_reply_markup(reply_markup=None)
#     await callback.message.answer(f'Класс "{label_name}" добавлен.')
#     await state.set_state(Administration.waiting_admin_command)
#     await callback.message.answer(
#         text='Выберите нужную команду.', 
#         reply_markup=kb.admin_commands
#     )
#     logger.info(f"Обработка завершена")


# @admin_router.callback_query(
#         Administration.confirming_new_label_class,
#         F.data == "go_back"
# )
# async def go_back_admin_commands(callback: CallbackQuery, state: FSMContext):
#     """
#     Обрабатывает callback в состоянии подтверждения названия нового класса, 
#     если callback_data == 'go_back'. Удаляет inlineInlineKeyboard и переходит 
#     в состояние ожидания команды эксперта.
#     """
#     logger.info(f"Начинаю обработку")
#     await state.set_state(Administration.waiting_admin_command)
#     await callback.message.edit_reply_markup(reply_markup=None)
#     await callback.message.answer(
#         text='Выберите нужную команду.', 
#         reply_markup=kb.admin_commands
#     )


def extract_first_phone(phone_value: str) -> str | None:
    """
    Нормализация телефона:
    - 8XXXXXXXXXX  -> 7XXXXXXXXXX
    - +7XXXXXXXXXX -> 7XXXXXXXXXX
    - результат: 7XXXXXXXXXX (11 цифр)
    """
    if not isinstance(phone_value, str):
        return None

    # Убираем всё кроме цифр
    digits = re.sub(r"\D", "", phone_value)

    candidates = []

    # 8XXXXXXXXXX -> 7XXXXXXXXXX
    for m in re.findall(r"8\d{10}", digits):
        candidates.append("7" + m[1:])

    # 7XXXXXXXXXX (включая бывшие +7)
    candidates.extend(re.findall(r"7\d{10}", digits))

    if not candidates:
        return None

    return candidates[0]


@admin_router.message(Administration.waiting_new_access_number_table)
async def get_new_access_number_table(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания нового файла с номерами для 
    доступа. Если пользователь отправил сообщение с текстом "Вернуться назад", 
    то переходит в состояние ожидания команды администратора.
    Иначе обрабатывает файл и добавляет номера в БД.
    """
    logger.info(f"Начинаю обработку")
    if message.text == "Вернуться назад":
        await state.set_state(Administration.waiting_admin_command)
        await message.answer(
            text='Выберите нужную команду.', 
            reply_markup=kb.admin_commands
        )
    elif message.document:
        document = message.document
        file_id = document.file_id
        file_info = await message.bot.get_file(file_id)
        file_path = file_info.file_path
        file_name = document.file_name
        FIO_COLUMN = "ФИО"
        PHONE_COLUMN = "Телефон"

        if not file_name.endswith('.xlsx'):
            await message.reply('Ошибка: файл должен быть в формате .xlsx. '
                                'Попробуйте снова.')
            return

        temp_file = f'temp_{file_name}'
        await message.bot.download_file(file_path, destination=temp_file)

        try:
            df = pd.read_excel(temp_file, sheet_name=0)
        except Exception as e:
            await message.reply(f"Ошибка при открытии Excel: {e}")

        if FIO_COLUMN not in df.columns or PHONE_COLUMN not in df.columns:
            await message.reply(f"Ошибка: в таблице должны быть столбцы '{FIO_COLUMN}' и '{PHONE_COLUMN}'")
            return
        
        inserted = 0
        inserted_str = []

        for index, row in df.iterrows():
            fio = row[FIO_COLUMN]
            phone_raw = row[PHONE_COLUMN]

            # Пропуск пустых строк
            if pd.isna(fio) or pd.isna(phone_raw):
                continue

            phone = extract_first_phone(str(phone_raw))
            if not phone:
                continue
            inserted_str.append(f"Добавлeн: {fio} - {phone}")
            await rq.add_access_number(fio, phone)  

            inserted += 1



        # inserted_str.append(f'Добавлено номеров для доступа: {inserted}.')
        # response_text = "\n".join(inserted_str)
        os.remove(temp_file)
        
        await message.answer(f'Добавлено номеров для доступа: {inserted}.')
        await state.set_state(Administration.waiting_admin_command)
        await message.answer(
            text='Выберите нужную команду.', 
            reply_markup=kb.admin_commands
        )



@admin_router.message(Administration.waiting_new_access_number)
async def get_new_access_number(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания нового номера для доступа.
    Если пользователь отправил сообщение с текстом "Вернуться назад", то
    переходит в состояние ожидания команды администратора.
    Иначе отправляет сообщение с просьбой подтвердить добавление номера.
    """
    logger.info(f"Начинаю обработку")
    if message.text == "Вернуться назад":
        await state.set_state(Administration.waiting_admin_command)
        await message.answer(
            text='Выберите нужную команду.', 
            reply_markup=kb.admin_commands
        )
    else:
        answer = message.text

        if "-" not in answer:
            error_message = (f"Ошибка: неверный формат строки: {answer}\n"
                             "Ожидаемый формат: ФИО - номер"
                             "\nВведите данные повторно.")
            await message.reply(error_message)
        else:

            fio_part, phone_part = answer.split("-", 1)

            fio = fio_part.strip()
            phone_raw = phone_part.strip()

            if not fio:
                error_message = (f"Ошибка: ФИО пустое в строке: {answer}"
                                 "\nВведите данные повторно.")
                await message.reply(error_message)
            else:

                # Оставляем только цифры
                phone_digits = re.sub(r"\D", "", phone_raw)

                # Проверка номера
                if not phone_digits.startswith("7"):
                    error_message = (f"Ошибка: номер не начинается с 7: {phone_raw}"
                                     "\nВведите данные повторно.")
                    await message.reply(error_message)
                elif len(phone_digits) != 11:
                    error_message = (f"Ошибка: номер должен содержать 11 цифр: {phone_raw}"
                                     "\nВведите данные повторно.")
                    await message.reply(error_message)
                else:
                    await state.update_data(member_phone=phone_digits)
                    await state.update_data(member_fio=fio)

                    await state.set_state(Administration.confirming_new_access_number)
                    await message.reply(
                        text=f'Подтвердите добавление номера: \n"{fio}".',
                        reply_markup=kb.confirming_admin
                    )


@admin_router.callback_query(
        Administration.confirming_new_access_number, 
        F.data == "confirm"
)
async def confirm_new_access_number(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии подтверждения нового номера для доступа, 
    если callback_data == 'confirm'. Добавляет новый номер в БД, удаляет 
    inlineInlineKeyboard и переходит в состояние ожидания команды администратора.
    """    
    logger.info(f"Начинаю обработку")
    data = await state.get_data()
    fio = data["member_fio"]
    phone_digits = data["member_phone"]

    await rq.add_access_number(fio, phone_digits)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f'Номер "{phone_digits}" для {fio} добавлен.')
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )
    logger.info(f"Обработка завершена")


@admin_router.message(
        Administration.waiting_new_xray, 
        F.text == "Вернуться назад"
)
async def go_back_admin_commands(message: Message, state: FSMContext):
    """
    Обрабатывает сообщение в состоянии ожидания нового снимка, если сообщение 
    равно "Вернуться назад" переходит в состояние ожидания команды эксперта.
    """
    logger.info(f"Начинаю обработку")
    await state.set_state(Administration.waiting_admin_command)
    await message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )


@admin_router.message(Administration.waiting_new_xray, F.photo)
async def get_xray(message: Message, state: FSMContext):
    logger.info('Начинает обработку')
    """
    Обрабатывает сообщение в состоянии ожидания нового снимка, если 
    пользователь отправил фото. Переходит в состояние подтверждения снимка
    """
    await state.set_state(Administration.confirming_new_xray)
    await state.update_data(photo_id=message.photo[-1].file_id)
    await message.reply(
        text=f'Подтвердите добавление снимка.',
        reply_markup=kb.confirming_admin
    )
    

@admin_router.callback_query(
        Administration.confirming_new_xray, 
        F.data == "confirm"
)
async def confirm_xray(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обрабатывает callback в состоянии подтверждения нового снимка, 
    если callback_data == 'confirm'. Сохраняет снимок, использует модуль для 
    обнаружения зубов на снимке (Xray2Teeth) и добавляет путь до снимка в БД. 
    После чего переходит в состояние ожидания команды эксперта.
    """    
    logger.info(f"Начинаю обработку")
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    photo_file = await bot.get_file(data["photo_id"])
    xray_name = photo_file.file_unique_id
    xray_file = XRAYS_DIR + f"{xray_name}.png"

    await bot.download_file(photo_file.file_path, destination=xray_file)
    await rq.add_xray(xray_file)

    position = inference_queue.qsize() + 1
    await inference_queue.put((xray_file, TEETH_DIR))
    await callback.message.answer(f"Ваш снимок добавлен в очередь.\n"
                                  f"Позиция в очереди: {position}.")
    await rq.add_teeth(TEETH_DIR, xray_name, xray_file)

    await callback.message.answer(f'Снимок добавлен.')
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )


@admin_router.callback_query(
        Administration.confirming_new_xray,
        F.data == "go_back"
)
async def go_back_admin_commands(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает callback в состоянии подтверждения нового снимка, 
    если callback_data == 'go_back'. Удаляет inlineInlineKeyboard и переходит 
    в состояние ожидания команды эксперта.
    """ 
    logger.info(f"Начинаю обработку")
    await state.set_state(Administration.waiting_admin_command)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text='Выберите нужную команду.', 
        reply_markup=kb.admin_commands
    )