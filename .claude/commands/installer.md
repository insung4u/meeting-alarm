# 설치 프로그램 생성

Inno Setup으로 Windows 설치 프로그램을 생성합니다.

## 실행할 작업

1. exe 빌드 확인 (없으면 `python build.py` 먼저 실행)
2. Inno Setup 컴파일:
   ```
   & 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' installer/setup.iss
   ```
3. 결과 확인: `dist/installer/MeetingAlarm_Setup.exe`
4. 성공/실패 여부 알려주기
