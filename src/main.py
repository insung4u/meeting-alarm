"""회의 알림 프로그램 진입점"""
import sys
import os

# 패키지 경로 추가 (개발 환경에서 실행 시)
src_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(src_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.app import MeetingAlarmApp


def main():
    app = MeetingAlarmApp()
    app.run()


if __name__ == "__main__":
    main()
