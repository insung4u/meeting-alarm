"""소리 재생"""
import winsound
import threading


def play_alert_sound() -> None:
    """알림 소리 재생 (비동기)"""
    def _play():
        try:
            # Windows 기본 알림 소리 재생
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()


def play_alert_sound_sync() -> None:
    """알림 소리 재생 (동기)"""
    try:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        pass
