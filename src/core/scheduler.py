"""알림 스케줄러"""
import threading
from datetime import datetime, timedelta
from typing import List, Callable, Optional
import time

from .meeting import Meeting


class Scheduler:
    def __init__(
        self,
        on_alert: Callable[[Meeting], None],
        on_meeting_disabled: Optional[Callable[[Meeting], None]] = None,
    ):
        self.meetings: List[Meeting] = []
        self.on_alert = on_alert
        self.on_meeting_disabled = on_meeting_disabled
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._alerted: set = set()  # 이미 알림을 보낸 (meeting_id, alert_time) 쌍

    def set_meetings(self, meetings: List[Meeting]) -> None:
        self.meetings = meetings

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        while self._running:
            self._check_alerts()
            time.sleep(10)  # 10초마다 체크

    def _check_alerts(self) -> None:
        now = datetime.now()
        current_day = now.weekday()  # 0=월요일

        # 매일 자정에 알림 기록 초기화
        if now.hour == 0 and now.minute == 0:
            self._alerted.clear()

        for meeting in self.meetings:
            if not meeting.enabled:
                continue
            if current_day not in meeting.days:
                continue

            # 미팅 시간
            meeting_time = now.replace(
                hour=meeting.hour,
                minute=meeting.minute,
                second=0,
                microsecond=0
            )

            # 알림 시간 (미팅 시작 n분 전)
            alert_time = meeting_time - timedelta(minutes=meeting.alert_minutes)

            # 알림 키 (오늘 날짜 + 미팅 ID)
            alert_key = (meeting.id, now.date().isoformat())

            # 현재 시간이 알림 시간 범위 내인지 확인 (±30초)
            time_diff = (now - alert_time).total_seconds()

            if 0 <= time_diff <= 30 and alert_key not in self._alerted:
                self._alerted.add(alert_key)
                self.on_alert(meeting)
                if not meeting.repeat:
                    meeting.enabled = False
                    if self.on_meeting_disabled:
                        self.on_meeting_disabled(meeting)

    def get_next_alert_info(self) -> Optional[str]:
        """다음 알림 정보 반환"""
        now = datetime.now()
        current_day = now.weekday()

        next_alerts = []

        for meeting in self.meetings:
            if not meeting.enabled:
                continue

            for day_offset in range(7):
                check_day = (current_day + day_offset) % 7
                if check_day not in meeting.days:
                    continue

                # 해당 요일의 알림 시간 계산
                days_ahead = day_offset
                meeting_datetime = now.replace(
                    hour=meeting.hour,
                    minute=meeting.minute,
                    second=0,
                    microsecond=0
                ) + timedelta(days=days_ahead)

                alert_datetime = meeting_datetime - timedelta(minutes=meeting.alert_minutes)

                if alert_datetime > now:
                    next_alerts.append((alert_datetime, meeting))
                    break

        if not next_alerts:
            return None

        next_alerts.sort(key=lambda x: x[0])
        alert_time, meeting = next_alerts[0]

        return f"다음 알림: {meeting.name} - {alert_time.strftime('%m/%d %H:%M')}"
