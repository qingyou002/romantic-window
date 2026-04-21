
import tkinter as tk
import random
import math
import sys
from pathlib import Path

POSITION_SHIFT_X = random.random()
POSITION_SHIFT_Y = random.random()
BG_COLORS = ["#A9D6FF", "#FFC1DE", "#FFF1A8", "#BFE9C8", "#D8C4FF"]
opened_windows = []
heart_windows = []


def halton(index, base):
    # 低差异序列，用来让窗口位置分布得更均匀
    result = 0.0
    factor = 1.0 / base
    i = index + 1
    while i > 0:
        result += factor * (i % base)
        i //= base
        factor /= base
    return result

def load_lines(file_name):
    # 按行读取文本，自动去掉空行；文件不存在时返回空列表
    file_path = get_resource_path(file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def get_resource_path(file_name):
    # 优先读 exe/脚本同目录下的外部文件，找不到再回退到打包内置资源
    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).resolve().parent
    else:
        base_path = Path(__file__).resolve().parent

    external_path = base_path / file_name
    if external_path.exists():
        return external_path

    if hasattr(sys, "_MEIPASS"):
        bundled_path = Path(sys._MEIPASS) / file_name
        if bundled_path.exists():
            return bundled_path

    return external_path


names = load_lines("名字.txt")
sentences = load_lines("sentences.txt")
final_sentence = sentences[-1] if sentences else "hello~"

def create_one_window(index):
    # 创建一个随机位置、随机背景色的小窗口
    create_window_with_text(index)


def create_window_with_text(index, x=None, y=None, text=None):
    # 统一的小窗口创建逻辑，普通阶段和心形阶段共用
    win = tk.Toplevel()
    win.title(" ")
    opened_windows.append(win)

    # 固定窗口大小
    w = 190
    h = 90

    if x is None or y is None:
        # 使用低差异序列，让窗口在屏幕范围内分布更均匀
        max_x = max(0, root.winfo_screenwidth() - w)
        max_y = max(0, root.winfo_screenheight() - h)
        x_ratio = (halton(index, 2) + POSITION_SHIFT_X) % 1.0
        y_ratio = (halton(index, 3) + POSITION_SHIFT_Y) % 1.0
        x = int(x_ratio * max_x)
        y = int(y_ratio * max_y)

    bg_color = random.choice(BG_COLORS)
    fg_color = "#2F3A4A"

    win.geometry(f"{w}x{h}+{x}+{y}")
    win.configure(bg=bg_color)

    # 加文字
    if text is None:
        text = random.choice(sentences) if sentences else "hello~"
    label = tk.Label(win, text=text, font=("微软雅黑", 12), bg=bg_color, fg=fg_color)
    label.pack(expand=True, fill="both")
    return win


def close_windows_gradually(index=0):
    # 关闭速度从慢到快，逐个收起已打开的小窗口
    if index >= len(opened_windows):
        root.after(120, show_heart_shape)
        return

    win = opened_windows[index]
    if win.winfo_exists():
        win.destroy()

    delay = max(8, 180 - index * 5)
    root.after(delay, lambda: close_windows_gradually(index + 1))


def create_heart_windows():
    # 用小窗口的位置轨迹拼出心形轮廓
    center_x = root.winfo_screenwidth() // 2
    center_y = root.winfo_screenheight() // 2 - 20
    scale = 20
    seen_positions = set()
    points = []

    for step in range(170):
        t = math.pi * 2 * step / 180
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        x_pos = int(center_x + x * scale)
        y_pos = int(center_y - y * scale)
        position_key = (x_pos // 18, y_pos // 18)
        if position_key not in seen_positions:
            seen_positions.add(position_key)
            points.append((x_pos, y_pos))

    for index, (x_pos, y_pos) in enumerate(points):
        heart_windows.append(
            create_window_with_text(index, x_pos, y_pos, final_sentence)
        )


def show_heart_shape():
    create_heart_windows()


def start_small_windows():
    # 关闭互动窗口后，再开始按节奏生成小窗口
    intro_window.destroy()
    for i in range(100):
        root.after(i * 100, lambda idx=i: create_one_window(idx))
    root.after(100 * 100 + 1800, close_windows_gradually)


# 主窗口先隐藏，只保留后续生成的小窗口
root = tk.Tk()
root.withdraw()  # 隐藏主窗口，只留小窗口

# 启动前的互动窗口
intro_window = tk.Toplevel(root)
intro_window.title("小游戏")
intro_window.geometry("360x220+600+400")
intro_window.configure(bg="#FFF7FB")
intro_window.resizable(False, False)

name_text = random.choice(names) if names else "XXX"
title_label = tk.Label(
    intro_window,
    text=name_text,
    font=("微软雅黑", 20, "bold"),
    bg="#FFF7FB",
    fg="#2F3A4A",
)
title_label.pack(pady=(40, 15))

# 点击后开始正式生成小窗口
start_button = tk.Button(
    intro_window,
    text="开始游戏",
    font=("微软雅黑", 12),
    bg="#D8C4FF",
    fg="#2F3A4A",
    activebackground="#C8B1FF",
    activeforeground="#2F3A4A",
    command=start_small_windows,
)
start_button.pack(pady=10, ipadx=16, ipady=6)

intro_window.mainloop()