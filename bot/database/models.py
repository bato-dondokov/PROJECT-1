from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, ForeignKey


engine = create_async_engine(url='sqlite+aiosqlite:///bot/db.sqlite3')
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(255))  
    status: Mapped[str] = mapped_column(String(25))  
    current_tooth_id: Mapped[int] = mapped_column(ForeignKey('teeth.id'))


class Label(Base):
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))


class Xray(Base):
    __tablename__ = "xrays"
    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255))   


class Tooth(Base):
    __tablename__ = "teeth"
    id: Mapped[int] = mapped_column(primary_key=True)
    xray_id: Mapped[int] = mapped_column(ForeignKey('xrays.id'))
    file_name: Mapped[str] = mapped_column(String(255))    


class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tooth_id: Mapped[int] = mapped_column(ForeignKey('teeth.id'))
    label_ids: Mapped[str] = mapped_column(String(255)) 
    # TODO: add datetime


async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)