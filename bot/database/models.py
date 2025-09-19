from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    AsyncAttrs, 
    async_sessionmaker, 
    create_async_engine
)
from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy import select
from config import DEFAULT_RECOMMENDATIONS, DEFAULT_LABELS


"""
Модели таблиц БД
"""


engine = create_async_engine(url='sqlite+aiosqlite:///bot/db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    """
    Модель таблицы для пользователей.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(255))  
    status: Mapped[str] = mapped_column(String(25))  
    current_tooth_id: Mapped[int] = mapped_column(ForeignKey('teeth.id'))


class Label(Base):
    """
    Модель таблицы для классов разметки.
    """
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Recommendation(Base):
    """
    Модель таблицы для рекомендаций к лечению.
    """
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Xray(Base):
    """
    Модель таблицы для снимков.
    """
    __tablename__ = "xrays"
    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255))   


class Tooth(Base):
    """
    Модель таблицы для изображений зубов.
    """
    __tablename__ = "teeth"
    id: Mapped[int] = mapped_column(primary_key=True)
    xray_id: Mapped[int] = mapped_column(ForeignKey('xrays.id'))
    file_name: Mapped[str] = mapped_column(String(255))    
    cropped_file_name: Mapped[str] = mapped_column(String(255))    


class Answer(Base):
    """
    Модель таблицы для результатов разметки.
    """
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tooth_id: Mapped[int] = mapped_column(ForeignKey('teeth.id'))
    label_ids: Mapped[str] = mapped_column(String(255)) 
    recommendation_id: Mapped[int] = mapped_column(ForeignKey('recommendations.id'))


async def async_main():
    """
    Добавляет в таблицы Labels и Recommendations значения из конфига.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        is_recs_exist = await session.scalar(select(Recommendation).limit(1))
        is_labels_exist = await session.scalar(select(Label).limit(1))

        if not is_labels_exist:
            labels = DEFAULT_LABELS
            for label_id, label_name in labels.items():
                session.add(Label(id=label_id, name=label_name))
            await session.commit() 
            print('Default labels added')

        if not is_recs_exist:
            recs = DEFAULT_RECOMMENDATIONS
            for rec_id, rec_name in recs.items():
                session.add(Recommendation(id=rec_id, name=rec_name))
            await session.commit() 
            print('Default recommendations added')