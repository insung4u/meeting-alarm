"""알림 팝업 창"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ..core.meeting import Meeting


class AlertWindow:
    def __init__(self, meeting: Meeting, on_close: Optional[Callable] = None, play_sound: bool = True):
        self.meeting = meeting
        self.on_close = on_close
        self.play_sound = play_sound
        self.window: Optional[tk.Toplevel] = None

    def show(self, parent: Optional[tk.Tk] = None) -> None:
        """알림 창 표시"""
        if self.window is not None:
            return

        # 소리 재생
        if self.play_sound:
            from ..utils.sound import play_alert_sound
            play_alert_sound()

        # 새 창 생성
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()

        self._setup_window()

    def _setup_window(self) -> None:
        win = self.window
        win.title("회의 알림")

        # 최상단 표시 설정
        win.attributes("-topmost", True)
        win.lift()
        win.focus_force()

        # 창 크기 및 위치
        width = 400
        height = 200
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 3  # 화면 상단 1/3 위치

        win.geometry(f"{width}x{height}+{x}+{y}")
        win.resizable(False, False)

        # 배경색
        win.configure(bg="#FF6B6B")

        # 메인 프레임
        main_frame = tk.Frame(win, bg="#FF6B6B", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 알림 아이콘/제목
        title_label = tk.Label(
            main_frame,
            text="🔔 회의 알림",
            font=("맑은 고딕", 16, "bold"),
            fg="white",
            bg="#FF6B6B"
        )
        title_label.pack(pady=(0, 10))

        # 미팅 이름
        name_label = tk.Label(
            main_frame,
            text=self.meeting.name,
            font=("맑은 고딕", 20, "bold"),
            fg="white",
            bg="#FF6B6B"
        )
        name_label.pack(pady=(0, 5))

        # 시간 정보
        time_text = f"{self.meeting.alert_minutes}분 후 시작 ({self.meeting.get_time_str()})"
        time_label = tk.Label(
            main_frame,
            text=time_text,
            font=("맑은 고딕", 14),
            fg="white",
            bg="#FF6B6B"
        )
        time_label.pack(pady=(0, 15))

        # 확인 버튼
        confirm_btn = tk.Button(
            main_frame,
            text="확인",
            font=("맑은 고딕", 12, "bold"),
            width=15,
            height=1,
            bg="white",
            fg="#FF6B6B",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_confirm
        )
        confirm_btn.pack()

        # 창 닫기 이벤트
        win.protocol("WM_DELETE_WINDOW", self._on_confirm)

        # 주기적으로 최상단 유지
        self._keep_on_top()

    def _keep_on_top(self) -> None:
        """창을 최상단으로 유지"""
        if self.window and self.window.winfo_exists():
            self.window.attributes("-topmost", True)
            self.window.lift()
            self.window.after(1000, self._keep_on_top)  # 1초마다 반복

    def _on_confirm(self) -> None:
        """확인 버튼 클릭"""
        if self.window:
            self.window.destroy()
            self.window = None
        if self.on_close:
            self.on_close()
