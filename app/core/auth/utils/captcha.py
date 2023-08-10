import random
from PIL import Image, ImageDraw, ImageFont
from app.core.auth.utils.password import get_password_hash, verify_and_update_password
import uuid
import io
import base64

from app.core.config import settings
from app.core.cache import cache

font = ImageFont.FreeTypeFont(settings.CAPTCHA_FONT_PATH, size=30)


def create_captcha(text):
    # 创建一个Image对象
    width, height = 150, 50
    image = Image.new('RGB', (width, height), color=(255, 255, 255))

    # 创建一个Draw对象
    draw = ImageDraw.Draw(image)

    # 计算文本的宽度和高度
    _, _, text_width, text_height = font.getbbox(text)
    # 将文本添加到图片中
    text_x = (width - text_width) / 2
    text_y = (height - text_height) / 2
    draw.text((text_x, text_y), text, fill=(0, 180, 0), font=font)

    # 添加噪声
    for _ in range(5):  # 添加点
        x, y = random.randint(0, width), random.randint(0, height)
        point_size = random.randint(2, 5)
        draw.ellipse((x-point_size, y-point_size, x+point_size,
                     y+point_size), fill=(0, 180, 0))

    for _ in range(3):  # 添加线
        draw.line([
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height))
        ], fill=(0, 180, 0), width=3)
    # 将图片转换为base64字符串
    buffered = io.BytesIO()
    image.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # image.save("captcha.png")
    return f"data:image/png;base64,{img_str}"


def random_problem(difficulty: int = 10):
    # 确保难度级别至少为1
    difficulty = max(1, difficulty)

    # 生成两个随机数，范围在1到难度级别之间
    num1 = random.randint(1, difficulty)
    num2 = random.randint(1, difficulty)

    # 选择加法或减法。如果第一个数小于第二个数，我们选择加法以确保结果为正数
    if num1 < num2:
        problem = f"{num1} + {num2} = ?"
        answer = str(num1 + num2)
    else:
        problem = f"{num1} - {num2} = ?"
        answer = str(num1 - num2)

    return (problem, answer)


async def get_captcha(difficulty: int = 10):
    problem, answer = random_problem(difficulty)
    uuid_str = str(uuid.uuid4())
    await cache.set(f"fast_captcha:{uuid_str}", answer, ex=300)
    return (create_captcha(problem), uuid_str)


async def verify_captcha(answer: str, captcha_id: str):
    try:
        if answer is None or len(answer) == 0:
            verified = False
        else:
            saved_answer = await cache.getdel(f"fast_captcha:{captcha_id}")
            verified = saved_answer == answer
    except Exception:
        verified = False
    return verified
