from database.models import async_session 
from database.models import User, Label, Xray, Tooth, Answer
from sqlalchemy import select, update
import os


async def set_user(tg_id, name, status):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id, User.status == status))

        if not user:
            session.add(User(tg_id=tg_id, name=name, status=status, current_tooth_id=1))
            await session.commit() 


async def get_user_current_tooth_id(tg_id):
    async with async_session() as session:
        current_tooth_id = await session.scalar(select(User.current_tooth_id).where(User.tg_id == tg_id, User.status == "Эксперт"))
        if current_tooth_id:
            return current_tooth_id
        

async def set_user_current_tooth_id(tg_id, tooth_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id, User.status == "Эксперт").values(current_tooth_id=tooth_id))
        await session.commit() 



async def get_tooth(tooth_id):
    async with async_session() as session:
        tooth_file_path = await session.scalar(select(Tooth.file_name).where(Tooth.id == tooth_id))
        if tooth_file_path:
            return tooth_file_path
        

async def get_labels():
    async with async_session() as session:
        return await session.scalars(select(Label))
    

async def add_label(label_name):
    async with async_session() as session:
        is_label_exist = await session.scalar(select(Label).where(Label.name == label_name))

        if not is_label_exist:
            session.add(Label(name=label_name))
            await session.commit() 


async def add_xray(xray_path):
    async with async_session() as session:
        is_xray_exist = await session.scalar(select(Xray).where(Xray.file_name == xray_path))

        if not is_xray_exist:
            session.add(Xray(file_name=xray_path))
            await session.commit() 


async def add_teeth(teeth_dir, xray_name, xray_path):
    async with async_session() as session:
        xray_id = await session.scalar(select(Xray.id).where(Xray.file_name == xray_path))
        tooth_files = os.listdir(os.path.join(teeth_dir, xray_name))
        for tooth_file in tooth_files:
            tooth_path = os.path.join(teeth_dir, xray_name, tooth_file)

            is_tooth_exist = await session.scalar(select(Tooth).where(Tooth.file_name == tooth_path))
            if not is_tooth_exist:
                print(f"Зуб {tooth_file} добавлен")
                session.add(Tooth(file_name=tooth_path, xray_id=xray_id))
        await session.commit() 


async def add_answer(tg_id, tooth_id, label_id):
    async with async_session() as session:
        is_answer_exist = await session.scalar(select(Answer).where(Answer.tooth_id == tooth_id))
        user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id, User.status == "Эксперт"))
        if not is_answer_exist and user_id:
            session.add(Answer(user_id=user_id, 
                               tooth_id=tooth_id, 
                               label_id=label_id))
            await session.commit()