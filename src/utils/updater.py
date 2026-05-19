"""자동 업데이트 유틸리티"""
import threading
import urllib.request
import json
import os
import tempfile
from typing import Optional, Callable

GITHUB_API = "https://api.github.com/repos/insung4u/meeting-alarm/releases/latest"
INSTALLER_NAME = "MeetingAlarm_Setup.exe"


def get_latest_version(callback: Callable[[Optional[str]], None]) -> None:
    """GitHub API로 최신 버전 비동기 조회. callback(version_str or None) 호출"""
    def fetch():
        try:
            req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "MeetingAlarm"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                tag = json.loads(resp.read()).get("tag_name", "")
                callback(tag.lstrip("v") or None)
        except Exception:
            callback(None)
    threading.Thread(target=fetch, daemon=True).start()


def download_installer(
    version: str,
    on_progress: Callable[[int], None],
    on_done: Callable[[str], None],
    on_error: Callable[[str], None],
) -> None:
    """최신 설치 파일을 임시 폴더에 다운로드. on_done(installer_path) 호출"""
    url = (
        f"https://github.com/insung4u/meeting-alarm/releases/download/"
        f"v{version}/{INSTALLER_NAME}"
    )

    def fetch():
        try:
            tmp_path = os.path.join(tempfile.mkdtemp(), INSTALLER_NAME)
            req = urllib.request.Request(url, headers={"User-Agent": "MeetingAlarm"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                with open(tmp_path, "wb") as f:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            on_progress(int(downloaded / total * 100))
            on_done(tmp_path)
        except Exception as e:
            on_error(str(e))

    threading.Thread(target=fetch, daemon=True).start()
