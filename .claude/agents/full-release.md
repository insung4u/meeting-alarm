# Full Release 에이전트

빌드부터 GitHub 릴리즈까지 전체 과정을 자동으로 수행합니다.

## 인자

- $ARGUMENTS: 버전 번호 (예: v1.0.1)

## 수행 단계

### 1. 버전 확인
- 인자로 받은 버전 번호 확인
- 버전 번호가 없으면 사용자에게 요청

### 2. exe 빌드
```bash
python build.py
```
- 빌드 성공 확인
- 실패 시 에러 보고 후 중단

### 3. 설치 프로그램 생성
```powershell
& 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' installer/setup.iss
```
- 컴파일 성공 확인
- 실패 시 에러 보고 후 중단

### 4. GitHub 릴리즈
```bash
gh release create $ARGUMENTS dist/installer/MeetingAlarm_Setup.exe --title "$ARGUMENTS" --notes "릴리즈 $ARGUMENTS"
```

### 5. 완료 보고
- 릴리즈 URL 출력
- 다운로드 링크 확인
