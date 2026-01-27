# GitHub 릴리즈 생성

새 버전을 GitHub에 릴리즈합니다.

## 인자

- $ARGUMENTS: 버전 번호 (예: v1.0.1)

## 실행할 작업

1. exe 빌드: `python build.py`
2. 설치 프로그램 생성: Inno Setup 컴파일
3. GitHub 릴리즈 생성:
   ```
   gh release create $ARGUMENTS dist/installer/MeetingAlarm_Setup.exe --title "$ARGUMENTS" --notes "릴리즈 $ARGUMENTS"
   ```
4. 릴리즈 URL 알려주기
