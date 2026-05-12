# Meeting Alarm 프로젝트

Windows용 회의 알림 프로그램입니다. 매주 반복 또는 1회 알림을 지원합니다.

## 프로젝트 구조

```
meeting-alarm/
├── src/
│   ├── main.py          # 진입점
│   ├── app.py           # 메인 애플리케이션 (전체 흐름 조율)
│   ├── version.py       # 버전 상수 (VERSION = "x.x.x")
│   ├── core/            # 핵심 로직
│   │   ├── meeting.py   # 미팅 데이터 모델
│   │   ├── scheduler.py # 알림 스케줄러 (백그라운드 스레드)
│   │   └── storage.py   # JSON 파일 저장/로드
│   ├── ui/              # UI 컴포넌트
│   │   ├── main_window.py    # 메인 윈도우 (미팅 목록, 설정)
│   │   ├── meeting_dialog.py # 미팅 추가/수정 다이얼로그
│   │   └── alert_window.py   # 알림 팝업
│   ├── tray/            # 시스템 트레이
│   │   └── tray_icon.py
│   └── utils/           # 유틸리티
│       └── autostart.py # Windows 자동 시작 (레지스트리)
├── assets/              # 아이콘, 이미지
├── installer/           # Inno Setup 스크립트
│   └── setup.iss        # 버전 정보 포함 (version.py와 동기화 필요)
├── build.py             # PyInstaller 빌드 스크립트
├── create_icon.py       # 아이콘 생성 스크립트
└── requirements.txt     # Python 의존성
```

## 기술 스택

- Python 3.9+
- tkinter (GUI)
- pystray (시스템 트레이)
- Pillow (이미지 처리)
- PyInstaller (exe 빌드)
- Inno Setup (설치 프로그램)

## 빌드 명령어

### 개발 실행
```bash
python src/main.py
```

### exe 빌드
```bash
python build.py
```
결과: `dist/MeetingAlarm.exe`

### 설치 프로그램 생성
```powershell
# Inno Setup 설치 위치 (사용자 설치 기준)
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" installer/setup.iss
```
결과: `dist/installer/MeetingAlarm_Setup.exe`

## 릴리즈 절차

기능 추가 또는 수정 후 GitHub에 올릴 때는 아래 순서를 반드시 따른다.

1. **버전 번호 업데이트** — 두 곳 모두 수정
   - `src/version.py` → `VERSION = "x.x.x"`
   - `installer/setup.iss` → `#define MyAppVersion "x.x.x"`

2. **README.md 업데이트**
   - 추가/수정된 기능을 `## 주요 기능` 및 `## 사용 방법`에 반영
   - `## 버전 히스토리`에 새 버전 항목 추가

3. **CLAUDE.md 업데이트**
   - AI 참고 정보 중 변경된 내용 반영

4. **소스 커밋**
   - `__pycache__` 제외, 변경된 `.py` 파일과 문서 파일만 스테이징
   ```bash
   git add src/... README.md CLAUDE.md installer/setup.iss
   git commit -m "..."
   git push
   ```

5. **exe 빌드**
   ```bash
   python build.py
   ```

6. **설치 파일 생성**
   ```powershell
   & "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" installer/setup.iss
   ```

7. **GitHub 릴리즈 생성**
   ```bash
   gh release create vX.X.X dist/installer/MeetingAlarm_Setup.exe --title "vX.X.X" --notes "..."
   ```
   - 같은 태그 릴리즈가 이미 있으면 `gh release upload vX.X.X ... --clobber` 로 파일 교체
   - GitHub CLI(`gh`) 위치: `%LOCALAPPDATA%\GitHubCLI\bin\gh.exe` (사용자 설치 기준)

## 데이터 저장 위치

- `%APPDATA%\MeetingAlarm\meetings.json` - 미팅 목록
- `%APPDATA%\MeetingAlarm\settings.json` - 설정

---

## AI 참고 정보

### 버전 관리
버전은 두 곳에서 관리되며 항상 동기화해야 한다.
- `src/version.py` → 앱 내 설정 창에 표시
- `installer/setup.iss` → 설치 파일 버전 정보

버전 변경 시 두 파일 모두 수정 후 빌드(`build.py`) → 설치 파일(`ISCC.exe`) 순서로 진행한다.

### Meeting 데이터 모델 (`src/core/meeting.py`)
```python
@dataclass
class Meeting:
    name: str
    days: List[int]       # 0=월 ~ 6=일
    hour: int
    minute: int
    alert_minutes: int = 5
    id: str               # uuid4 자동 생성
    enabled: bool = True
    repeat: bool = True   # True=매주반복, False=1회
```
- `repeat=False`이고 `enabled=False`이면 알림 완료된 1회 미팅
- `from_dict`에서 `repeat` 필드 없는 구버전 JSON도 호환 처리 (`setdefault`)

### 스케줄러 동작 (`src/core/scheduler.py`)
- 10초마다 체크, 알림 시간 ±30초 범위 내에서 1회 발동
- 중복 방지: `_alerted` set에 `(meeting_id, date)` 키로 관리, 자정에 초기화
- `repeat=False` 미팅은 알림 발동 후 `enabled=False` 처리 후 `on_meeting_disabled` 콜백 호출
- 콜백은 스케줄러 스레드에서 호출되므로 UI 조작은 반드시 `root.after(0, ...)` 사용

### UI 패턴
- **스레드 안전**: 스케줄러(백그라운드 스레드) → UI 변경은 항상 `root.after(0, fn)` 경유
- **취소선 표시**: `ttk.Treeview` 태그에 `tkfont.Font(overstrike=True)` 적용
  - `tkfont.Font(overstrike=True)` — 인자 없이 호출하면 시스템 기본 폰트 상속
  - `treeview.cget("font")`는 ttk에서 지원 안 됨 (TclError 발생)
- **설정 창 버전 표시**: `VERSION` 상수를 `main_window.py`에서 import해 라벨로 표시

### 주의사항
- Windows 전용 (pystray Windows 백엔드, 레지스트리 자동 시작)
- `__pycache__` 폴더가 git에 이미 트래킹된 상태 (`.gitignore`에 있지만 기존 커밋에 포함됨)
  - 소스 `.py` 파일만 스테이징해서 커밋할 것
- Inno Setup이 시스템 전역이 아닌 사용자 로컬에 설치됨:
  `C:\Users\insun\AppData\Local\Programs\Inno Setup 6\ISCC.exe`
