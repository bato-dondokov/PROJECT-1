from database.models import async_session 
from database.models import (
    User, 
    Label, 
    Xray, 
    Tooth, 
    Answer, 
    Recommendation
)
from sqlalchemy import select, update, func
import os


"""
Запросы в БД
"""


async def check_user(tg_id, status):
    """
    Возвращает True если существует пользователь с указанным tg_id, status 
    в таблице Users, иначе возвращает False
    """
    async with async_session() as session:
        is_user_exist = True
        user = await session.scalar(select(User).where(
            User.tg_id == tg_id, 
            User.status == status
        ))    
        if not user:
            is_user_exist = False
        return is_user_exist


async def set_user(tg_id, name, status):
    """
    Добавляет нового пользователя в таблицу Users.
    """
    async with async_session() as session:
        user = await session.scalar(select(User).where(
            User.tg_id == tg_id, 
            User.status == status
        ))

        if not user:
            session.add(User(
                tg_id=tg_id, 
                name=name, 
                status=status, 
                current_tooth_id=1
            ))
            await session.commit() 


async def get_user_current_tooth_id(tg_id):
    """
    Возвращает id последнего зуба, который разметил пользователь из 
    таблицы Users, и количество зубов в таблице Tooth.
    """
    async with async_session() as session:
        current_tooth_id = await session.scalar(
            select(User.current_tooth_id).where(
                User.tg_id == tg_id, 
                User.status == "Эксперт"
            )
        )
        teeth_num = await session.execute(
            select(func.count()).select_from(Tooth)
        )
        if current_tooth_id:
            return current_tooth_id, teeth_num.scalar()
        

async def set_user_current_tooth_id(tg_id, tooth_id):
    """
    Изменяет значение поля current_tooth_id
    """
    async with async_session() as session:
        await session.execute(update(User).where(
            User.tg_id == tg_id, 
            User.status == "Эксперт"
        ).values(current_tooth_id=tooth_id))
        await session.commit() 


async def get_tooth(tooth_id):
    """
    Возвращает изображения зуба по tooth_id, если такой имеется, 
    иначе возвращает False.
    """
    async with async_session() as session:
        tooth_files = await session.execute(
            select(Tooth.file_name, Tooth.cropped_file_name).where(
                Tooth.id == tooth_id)
        )
        if tooth_files:
            return tooth_files.first()
        else:
            return False
        

async def get_labels():
    """
    Возвращает значения из таблицы Labels
    """
    async with async_session() as session:
        return await session.scalars(select(Label))
    

async def get_recommendations():
    """
    Возвращает значения из таблицы Recommendations
    """
    async with async_session() as session:
        return await session.scalars(select(Recommendation))
    

async def add_label(label_name):
    """
    Добавляет новый класс разметки в таблицу Labels
    """
    async with async_session() as session:
        is_label_exist = await session.scalar(
            select(Label).where(Label.name == label_name)
        )

        if not is_label_exist:
            session.add(Label(name=label_name))
            await session.commit() 


async def add_xray(xray_path):
    """
    Добавляет новый снимок в таблицу Xrays
    """
    async with async_session() as session:
        is_xray_exist = await session.scalar(select(Xray).where(
            Xray.file_name == xray_path
        ))

        if not is_xray_exist:
            session.add(Xray(file_name=xray_path))
            await session.commit() 


async def add_teeth(teeth_dir, xray_name, xray_path):
    """
    Добавляет новые изображения зубов в таблицу Teeth
    """
    async with async_session() as session:
        xray_id = await session.scalar(select(Xray.id).where(
            Xray.file_name == xray_path
        ))
        teeth = os.listdir(os.path.join(teeth_dir, xray_name))
        print(type(teeth))
        print(teeth)
        for tooth in teeth:
            tooth_path = os.path.join(
                teeth_dir, 
                xray_name, 
                tooth, 
                tooth+'.png')
            cropped_tooth_path = os.path.join(
                teeth_dir, 
                xray_name, 
                tooth, 
                tooth+'-cropped.png')
            print(tooth_path)
            print(cropped_tooth_path)
            is_tooth_exist = await session.scalar(select(Tooth).where(
                Tooth.file_name == tooth_path
            ))
            if not is_tooth_exist:
                print(f"Зуб {tooth} добавлен")
                session.add(Tooth(file_name=tooth_path, 
                                  cropped_file_name=cropped_tooth_path,
                                  xray_id=xray_id))
        await session.commit() 


async def add_answer(tg_id, tooth_id, label_ids, rec_id):
    """
    Добавляет результаты разметки в таблицу Answers
    """
    async with async_session() as session:
        is_answer_exist = await session.scalar(select(Answer).where(
            Answer.tooth_id == tooth_id
        ))
        user_id = await session.scalar(select(User.id).where(
            User.tg_id == tg_id, 
            User.status == "Эксперт"
        ))
        if not is_answer_exist and user_id:
            session.add(Answer(
                user_id=user_id, 
                tooth_id=tooth_id, 
                label_ids=label_ids,
                recommendation_id=rec_id
            ))
            await session.commit()