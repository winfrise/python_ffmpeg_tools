# -*- coding: utf-8 -*-
"""
M3U8 通用下载器（自动判断 mp4 / mp3 + 下载进度 + 分离入参）

依赖：本机已安装 ffmpeg / ffprobe 并配置到系统环境变量。

核心能力：
1. 入参分离：分别传入「保存目录 save_dir」和「保存文件名 save_name」；
2. 自动判断格式：探测 m3u8 内的流，含视频流 -> mp4(直接封装，不转码)，
   纯音频流 -> mp3(音频重编码)；也可通过 fmt 参数强制指定；
3. 下载进度：实时打印百分比进度条（基于已下载时长 / 总时长）；
4. 请求头：dict 形式传入，自动转成 ffmpeg 需要的格式（抖音等防盗链）。
"""

import os
import re
import shutil
import subprocess
from datetime import datetime


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def _build_headers_arg(headers):
    """把 dict 请求头转成 ffmpeg -headers 需要的单个字符串（\r\n 分隔）。"""
    if not headers:
        return None
    return "\r\n".join(f"{k}: {v}" for k, v in headers.items())


def _time_to_seconds(hh, mm, ss):
    """把 ffmpeg/ffprobe 的时码字符串(00:01:23.45)换算成秒(float)。"""
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


def _check_ffmpeg():
    """检查 ffmpeg / ffprobe 是否可用，缺哪个抛 FileNotFoundError 信息。"""
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise EnvironmentError(
                f"未找到 {tool}，请确认已安装 ffmpeg 并配置到系统环境变量 PATH 中。")


def _ffprobe_info(m3u8_url, headers=None):
    """
    探测 m3u8：返回 (是否有视频流, 是否有音频流, 总时长秒)。
    探测失败时返回 (None, None, 0.0)，调用方按默认 mp4 处理。
    """
    cmd = ["ffprobe", "-hide_banner", "-loglevel", "error"]

    headers_str = _build_headers_arg(headers)
    if headers_str:
        cmd += ["-headers", headers_str]

    cmd += [
        "-show_entries", "stream=codec_type:format=duration",
        "-of", "default=noprint_wrappers=1",
        m3u8_url,
    ]

    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="ignore", check=True).stdout
    except subprocess.CalledProcessError:
        return None, None, 0.0

    has_video = has_audio = False
    duration = 0.0
    for line in out.splitlines():
        line = line.strip()
        if "codec_type=video" in line:
            has_video = True
        elif "codec_type=audio" in line:
            has_audio = True
        elif line.startswith("duration="):
            try:
                duration = float(line.split("=", 1)[1])
            except ValueError:
                pass
    return has_video, has_audio, duration


def _make_bar(percent, width=30):
    filled = int(width * percent / 100)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}]"


# ---------------------------------------------------------------------------
# 主下载函数
# ---------------------------------------------------------------------------
def download_m3u8(m3u8_url, save_dir, save_name, headers=None, fmt="auto"):
    """
    下载并合并 m3u8。

    :param m3u8_url:  m3u8 播放列表 URL
    :param save_dir:  保存目录（不存在会自动创建）
    :param save_name: 保存文件名（可带或不带扩展名，见下）
    :param headers:   请求头 dict，如 {"Referer": "...", "User-Agent": "..."}；None 则不带
    :param fmt:       'auto'(默认,自动判断) / 'mp4' / 'mp3'
                      - auto：探测有视频 -> mp4；纯音频 -> mp3
                      若 save_name 已带 .mp4/.mp3 扩展名，则以扩展名为准；
                      未带扩展名时自动补上最终判定的扩展名。
    :return: 实际保存的完整文件路径(str)，失败返回 None
    """
    _check_ffmpeg()

    # 1. 目录处理
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    # 2. 探测流信息，决定格式与总时长
    print("正在探测媒体信息 ...")
    has_video, has_audio, total_seconds = _ffprobe_info(m3u8_url, headers)

    # 解析文件名与扩展名
    name_no_ext, ext = os.path.splitext(save_name)
    ext = ext.lower().lstrip(".")

    if ext in ("mp4", "mp3"):
        final_fmt = ext                     # 文件名已指定扩展名，以其为准
    elif fmt in ("mp4", "mp3"):
        final_fmt = fmt                     # 参数强制指定
    else:                                   # auto
        if has_video:
            final_fmt = "mp4"
        elif has_audio:
            final_fmt = "mp3"
        else:
            final_fmt = "mp4"               # 探测不到时默认 mp4

    output_path = os.path.join(save_dir, f"{name_no_ext}.{final_fmt}")

    # 3. 构建 ffmpeg 命令
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats"]

    headers_str = _build_headers_arg(headers)
    if headers_str:
        cmd += ["-headers", headers_str]

    cmd += ["-i", m3u8_url]

    if final_fmt == "mp4":
        # 直接复制音视频流，不重新编码（极快）；aac_adtstoasc 防 AAC 无声
        cmd += ["-c", "copy", "-bsf:a", "aac_adtstoasc"]
    else:  # mp3：纯音频，丢弃视频流并重编码为 mp3
        cmd += ["-vn", "-acodec", "libmp3lame", "-q:a", "0"]

    cmd += ["-y", output_path]

    print(f"源地址 : {m3u8_url}")
    print(f"判定格式 : {final_fmt}"
          + ("  (含视频流)" if final_fmt == "mp4" and has_video else
             "  (纯音频流)" if final_fmt == "mp3" and has_audio else ""))
    print(f"保存路径 : {output_path}")
    if total_seconds > 0:
        print(f"预计时长 : {int(total_seconds // 60):02d}:"
              f"{int(total_seconds % 60):02d}")
    print("-" * 50)

    # 4. 执行下载并实时打印进度
    last_pct = -1
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="ignore")

        buf = ""
        while True:
            ch = proc.stderr.read(1)
            if not ch:
                break
            if ch in ("\r", "\n"):
                line = buf.strip()
                buf = ""
                m = re.search(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)", line)
                if m and total_seconds > 0:
                    cur = _time_to_seconds(m.group(1), m.group(2), m.group(3))
                    pct = min(100.0, cur / total_seconds * 100)
                    if pct - last_pct >= 0.5:
                        bar = _make_bar(pct)
                        print(f"\r{bar} {pct:5.1f}%  "
                              f"{int(cur // 60):02d}:{int(cur % 60):02d} / "
                              f"{int(total_seconds // 60):02d}:"
                              f"{int(total_seconds % 60):02d}   ",
                              end="", flush=True)
                        last_pct = pct
                elif line and "error" in line.lower():
                    print("\n" + line)
            else:
                buf += ch

        proc.wait()
        print()  # 进度条换行

        if proc.returncode != 0:
            print(f"[失败] ffmpeg 返回码 {proc.returncode}，下载未完成。")
            return None

        print("\n[完成] 下载并合并结束！")
        return output_path

    except FileNotFoundError:
        print("[错误] 未找到 ffmpeg，请检查安装与环境变量。")
        return None


# ---------------------------------------------------------------------------
# 使用示例
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    url = ("https://op.udhhzr.cn/videos5/13bf809a726064ed83b4340783a819df/13bf809a726064ed83b4340783a819df.m3u8?auth_key=1791876354-6acddd02e7561-0-c60962cb9259c6f4905f3da01854044b&v=3&time=0&project_id=tj005&pv=1")

    # 保存目录与保存文件名分离
    save_dir = "/Volumes/西数4T外置/ff_2026-10"
    now_str = datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒")
    save_name = now_str            # 不带扩展名 -> 由程序自动补 mp4 或 mp3

    # 抖音防盗链请求头
    headers = {
        "Referer": "https://www.douyin.com/",
        "User-Agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                       "Version/17.5 Mobile/15E148 Safari/604.1"),
    }

    download_m3u8(url, save_dir, save_name, headers=headers, fmt="auto")