"""JSON 파일 저장/로드"""
import json
import os
from typing import List, Dict, Any
from pathlib import Path

from .meeting import Meeting


def get_data_dir() -> Path:
    """데이터 저장 디렉토리 반환"""
    app_data = Path(os.environ.get("APPDATA", Path.home()))
    data_dir = app_data / "MeetingAlarm"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_meetings_file() -> Path:
    return get_data_dir() / "meetings.json"


def get_settings_file() -> Path:
    return get_data_dir() / "settings.json"


def load_meetings() -> List[Meeting]:
    """미팅 목록 로드"""
    file_path = get_meetings_file()
    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Meeting.from_dict(m) for m in data]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def save_meetings(meetings: List[Meeting]) -> None:
    """미팅 목록 저장"""
    file_path = get_meetings_file()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([m.to_dict() for m in meetings], f, ensure_ascii=False, indent=2)


def load_settings() -> Dict[str, Any]:
    """설정 로드"""
    file_path = get_settings_file()
    default_settings = {
        "sound_enabled": True,
        "default_alert_minutes": 5,
        "autostart": False,
    }

    if not file_path.exists():
        return default_settings

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**default_settings, **data}
    except (json.JSONDecodeError, KeyError, TypeError):
        return default_settings


def save_settings(settings: Dict[str, Any]) -> None:
    """설정 저장"""
    file_path = get_settings_file()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
