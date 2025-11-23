from database.models import async_session 
from database.models import (
    User, 
    Condition, 
    Xray, 
    Tooth, 
    Answer, 
    Recommendation,
    Term,
    Pathology
)
from sqlalchemy import select, update, func, desc
import os


"""Запросы в БД"""


async def check_user(tg_id, role):
    """
    Возвращает True если существует пользователь с указанным tg_id, role 
    в таблице Users, иначе возвращает False
    """
    async with async_session() as session:
        user_status =  await session.scalar(select(User.status).where(
            User.tg_id == tg_id, 
            User.role == role
        ))   
        return user_status


async def set_user(tg_id, name, role, status=None):
    """
    Добавляет нового пользователя в таблицу Users.
    """
    async with async_session() as session:
        user = await session.scalar(select(User).where(
            User.tg_id == tg_id, 
            User.role == role
        ))
        if not user:
            session.add(User(
                tg_id=tg_id, 
                name=name, 
                role=role, 
                status=status
            ))
            await session.commit()


async def get_tooth_id(user_id, user_status):
    """
    Возвращает id последнего зуба, который разметил пользователь из 
    таблицы Users, и количество зубов в таблице Tooth.
    """
    async with async_session() as session:
        if user_status == "Преподаватель":
            result = await session.scalars(
                select(Tooth.id).order_by(desc(Tooth.complexity), Tooth.id))
        else:
            result = await session.scalars(select(Tooth.id)
                .where(Tooth.complexity == 0)
                .order_by(desc(Tooth.complexity), Tooth.id))
        teeth_ids = result.all()
        teeth_num = len(teeth_ids)

        if not teeth_ids:
            return False, teeth_num

        aa_teeth_ids = await session.scalars(
            select(Answer.tooth_id).where(
                Answer.user_id == user_id)
        )
        aa_teeth_ids = (aa_teeth_ids.all())

        if aa_teeth_ids:
            aa_teeth_ids = set(aa_teeth_ids)
            stack = [item for item in teeth_ids if item not in aa_teeth_ids]

            if not stack:
                return False, teeth_num
            return stack[0], teeth_num
        else:
            return teeth_ids[0], teeth_num


async def get_tooth(tooth_id):
    """
    Возвращает изображения зуба и его сложность по tooth_id, 
    если такой имеется, иначе возвращает False.
    """
    async with async_session() as session:
        teeth_files = await session.execute(
            select(Tooth.file_name, 
                   Tooth.cropped_file_name, 
                   Tooth.complexity).where(Tooth.id == tooth_id)
        )
        tooth_files = teeth_files.first()
        if tooth_files:
            return tooth_files[:2], tooth_files[2]
        else:
            return False, False
        

async def get_labels(table_model_name='labels'):
    """Возвращает значения разметки из указанной таблицы."""
    model_map = {
        'conditions': Condition,
        'recommendations': Recommendation,
        'pathologies': Pathology,
        'terms': Term,
    }
    table_model = table_model_name if not isinstance(table_model_name, str) \
        else model_map.get(table_model_name)
    async with async_session() as session:
        return await session.scalars(select(table_model))
    

async def get_label_name(table_name, label_id):
    """Возвращает название класса разметки по ID"""
    model_map = {
        'conditions': Condition,
        'recommendations': Recommendation,
        'pathologies': Pathology,
        'terms': Term,
    }
    table_model = table_name if not isinstance(table_name, str) \
        else model_map.get(table_name)
    async with async_session() as session:
        label_name = await session.scalar(
            select(table_model.name).where(table_model.id==label_id)
        )
        return label_name
    

# async def add_label(label_name):
#     """Добавляет новый класс разметки в таблицу Labels"""
#     async with async_session() as session:
#         is_label_exist = await session.scalar(
#             select(Condition).where(Condition.name == label_name)
#         )

#         if not is_label_exist:
#             session.add(Condition(name=label_name))
#             await session.commit() 


async def add_xray(xray_path):
    """Добавляет новый снимок в таблицу Xrays"""
    async with async_session() as session:
        is_xray_exist = await session.scalar(select(Xray).where(
            Xray.file_name == xray_path
        ))

        if not is_xray_exist:
            session.add(Xray(file_name=xray_path))
            await session.commit() 


async def add_teeth(teeth_dir, xray_name, xray_path):
    """Добавляет новые изображения зубов в таблицу Teeth"""
    async with async_session() as session:
        xray_id = await session.scalar(select(Xray.id).where(
            Xray.file_name == xray_path
        ))
        teeth = os.listdir(os.path.join(teeth_dir, xray_name))
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
            is_tooth_exist = await session.scalar(select(Tooth).where(
                Tooth.file_name == tooth_path
            ))
            if not is_tooth_exist:
                # print(f"Зуб {tooth} добавлен")
                session.add(Tooth(file_name=tooth_path, 
                                  cropped_file_name=cropped_tooth_path,
                                  xray_id=xray_id))
        await session.commit() 


async def add_answer(tg_id, tooth_id, condition_id, pathology_id, rec_id, term_id):
    """Добавляет результаты разметки в таблицу Answers"""
    async with async_session() as session:
        is_answer_exist = await session.scalar(select(Answer).where(
            Answer.tooth_id == tooth_id,
            Answer.user_id == tg_id
        ))
        if not is_answer_exist:
            session.add(Answer(
                user_id=tg_id, 
                tooth_id=tooth_id, 
                condition_id=condition_id,
                pathology_id=pathology_id,
                rec_id=rec_id,
                term_id=term_id
            ))
            await session.commit()


async def change_tooth_complexity(tooth_id, complexity):
    """Изменяет поле complexity в таблице Teeth"""
    async with async_session() as session:
        await session.execute(update(Tooth).where(
            Tooth.id == tooth_id, 
        ).values(complexity=complexity))
        await session.commit() 
    

async def get_answers_count_by_user():
    """
    Возвращает количество ответов для каждого пользователя 
    с именем пользователя и статусом, а также их прогресс
    """
    async with async_session() as session:
        subquery = select(Answer.user_id, func.count(Answer.id).label('count'))\
            .group_by(Answer.user_id)\
            .subquery()
            
        experts = await session.execute(
            select(User.name, User.status, subquery.c.count)
            .join(subquery, User.tg_id == subquery.c.user_id)
            .where(User.status.in_(['Преподаватель', 'Ординатор']))
            .order_by(User.status)
        )
        experts = experts.all()

        total_teeth = await session.scalars(
                    select(Tooth).order_by(desc(Tooth.complexity), Tooth.id))
        total_teeth = len(total_teeth.all())
    
        normal_teeth = await session.scalars(select(Tooth)
                    .where(Tooth.complexity == 0)
                    .order_by(desc(Tooth.complexity), Tooth.id))
        normal_teeth = len(normal_teeth.all())

        if total_teeth < 1 or normal_teeth < 1:
            return False, False
        
        progress = []
        for expert in experts:
            if expert[1] == "Преподаватель":
                progress.append([int(expert[2] / total_teeth * 10), total_teeth])
            else:
                progress.append([int(expert[2] / normal_teeth * 10), normal_teeth])
        return experts, progress