"""미팅 추가/수정 다이얼로그"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from datetime import date as dt_date

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

        self._saved_start_date: Optional[str] = None
        self._saved_end_date: Optional[str] = None
        self._get_start_date: Optional[Callable[[], str]] = None
        self._get_end_date: Optional[Callable[[], str]] = None

        self.dialog = tk.Toplevel(parent)
        self._setup_dialog()

    def _setup_dialog(self) -> None:
        dialog = self.dialog
        dialog.title("미팅 추가" if self.meeting is None else "미팅 수정")
        dialog.transient(self.parent)
        dialog.grab_set()

        width = 370
        height = 470
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)

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
            ttk.Checkbutton(days_frame, text=day, variable=var).pack(side=tk.LEFT, padx=(0, 10))

        # 반복 여부
        self.repeat_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main_frame, text="매주 반복", variable=self.repeat_var
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))

        # 날짜 섹션 (repeat 여부에 따라 동적 변경)
        self.date_container = ttk.Frame(main_frame)
        self.date_container.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        self.repeat_var.trace_add("write", lambda *_: self._rebuild_date_widgets())
        self._rebuild_date_widgets()

        # 시간 선택
        ttk.Label(main_frame, text="시간:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        self.hour_var = tk.StringVar(value="09")
        self.minute_var = tk.StringVar(value="00")

        ttk.Spinbox(
            time_frame, from_=0, to=23, width=5,
            textvariable=self.hour_var, format="%02.0f"
        ).pack(side=tk.LEFT)
        ttk.Label(time_frame, text=" : ").pack(side=tk.LEFT)
        ttk.Spinbox(
            time_frame, from_=0, to=59, width=5,
            textvariable=self.minute_var, format="%02.0f"
        ).pack(side=tk.LEFT)

        # 알림 시간
        ttk.Label(main_frame, text="알림 (미팅 시작 전):").grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        alert_frame = ttk.Frame(main_frame)
        alert_frame.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        self.alert_var = tk.StringVar(value=str(self.default_alert_minutes))
        ttk.Spinbox(
            alert_frame, from_=1, to=60, width=5, textvariable=self.alert_var
        ).pack(side=tk.LEFT)
        ttk.Label(alert_frame, text=" 분 전").pack(side=tk.LEFT)

        # 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=10, column=0, columnspan=2)

        ttk.Button(btn_frame, text="저장", command=self._on_save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="취소", command=self._on_cancel).pack(side=tk.LEFT)

        if self.meeting:
            self._load_meeting_data()

        self.name_entry.focus_set()
        dialog.bind("<Return>", lambda e: self._on_save())
        dialog.bind("<Escape>", lambda e: self._on_cancel())

    def _make_date_row(self, parent: ttk.Frame, initial: str = "") -> tuple:
        """날짜 스핀박스 행 생성. (year_var, month_var, day_var, get_date_fn) 반환"""
        try:
            d = dt_date.fromisoformat(initial) if initial else dt_date.today()
        except (ValueError, TypeError):
            d = dt_date.today()

        year_var = tk.StringVar(value=str(d.year))
        month_var = tk.StringVar(value=f"{d.month:02d}")
        day_var = tk.StringVar(value=f"{d.day:02d}")

        ttk.Spinbox(parent, from_=2020, to=2099, width=5, textvariable=year_var).pack(side=tk.LEFT)
        ttk.Label(parent, text="년 ").pack(side=tk.LEFT)
        ttk.Spinbox(parent, from_=1, to=12, width=3, textvariable=month_var, format="%02.0f").pack(side=tk.LEFT)
        ttk.Label(parent, text="월 ").pack(side=tk.LEFT)
        ttk.Spinbox(parent, from_=1, to=31, width=3, textvariable=day_var, format="%02.0f").pack(side=tk.LEFT)
        ttk.Label(parent, text="일").pack(side=tk.LEFT)

        def get_date() -> str:
            y = year_var.get().strip()
            m = month_var.get().strip().zfill(2)
            dd = day_var.get().strip().zfill(2)
            return f"{y}-{m}-{dd}"

        return year_var, month_var, day_var, get_date

    def _rebuild_date_widgets(self) -> None:
        # 현재 날짜 값 저장
        if self._get_start_date:
            self._saved_start_date = self._get_start_date()
        if self._get_end_date:
            self._saved_end_date = self._get_end_date()

        for w in self.date_container.winfo_children():
            w.destroy()

        self._get_start_date = None
        self._get_end_date = None

        is_repeat = self.repeat_var.get()

        if is_repeat:
            # 시작일
            row1 = ttk.Frame(self.date_container)
            row1.pack(fill=tk.X, pady=(0, 6))
            ttk.Label(row1, text="시작일: ", width=9, anchor=tk.W).pack(side=tk.LEFT)
            _, _, _, self._get_start_date = self._make_date_row(row1, self._saved_start_date)

            # 완료일
            row2 = ttk.Frame(self.date_container)
            row2.pack(fill=tk.X)
            ttk.Label(row2, text="완료일: ", width=9, anchor=tk.W).pack(side=tk.LEFT)
            _, _, _, self._get_end_date = self._make_date_row(row2, self._saved_end_date)
        else:
            # 알림 요청일
            row1 = ttk.Frame(self.date_container)
            row1.pack(fill=tk.X)
            ttk.Label(row1, text="알림 요청일: ", anchor=tk.W).pack(side=tk.LEFT)
            sy, sm, sd, self._get_start_date = self._make_date_row(row1, self._saved_start_date)
            self._get_end_date = None

            def auto_weekday(*_):
                try:
                    d = dt_date.fromisoformat(self._get_start_date())
                    for i, var in enumerate(self.day_vars):
                        var.set(i == d.weekday())
                except Exception:
                    pass

            for v in (sy, sm, sd):
                v.trace_add("write", auto_weekday)
            # 날짜가 지정된 경우에만 초기 자동 설정
            if self._saved_start_date:
                auto_weekday()

    def _load_meeting_data(self) -> None:
        if not self.meeting:
            return

        self.name_entry.insert(0, self.meeting.name)

        # 저장된 날짜를 먼저 세팅한 뒤 repeat_var 변경 (trace가 _rebuild_date_widgets 호출)
        self._saved_start_date = self.meeting.start_date
        self._saved_end_date = self.meeting.end_date
        self.repeat_var.set(self.meeting.repeat)

        # _rebuild_date_widgets의 auto_weekday보다 meeting.days를 우선 적용
        for i, var in enumerate(self.day_vars):
            var.set(i in self.meeting.days)

        self.hour_var.set(f"{self.meeting.hour:02d}")
        self.minute_var.set(f"{self.meeting.minute:02d}")
        self.alert_var.set(str(self.meeting.alert_minutes))

    def _on_save(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("경고", "미팅 이름을 입력해주세요.", parent=self.dialog)
            self.name_entry.focus_set()
            return

        repeat = self.repeat_var.get()

        # 날짜 검증
        start_str = self._get_start_date() if self._get_start_date else None
        end_str = self._get_end_date() if self._get_end_date else None

        try:
            start_d = dt_date.fromisoformat(start_str) if start_str else None
            end_d = dt_date.fromisoformat(end_str) if end_str else None
            if start_d and end_d and end_d < start_d:
                messagebox.showwarning("경고", "완료일이 시작일보다 이전입니다.", parent=self.dialog)
                return
        except ValueError:
            messagebox.showwarning("경고", "날짜가 올바르지 않습니다.", parent=self.dialog)
            return

        # 1회 미팅: 날짜에서 요일 자동 결정
        if not repeat and start_str and start_d:
            days = [start_d.weekday()]
        else:
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

        if self.meeting:
            self.meeting.name = name
            self.meeting.days = days
            self.meeting.hour = hour
            self.meeting.minute = minute
            self.meeting.alert_minutes = alert_minutes
            self.meeting.repeat = repeat
            self.meeting.start_date = start_str
            self.meeting.end_date = end_str
            self.result = self.meeting
        else:
            self.result = Meeting(
                name=name,
                days=days,
                hour=hour,
                minute=minute,
                alert_minutes=alert_minutes,
                repeat=repeat,
                start_date=start_str,
                end_date=end_str,
            )

        if self.on_save:
            self.on_save(self.result)

        self.dialog.destroy()

    def _on_cancel(self) -> None:
        self.dialog.destroy()
