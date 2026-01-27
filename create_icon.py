"""아이콘 파일 생성 스크립트"""
from PIL import Image, ImageDraw
import os


def create_icon():
    """프로그램 아이콘 생성 (ICO 파일) - 캘린더 + 시계 디자인"""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 색상 정의
        calendar_bg = (66, 133, 244, 255)  # 파란색 (Google Calendar 스타일)
        calendar_top = (52, 106, 195, 255)  # 진한 파란색 (상단)
        white = (255, 255, 255, 255)
        clock_bg = (255, 193, 7, 255)  # 노란색/주황색 (알림 강조)
        clock_hand = (50, 50, 50, 255)  # 시계 바늘

        padding = max(1, size // 16)
        corner_radius = size // 8

        # 캘린더 배경 (둥근 사각형)
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=corner_radius,
            fill=calendar_bg
        )

        # 캘린더 상단 바
        top_height = size * 0.22
        draw.rounded_rectangle(
            [padding, padding, size - padding, padding + top_height],
            radius=corner_radius,
            fill=calendar_top
        )
        # 상단 바 하단 모서리 채우기
        draw.rectangle(
            [padding, padding + top_height - corner_radius,
             size - padding, padding + top_height],
            fill=calendar_top
        )

        # 캘린더 고리 (2개)
        ring_width = max(2, size // 16)
        ring_height = size * 0.12
        ring_y = padding
        for ring_x in [size * 0.28, size * 0.72]:
            draw.rounded_rectangle(
                [ring_x - ring_width, ring_y - ring_height * 0.3,
                 ring_x + ring_width, ring_y + ring_height],
                radius=max(1, ring_width // 2),
                fill=white
            )

        # 캘린더 날짜 격자 (간단하게 점으로 표현)
        if size >= 32:
            dot_size = max(2, size // 20)
            grid_start_y = padding + top_height + size * 0.08
            grid_spacing = size * 0.18
            for row in range(2):
                for col in range(3):
                    dot_x = size * 0.22 + col * grid_spacing
                    dot_y = grid_start_y + row * grid_spacing
                    draw.ellipse(
                        [dot_x - dot_size, dot_y - dot_size,
                         dot_x + dot_size, dot_y + dot_size],
                        fill=(255, 255, 255, 180)
                    )

        # 시계 (오른쪽 하단)
        clock_size = size * 0.42
        clock_x = size - padding - clock_size * 0.6
        clock_y = size - padding - clock_size * 0.6

        # 시계 배경
        draw.ellipse(
            [clock_x - clock_size / 2, clock_y - clock_size / 2,
             clock_x + clock_size / 2, clock_y + clock_size / 2],
            fill=clock_bg,
            outline=white,
            width=max(1, size // 32)
        )

        # 시계 바늘
        if size >= 32:
            # 시침 (짧은 바늘 - 10시 방향)
            hour_len = clock_size * 0.22
            draw.line(
                [clock_x, clock_y,
                 clock_x - hour_len * 0.5, clock_y - hour_len * 0.85],
                fill=clock_hand,
                width=max(2, size // 24)
            )
            # 분침 (긴 바늘 - 12시 방향)
            min_len = clock_size * 0.32
            draw.line(
                [clock_x, clock_y,
                 clock_x, clock_y - min_len],
                fill=clock_hand,
                width=max(1, size // 32)
            )
            # 중심점
            center_dot = max(2, size // 40)
            draw.ellipse(
                [clock_x - center_dot, clock_y - center_dot,
                 clock_x + center_dot, clock_y + center_dot],
                fill=clock_hand
            )

        images.append(image)

    # 가장 큰 이미지를 기준으로 ICO 저장
    os.makedirs("assets", exist_ok=True)
    images[-1].save(
        "assets/icon.ico",
        format="ICO",
        sizes=[(s, s) for s in sizes]
    )
    print("assets/icon.ico 파일이 생성되었습니다.")


if __name__ == "__main__":
    create_icon()
