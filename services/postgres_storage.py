from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from config.env_vars import config
from utils.logger import get_logger


logger = get_logger("postgres_storage", level=config.LOG_LEVEL)


engine = create_engine(config.DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
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


# Optional table for future swap requests
class ShiftSwapORM(Base):
    __tablename__ = "shift_swap"
    id = Column(Integer, primary_key=True)
    region = Column(String, nullable=False)
    from_member = Column(Integer, ForeignKey("sre_member.id"))
    to_member = Column(Integer, ForeignKey("sre_member.id"))
    requested_at = Column(DateTime, server_default=text("now()"))
    approved = Column(Boolean, default=False)


# Create tables if they don't exist
Base.metadata.create_all(engine)


class PostgresStorage:
    """High-level API matching the old RedisStorage interface but backed by PostgreSQL."""

    def __init__(self):
        self._session: Session = SessionLocal()

    # --------------- member helpers ---------------
    def _get_or_create_member(self, slack_id: str, name: str, region: str) -> SREMemberORM:
        member = self._session.query(SREMemberORM).filter_by(slack_id=slack_id).one_or_none()
        if not member:
            member = SREMemberORM(slack_id=slack_id, name=name, region=region)
            self._session.add(member)
            self._session.commit()
        return member

    def get_oncall(self, region: str) -> Optional[str]:
        oc = self._session.query(OnCallORM).filter_by(region=region).one_or_none()
        return oc.member.slack_id if oc and oc.member else None

    def set_oncall(self, region: str, slack_id: str, name: str = "", region_name: str = ""):
        """Set current oncall; create member/oncall row if absent."""
        member = self._get_or_create_member(slack_id, name or slack_id, region_name or region)
        oc = self._session.query(OnCallORM).filter_by(region=region).one_or_none()
        if not oc:
            oc = OnCallORM(region=region, member=member, rotation_idx=0)
            self._session.add(oc)
        else:
            oc.member = member
            oc.since = datetime.utcnow()
        self._session.commit()

    # rotation index helpers
    def get_rotation_idx(self, region: str) -> int:
        oc = self._session.query(OnCallORM).filter_by(region=region).one_or_none()
        return oc.rotation_idx if oc else -1

    def set_rotation_idx(self, region: str, idx: int):
        oc = self._session.query(OnCallORM).filter_by(region=region).one_or_none()
        if not oc:
            oc = OnCallORM(region=region, rotation_idx=idx)
            self._session.add(oc)
        else:
            oc.rotation_idx = idx
        self._session.commit()

    # history helpers
    def push_history(self, region: str, slack_id: str):
        member = self._get_or_create_member(slack_id, slack_id, region)
        hist = RotationHistoryORM(region=region, member=member)
        self._session.add(hist)
        self._session.commit()

    def lrange(self, region: str, limit: int = 1) -> List[str]:
        rows = (
            self._session.query(RotationHistoryORM)
            .filter_by(region=region)
            .order_by(RotationHistoryORM.rotated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            json.dumps({
                "member_id": r.member.slack_id,
                "timestamp": r.rotated_at.isoformat(),
            })
            for r in rows
        ]
