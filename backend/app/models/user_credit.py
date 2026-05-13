from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


class UserCredit(Base):
    __tablename__ = "user_credits"
    __table_args__ = (
        UniqueConstraint("user_id", "type", name="uq_user_credits_user_id_type"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Integer, nullable=False, default=0, server_default="0", index=True)
    balance = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="credit_accounts")
