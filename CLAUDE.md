# Meeting Alarm 프로젝트

Windows용 매주 반복 회의 알림 프로그램입니다.

## 프로젝트 구조

```
meeting-alarm/
├── src/
│   ├── main.py          # 진입점
│   ├── app.py           # 메인 애플리케이션
│   ├── core/            # 핵심 로직
│   │   ├── meeting.py   # 미팅 데이터 모델
│   │   └── scheduler.py # 알림 스케줄러
│   ├── ui/              # UI 컴포넌트
│   │   ├── main_window.py
│   │   ├── meeting_dialog.py
│   │   └── alert_window.py
│   ├── tray/            # 시스템 트레이
│   │   └── tray_icon.py
│   └── utils/           # 유틸리티
│       └── autostart.py # Windows 자동 시작
├── assets/              # 아이콘, 이미지
├── installer/           # Inno Setup 스크립트
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
```bash
# Inno Setup 설치 필요
& 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' installer/setup.iss
```
결과: `dist/installer/MeetingAlarm_Setup.exe`

## 데이터 저장 위치

- `%APPDATA%\MeetingAlarm\meetings.json` - 미팅 목록
- `%APPDATA%\MeetingAlarm\settings.json` - 설정

## 주의사항

- Windows 전용 프로그램
- 시스템 트레이 기능은 pystray 사용
- 자동 시작은 레지스트리 등록 방식
