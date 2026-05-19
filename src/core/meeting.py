"""미팅 데이터 모델"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import uuid


@dataclass
class Meeting:
    name: str
    days: List[int]  # 0=월, 1=화, 2=수, 3=목, 4=금, 5=토, 6=일
    hour: int
    minute: int
    alert_minutes: int = 5  # 미팅 시작 n분 전 알림
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    enabled: bool = True
    repeat: bool = True  # True=매주 반복, False=1회
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD (repeat 시 종료일)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Meeting":
        data.setdefault("repeat", True)
        data.setdefault("start_date", None)
        data.setdefault("end_date", None)
        return cls(**data)

    def get_time_str(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"

    def get_days_str(self) -> str:
        day_names = ["월", "화", "수", "목", "금", "토", "일"]
        return ", ".join(day_names[d] for d in sorted(self.days))
