"""시스템 트레이 아이콘"""
import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw


def create_default_icon() -> Image.Image:
    """기본 아이콘 생성 (빨간색 원 위에 종 모양)"""
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 빨간색 원 배경
    padding = 4
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=(255, 107, 107, 255)
    )

    # 흰색 종 모양 (간단한 형태)
    bell_color = (255, 255, 255, 255)
    center_x = size // 2
    # 종 몸체
    draw.ellipse([18, 20, 46, 44], fill=bell_color)
    # 종 손잡이
    draw.arc([26, 12, 38, 24], 0, 180, fill=bell_color, width=3)
    # 종 아래 부분
    draw.ellipse([26, 42, 38, 50], fill=bell_color)

    return image


class TrayIcon:
    def __init__(
        self,
        on_open: Callable,
        on_quit: Callable,
        icon_path: Optional[str] = None
    ):
        self.on_open = on_open
        self.on_quit = on_quit
        self.icon_path = icon_path
        self._icon = None
        self._thread: Optional[threading.Thread] = None

    def _create_icon(self):
        """아이콘 이미지 로드 또는 생성"""
        if self.icon_path:
            try:
                return Image.open(self.icon_path)
            except Exception:
                pass
        return create_default_icon()

    def _create_menu(self):
        """트레이 메뉴 생성"""
        import pystray

        return pystray.Menu(
            pystray.MenuItem("열기", self._on_open_click, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("종료", self._on_quit_click)
        )

    def _on_open_click(self, icon, item):
        """열기 메뉴 클릭"""
        self.on_open()

    def _on_quit_click(self, icon, item):
        """종료 메뉴 클릭"""
        self.stop()
        self.on_quit()

    def start(self) -> None:
        """트레이 아이콘 시작"""
        import pystray

        image = self._create_icon()
        menu = self._create_menu()

        self._icon = pystray.Icon(
            "meeting_alarm",
            image,
            "회의 알림",
            menu
        )

        # 더블클릭 이벤트
        self._icon.on_activate = lambda: self.on_open()

        # 별도 스레드에서 실행
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """트레이 아이콘 중지"""
        if self._icon:
            self._icon.stop()
            self._icon = None

    def update_tooltip(self, text: str) -> None:
        """툴팁 텍스트 업데이트"""
        if self._icon:
            self._icon.title = text
