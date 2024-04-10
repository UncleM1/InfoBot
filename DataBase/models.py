from sqlalchemy import Text, String, Float, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    time_created:Mapped[DateTime] = mapped_column(DateTime,default=func.now(), )
    time_updated:Mapped[DateTime] = mapped_column(DateTime,default=func.now(), onupdate=func.now() )

class Product(Base):
    __tablename__ = "product"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name:Mapped[str] = mapped_column(String(150),nullable=False)
    description:Mapped[str] = mapped_column(Text)
    price:Mapped[float] = mapped_column(Float(asdecimal=True),nullable=False)
    # order:Mapped[dict] = mapped_column(nullable=False)
    #image: Mapped[float] = mapped_column(String(150))



class Customer(Base):
    __tablename__ = "customer"

    id:Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    user_id:Mapped[int] = mapped_column(nullable=False)
    first_name:Mapped[str] = mapped_column(String(15),nullable=False)
    phone_number:Mapped[str] = mapped_column(String(20),nullable=True)
    # user_active:Mapped[int] = mapped_column(default=1, nullable=False)