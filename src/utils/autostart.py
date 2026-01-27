"""Windows 자동 시작 설정"""
import sys
import os
import winreg


APP_NAME = "MeetingAlarm"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_exe_path() -> str:
    """실행 파일 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 exe
        return sys.executable
    else:
        # Python 스크립트로 실행
        return f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'


def is_autostart_enabled() -> bool:
    """자동 시작이 활성화되어 있는지 확인"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def set_autostart(enabled: bool) -> bool:
    """자동 시작 설정/해제"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            if enabled:
                exe_path = get_exe_path()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            return True
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        print(f"자동 시작 설정 실패: {e}")
        return False
