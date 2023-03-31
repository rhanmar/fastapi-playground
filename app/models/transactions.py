from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base


class Transaction(Base):
    """
    Транзакция.

    """

    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="transactions")
    created_at = Column(DateTime, default=datetime.now)
    amount = Column(Float, info={"verbose_name": "Сумма средств"})
    order_id = Column(String, info={"verbose_name": "ID Заказа"})
    service_id = Column(String, info={"verbose_name": "ID Услуги"})
