"""메인 애플리케이션 클래스"""
import tkinter as tk
import sys
import os
from typing import List, Optional

from .core.meeting import Meeting
from .core.storage import load_meetings, save_meetings, load_settings
from .core.scheduler import Scheduler
from .ui.main_window import MainWindow
from .ui.alert_window import AlertWindow
from .tray.tray_icon import TrayIcon


class MeetingAlarmApp:
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.main_window: Optional[MainWindow] = None
        self.tray_icon: Optional[TrayIcon] = None
        self.scheduler: Optional[Scheduler] = None
        self.meetings: List[Meeting] = []
        self.settings = {}
        self.alert_windows: List[AlertWindow] = []

    def run(self) -> None:
        """애플리케이션 실행"""
        # 데이터 로드
        self.meetings = load_meetings()
        self.settings = load_settings()

        # Tkinter 초기화
        self.root = tk.Tk()

        # 스케줄러 초기화
        self.scheduler = Scheduler(
            on_alert=self._on_alert,
            on_meeting_disabled=self._on_meeting_disabled,
        )
        self.scheduler.set_meetings(self.meetings)
        self.scheduler.start()

        # 메인 윈도우 생성
        self.main_window = MainWindow(
            self.root,
            self.meetings,
            on_meeting_change=self._on_meeting_change,
            on_close=self._on_window_close
        )

        # 시스템 트레이 아이콘 생성
        icon_path = self._get_icon_path()
        self.tray_icon = TrayIcon(
            on_open=self._show_main_window,
            on_quit=self._quit_app,
            icon_path=icon_path
        )
        self.tray_icon.start()

        # 창 닫기 버튼 처리 (트레이로 최소화)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # 상태 업데이트
        self._update_status()

        # 메인 루프 시작
        self.root.mainloop()

    def _get_icon_path(self) -> Optional[str]:
        """아이콘 파일 경로 반환"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(__file__))

        icon_path = os.path.join(base_path, "assets", "icon.ico")
        if os.path.exists(icon_path):
            return icon_path
        return None

    def _on_alert(self, meeting: Meeting) -> None:
        if self.root:
            self.root.after(0, lambda: self._show_alert(meeting))

    def _on_meeting_disabled(self, _: Meeting) -> None:
        """1회 미팅 알림 후 비활성화 처리 (스케줄러 스레드에서 호출)"""
        if self.root:
            self.root.after(0, self._handle_meeting_disabled)

    def _handle_meeting_disabled(self) -> None:
        save_meetings(self.meetings)
        if self.main_window:
            self.main_window.refresh_meetings(self.meetings)

    def _show_alert(self, meeting: Meeting) -> None:
        """알림 창 표시"""
        play_sound = self.settings.get("sound_enabled", True)

        def on_close():
            pass

        alert = AlertWindow(meeting, on_close=on_close, play_sound=play_sound)
        alert.show(self.root)
        self.alert_windows.append(alert)

    def _on_meeting_change(self, meetings: List[Meeting]) -> None:
        """미팅 목록 변경 시 호출"""
        self.meetings = meetings
        save_meetings(meetings)

        if self.scheduler:
            self.scheduler.set_meetings(meetings)

        self._update_status()

    def _on_window_close(self) -> None:
        """창 닫기 버튼 클릭 시"""
        if self.main_window:
            self.main_window.hide()

    def _show_main_window(self) -> None:
        """메인 창 표시"""
        if self.main_window:
            self.main_window.show()

    def _quit_app(self) -> None:
        """애플리케이션 종료"""
        # 스케줄러 중지
        if self.scheduler:
            self.scheduler.stop()

        # 트레이 아이콘 중지
        if self.tray_icon:
            self.tray_icon.stop()

        # Tkinter 종료
        if self.root:
            self.root.quit()
            self.root.destroy()

    def _update_status(self) -> None:
        """상태 업데이트"""
        if self.scheduler and self.main_window:
            next_alert = self.scheduler.get_next_alert_info()
            if next_alert:
                self.main_window.update_status(next_alert)
            else:
                self.main_window.update_status(f"등록된 미팅: {len(self.meetings)}개")

        if self.tray_icon:
            self.tray_icon.update_tooltip(f"회의 알림 - {len(self.meetings)}개 미팅")
