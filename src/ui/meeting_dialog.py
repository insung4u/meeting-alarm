"""미팅 추가/수정 다이얼로그"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List

from ..core.meeting import Meeting


class MeetingDialog:
    def __init__(
        self,
        parent: tk.Tk,
        meeting: Optional[Meeting] = None,
        default_alert_minutes: int = 5,
        on_save: Optional[Callable[[Meeting], None]] = None
    ):
        self.parent = parent
        self.meeting = meeting
        self.default_alert_minutes = default_alert_minutes
        self.on_save = on_save
        self.result: Optional[Meeting] = None

        self.dialog = tk.Toplevel(parent)
        self._setup_dialog()

    def _setup_dialog(self) -> None:
        dialog = self.dialog
        dialog.title("미팅 추가" if self.meeting is None else "미팅 수정")
        dialog.transient(self.parent)
        dialog.grab_set()

        # 창 크기 및 위치
        width = 350
        height = 390
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        # 메인 프레임
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 미팅 이름
        ttk.Label(main_frame, text="미팅 이름:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        # 요일 선택
        ttk.Label(main_frame, text="요일:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        days_frame = ttk.Frame(main_frame)
        days_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        self.day_vars: List[tk.BooleanVar] = []
        day_names = ["월", "화", "수", "목", "금", "토", "일"]
        for i, day in enumerate(day_names):
            var = tk.BooleanVar()
            self.day_vars.append(var)
            cb = ttk.Checkbutton(days_frame, text=day, variable=var)
            cb.pack(side=tk.LEFT, padx=(0, 10))

        # 반복 여부
        self.repeat_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame, text="매주 반복", variable=self.repeat_var
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # 시간 선택
        ttk.Label(main_frame, text="시간:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        self.hour_var = tk.StringVar(value="09")
        self.minute_var = tk.StringVar(value="00")

        hour_spinbox = ttk.Spinbox(
            time_frame, from_=0, to=23, width=5,
            textvariable=self.hour_var, format="%02.0f"
        )
        hour_spinbox.pack(side=tk.LEFT)

        ttk.Label(time_frame, text=" : ").pack(side=tk.LEFT)

        minute_spinbox = ttk.Spinbox(
            time_frame, from_=0, to=59, width=5,
            textvariable=self.minute_var, format="%02.0f"
        )
        minute_spinbox.pack(side=tk.LEFT)

        # 알림 시간
        ttk.Label(main_frame, text="알림 (미팅 시작 전):").grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        alert_frame = ttk.Frame(main_frame)
        alert_frame.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        self.alert_var = tk.StringVar(value=str(self.default_alert_minutes))
        alert_spinbox = ttk.Spinbox(
            alert_frame, from_=1, to=60, width=5,
            textvariable=self.alert_var
        )
        alert_spinbox.pack(side=tk.LEFT)
        ttk.Label(alert_frame, text=" 분 전").pack(side=tk.LEFT)

        # 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(btn_frame, text="저장", command=self._on_save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="취소", command=self._on_cancel).pack(side=tk.LEFT)

        # 기존 미팅 데이터 로드
        if self.meeting:
            self._load_meeting_data()

        # 포커스
        self.name_entry.focus_set()

        # 엔터키로 저장
        dialog.bind("<Return>", lambda e: self._on_save())
        dialog.bind("<Escape>", lambda e: self._on_cancel())

    def _load_meeting_data(self) -> None:
        """기존 미팅 데이터를 폼에 로드"""
        if not self.meeting:
            return

        self.name_entry.insert(0, self.meeting.name)

        for day in self.meeting.days:
            self.day_vars[day].set(True)

        self.repeat_var.set(self.meeting.repeat)
        self.hour_var.set(f"{self.meeting.hour:02d}")
        self.minute_var.set(f"{self.meeting.minute:02d}")
        self.alert_var.set(str(self.meeting.alert_minutes))

    def _on_save(self) -> None:
        """저장 버튼 클릭"""
        # 유효성 검사
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("경고", "미팅 이름을 입력해주세요.", parent=self.dialog)
            self.name_entry.focus_set()
            return

        days = [i for i, var in enumerate(self.day_vars) if var.get()]
        if not days:
            messagebox.showwarning("경고", "요일을 선택해주세요.", parent=self.dialog)
            return

        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            alert_minutes = int(self.alert_var.get())

            if not (0 <= hour <= 23):
                raise ValueError("시간은 0-23 사이여야 합니다.")
            if not (0 <= minute <= 59):
                raise ValueError("분은 0-59 사이여야 합니다.")
            if not (1 <= alert_minutes <= 60):
                raise ValueError("알림 시간은 1-60분 사이여야 합니다.")

        except ValueError as e:
            messagebox.showwarning("경고", str(e), parent=self.dialog)
            return

        repeat = self.repeat_var.get()

        # 미팅 생성/수정
        if self.meeting:
            self.meeting.name = name
            self.meeting.days = days
            self.meeting.hour = hour
            self.meeting.minute = minute
            self.meeting.alert_minutes = alert_minutes
            self.meeting.repeat = repeat
            self.result = self.meeting
        else:
            self.result = Meeting(
                name=name,
                days=days,
                hour=hour,
                minute=minute,
                alert_minutes=alert_minutes,
                repeat=repeat
            )

        if self.on_save:
            self.on_save(self.result)

        self.dialog.destroy()

    def _on_cancel(self) -> None:
        """취소 버튼 클릭"""
        self.dialog.destroy()
