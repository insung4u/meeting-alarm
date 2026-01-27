"""아이콘 파일 생성 스크립트"""
from PIL import Image, ImageDraw
import os


def create_icon():
    """프로그램 아이콘 생성 (ICO 파일)"""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 빨간색 원 배경
        padding = max(1, size // 16)
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill=(255, 107, 107, 255)
        )

        # 흰색 종 모양
        bell_color = (255, 255, 255, 255)
        center = size // 2

        # 종 몸체 (타원)
        body_w = size * 0.44
        body_h = size * 0.38
        draw.ellipse(
            [center - body_w / 2, size * 0.31,
             center + body_w / 2, size * 0.31 + body_h],
            fill=bell_color
        )

        # 종 손잡이 (호)
        handle_w = size * 0.19
        handle_h = size * 0.19
        line_width = max(1, size // 20)
        draw.arc(
            [center - handle_w / 2, size * 0.16,
             center + handle_w / 2, size * 0.16 + handle_h],
            0, 180, fill=bell_color, width=line_width
        )

        # 종 아래 부분 (작은 원)
        clapper_r = size * 0.09
        draw.ellipse(
            [center - clapper_r, size * 0.66,
             center + clapper_r, size * 0.66 + clapper_r * 2],
            fill=bell_color
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
