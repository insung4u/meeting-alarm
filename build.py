"""PyInstaller 빌드 스크립트"""
import PyInstaller.__main__
import os
import shutil

# 빌드 디렉토리 정리
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# PyInstaller 실행
PyInstaller.__main__.run([
    "src/main.py",
    "--name=MeetingAlarm",
    "--onefile",
    "--windowed",
    "--add-data=assets;assets",
    "--icon=assets/icon.ico" if os.path.exists("assets/icon.ico") else "",
    "--noconfirm",
    "--clean",
])

print("\n빌드 완료! dist/MeetingAlarm.exe 파일이 생성되었습니다.")
