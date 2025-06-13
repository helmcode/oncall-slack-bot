from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.orm import declarative_base, relationship
from utils.logger import get_logger
from config.env_vars import config

logger = get_logger(__name__, level=config.LOG_LEVEL)

Base = declarative_base()

class SREMemberORM(Base):
    __tablename__ = "sre_member"
    id = Column(Integer, primary_key=True)
    slack_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)

    rotations = relationship("RotationHistoryORM", back_populates="member")

class OnCallORM(Base):
    __tablename__ = "oncall"
    region = Column(String, primary_key=True)
    member_id = Column(Integer, ForeignKey("sre_member.id"))
    since = Column(DateTime, nullable=False, server_default=text("now()"))
    rotation_idx = Column(Integer, nullable=False, server_default=text("0"))

    member = relationship("SREMemberORM")

class RotationHistoryORM(Base):
    __tablename__ = "rotation_history"
    id = Column(Integer, primary_key=True)
    region = Column(String, nullable=False)
    member_id = Column(Integer, ForeignKey("sre_member.id"))
    rotated_at = Column(DateTime, nullable=False, server_default=text("now()"))

    member = relationship("SREMemberORM", back_populates="rotations")

class ShiftSwapORM(Base):
    __tablename__ = "shift_swap"
    id = Column(Integer, primary_key=True)
    region = Column(String, nullable=False)
    from_member = Column(Integer, ForeignKey("sre_member.id"))
    to_member = Column(Integer, ForeignKey("sre_member.id"))
    requested_at = Column(DateTime, server_default=text("now()"))
    approved = Column(Boolean, default=False)
