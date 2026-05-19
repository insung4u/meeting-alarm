"""메인 윈도우 UI"""
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from typing import List, Callable, Optional

from ..core.meeting import Meeting
from ..core.storage import load_settings, save_settings
from ..utils.autostart import is_autostart_enabled, set_autostart
from ..version import VERSION
from .meeting_dialog import MeetingDialog


class MainWindow:
    def __init__(
        self,
        root: tk.Tk,
        meetings: List[Meeting],
        on_meeting_change: Callable[[List[Meeting]], None],
        on_close: Optional[Callable] = None
    ):
        self.root = root
        self.meetings = meetings
        self.on_meeting_change = on_meeting_change
        self.on_close = on_close
        self.settings = load_settings()

        self._setup_window()
        self._create_widgets()
        self._populate_meeting_list()

    def _setup_window(self) -> None:
        self.root.title("회의 알림")
        self.root.geometry("500x400")
        self.root.minsize(400, 300)

        # 아이콘 설정 (있는 경우)
        try:
            import sys
            import os
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            icon_path = os.path.join(base_path, "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def _create_widgets(self) -> None:
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 상단 버튼 프레임
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="+ 미팅 추가", command=self._add_meeting).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="수정", command=self._edit_meeting).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="삭제", command=self._delete_meeting).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="설정", command=self._open_settings).pack(side=tk.RIGHT)

        # 미팅 목록
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        columns = ("name", "days", "time", "alert", "repeat")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("name", text="미팅 이름")
        self.tree.heading("days", text="요일")
        self.tree.heading("time", text="시간")
        self.tree.heading("alert", text="알림")
        self.tree.heading("repeat", text="반복")

        self.tree.column("name", width=130)
        self.tree.column("days", width=110)
        self.tree.column("time", width=70)
        self.tree.column("alert", width=70)
        self.tree.column("repeat", width=60, anchor=tk.CENTER)

        # 취소선 태그 (1회 알림 완료된 항목)
        base_font = tkfont.nametofont("TkDefaultFont")
        done_font = tkfont.Font(
            family=base_font.actual("family"),
            size=base_font.actual("size"),
            overstrike=True
        )
        self.tree.tag_configure("done", font=done_font, foreground="gray")

        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 더블클릭으로 수정
        self.tree.bind("<Double-1>", lambda e: self._edit_meeting())

        # 상태바
        self.status_var = tk.StringVar(value="준비됨")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def _populate_meeting_list(self) -> None:
        """미팅 목록 갱신"""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 미팅 추가
        for meeting in self.meetings:
            alert_text = f"{meeting.alert_minutes}분 전"
            repeat_text = "매주" if meeting.repeat else "1회"
            tags = ("done",) if not meeting.repeat and not meeting.enabled else ()
            self.tree.insert("", tk.END, iid=meeting.id, values=(
                meeting.name,
                meeting.get_days_str(),
                meeting.get_time_str(),
                alert_text,
                repeat_text,
            ), tags=tags)

    def _add_meeting(self) -> None:
        """미팅 추가"""
        def on_save(meeting: Meeting):
            self.meetings.append(meeting)
            self._populate_meeting_list()
            self.on_meeting_change(self.meetings)
            self.update_status(f"'{meeting.name}' 미팅이 추가되었습니다.")

        MeetingDialog(
            self.root,
            default_alert_minutes=self.settings.get("default_alert_minutes", 5),
            on_save=on_save
        )

    def _edit_meeting(self) -> None:
        """미팅 수정"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("알림", "수정할 미팅을 선택해주세요.")
            return

        meeting_id = selection[0]
        meeting = next((m for m in self.meetings if m.id == meeting_id), None)
        if not meeting:
            return

        def on_save(updated_meeting: Meeting):
            self._populate_meeting_list()
            self.on_meeting_change(self.meetings)
            self.update_status(f"'{updated_meeting.name}' 미팅이 수정되었습니다.")

        MeetingDialog(
            self.root,
            meeting=meeting,
            default_alert_minutes=self.settings.get("default_alert_minutes", 5),
            on_save=on_save
        )

    def _delete_meeting(self) -> None:
        """미팅 삭제"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("알림", "삭제할 미팅을 선택해주세요.")
            return

        meeting_id = selection[0]
        meeting = next((m for m in self.meetings if m.id == meeting_id), None)
        if not meeting:
            return

        if messagebox.askyesno("확인", f"'{meeting.name}' 미팅을 삭제하시겠습니까?"):
            self.meetings.remove(meeting)
            self._populate_meeting_list()
            self.on_meeting_change(self.meetings)
            self.update_status(f"'{meeting.name}' 미팅이 삭제되었습니다.")

    def _open_settings(self) -> None:
        """설정 창 열기"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("설정")
        settings_win.transient(self.root)
        settings_win.grab_set()

        width, height = 300, 220
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        settings_win.geometry(f"{width}x{height}+{x}+{y}")
        settings_win.resizable(False, False)

        frame = ttk.Frame(settings_win, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # 소리 설정
        sound_var = tk.BooleanVar(value=self.settings.get("sound_enabled", True))
        ttk.Checkbutton(frame, text="알림 소리 재생", variable=sound_var).pack(anchor=tk.W, pady=(0, 10))

        # 기본 알림 시간
        alert_frame = ttk.Frame(frame)
        alert_frame.pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(alert_frame, text="기본 알림 시간: ").pack(side=tk.LEFT)
        alert_var = tk.StringVar(value=str(self.settings.get("default_alert_minutes", 5)))
        ttk.Spinbox(alert_frame, from_=1, to=60, width=5, textvariable=alert_var).pack(side=tk.LEFT)
        ttk.Label(alert_frame, text=" 분 전").pack(side=tk.LEFT)

        # 자동 시작
        autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        ttk.Checkbutton(frame, text="Windows 시작 시 자동 실행", variable=autostart_var).pack(anchor=tk.W, pady=(0, 20))

        # 버튼
        def save_settings_click():
            self.settings["sound_enabled"] = sound_var.get()
            try:
                self.settings["default_alert_minutes"] = int(alert_var.get())
            except ValueError:
                pass
            save_settings(self.settings)
            set_autostart(autostart_var.get())
            self.update_status("설정이 저장되었습니다.")
            settings_win.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="저장", command=save_settings_click).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="취소", command=settings_win.destroy).pack(side=tk.LEFT)

        ttk.Label(frame, text=f"버전 {VERSION}", foreground="gray").pack(pady=(12, 0))

    def update_status(self, message: str) -> None:
        """상태바 메시지 업데이트"""
        self.status_var.set(message)

    def show(self) -> None:
        """창 표시"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self) -> None:
        """창 숨기기"""
        self.root.withdraw()

    def refresh_meetings(self, meetings: List[Meeting]) -> None:
        """미팅 목록 새로고침"""
        self.meetings = meetings
        self._populate_meeting_list()
