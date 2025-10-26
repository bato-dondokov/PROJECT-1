from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    AsyncAttrs, 
    async_sessionmaker, 
    create_async_engine
)
from sqlalchemy import BigInteger, String, ForeignKey, Boolean
from sqlalchemy import select
from config import (
    DEFAULT_CONDITIONS, 
    DEFAULT_PATHOLOGIES,
    DEFAULT_RECOMMENDATIONS,
    DEFAULT_TERMS
)


"""Модели таблиц БД"""


engine = create_async_engine(url='sqlite+aiosqlite:///bot/db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    """Модель таблицы для пользователей."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(255))  
    role: Mapped[str] = mapped_column(String(25))
    status: Mapped[str] = mapped_column(String(25))  


class Condition(Base):
    """Модель таблицы для исходного состояния зубов."""
    __tablename__ = "conditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Pathology(Base):
    """Модель таблицы для патологий."""
    __tablename__ = "pathologies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Recommendation(Base):
    """Модель таблицы для рекомендаций к лечению."""
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Term(Base):
    """Модель таблицы для сроков обращения."""
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Xray(Base):
    """Модель таблицы для снимков."""
    __tablename__ = "xrays"
    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255))   


class Tooth(Base):
    """Модель таблицы для изображений зубов."""
    __tablename__ = "teeth"
    id: Mapped[int] = mapped_column(primary_key=True)
    complexity: Mapped[bool] = mapped_column(Boolean, 
                                             default=False, 
                                             nullable=False)
    xray_id: Mapped[int] = mapped_column(ForeignKey('xrays.id'))
    file_name: Mapped[str] = mapped_column(String(255))    
    cropped_file_name: Mapped[str] = mapped_column(String(255))    


class Answer(Base):
    """Модель таблицы для результатов разметки."""
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    tooth_id: Mapped[int] = mapped_column(ForeignKey('teeth.id'))
    condition_id: Mapped[int] = mapped_column(ForeignKey('conditions.id'))
    pathology_id: Mapped[int] = mapped_column(ForeignKey('pathologies.id'))
    rec_id: Mapped[int] = mapped_column(ForeignKey('recommendations.id'))
    term_id: Mapped[int] = mapped_column(ForeignKey('terms.id'))


async def async_main():
    """Добавляет в таблицы для разметки значения из конфига."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        is_recs_exist = await session.scalar(select(Recommendation).limit(1))
        is_pathologies_exist = await session.scalar(select(Pathology).limit(1))
        is_conditions_exist = await session.scalar(select(Condition).limit(1))
        is_terms_exist = await session.scalar(select(Term).limit(1))

        if not is_conditions_exist:
            conditions = DEFAULT_CONDITIONS
            for condition in conditions:
                session.add(Condition(name=condition))
            await session.commit() 
            print('Default conditions added')
        
        if not is_pathologies_exist:
            pathologies = DEFAULT_PATHOLOGIES
            for pathology in pathologies:
                session.add(Pathology(name=pathology))
            await session.commit() 
            print('Default pathologies added')

        if not is_recs_exist:
            recs = DEFAULT_RECOMMENDATIONS
            for rec in recs:
                session.add(Recommendation(name=rec))
            await session.commit() 
            print('Default recommendations added')
        
        if not is_terms_exist:
            terms = DEFAULT_TERMS
            for term in terms:
                session.add(Term(name=term))
            await session.commit() 
            print('Default terms added')