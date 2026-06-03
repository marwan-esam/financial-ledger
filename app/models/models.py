from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.db import database
import datetime

# The Account Table
class Account(database.Base):
  __tablename__ = "accounts"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  owner_name: Mapped[str] = mapped_column(index=True)
  balance: Mapped[float] = mapped_column(default=0.0)


# The Transaction Table
class Transaction(database.Base):
  __tablename__ = "transactions"

  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  amount: Mapped[float] = mapped_column()
  timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

  # Foreign keys
  sender_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
  receiver_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))


database.Base.metadata.create_all(bind=database.engine)