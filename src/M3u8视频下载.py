import subprocess
import os
from datetime import datetime


def download_m3u8(m3u8_url, output_path, headers=None):
    """
    下载并合并 m3u8 视频

    :param m3u8_url:    m3u8 播放列表的 URL
    :param output_path: 最终 MP4 文件的保存路径（包含文件名）
    :param headers:     请求头，dict 形式，如 {"Referer": "...", "User-Agent": "..."}
                        传 None 则不带任何自定义请求头
    """
    # 1. 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. 构建 FFmpeg 命令
    cmd = ['ffmpeg']

    # 3. 如果传入了 headers，转换成 FFmpeg 需要的格式再插入命令
    #    FFmpeg 的 -headers 只接受"一个字符串"，多个头之间必须用 \r\n 分隔
    if headers:
        headers_str = "\r\n".join(f"{k}: {v}" for k, v in headers.items())
        cmd += ['-headers', headers_str]

    cmd += [
        '-i', m3u8_url,
        '-c', 'copy',              # 直接复制音视频流，不重新编码，速度极快
        '-bsf:a', 'aac_adtstoasc', # 处理 AAC 音频兼容性，防止无声
        '-y',                      # 覆盖已存在的同名文件
        output_path,
    ]

    print(f"🚀 开始下载: {m3u8_url}")
    print(f"💾 保存路径: {output_path}")
    if headers:
        print(f"🔑 携带请求头: {headers}")

    # 4. 执行下载
    try:
        subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("✅ 下载并合并完成！")
    except subprocess.CalledProcessError as e:
        print(f"❌ 下载失败，错误信息:\n{e.stderr}")
    except FileNotFoundError:
        print("❌ 错误：未找到 ffmpeg，请确保已安装并配置到系统环境变量中。")


# --- 使用示例 ---
if __name__ == "__main__":
    # 替换为你的 m3u8 链接
    url = "https://v26-web.douyinvod.com/d3c17e5333263cde2a16e500207e9a5f/6ac3c4f2/video/tos/cn/tos-cn-ve-15/cbf617e451f242cebc1a41e4bf634f98/?a=6383&ch=26&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=1976&bt=1976&cs=0&ds=6&ft=4TMWc6DnppftDFLB.s2.C_bAja-CInilWkpc6Bd3hx7NVYpHDD__.CqEj_HeXusZ.&mime_type=video_mp4&qs=0&rc=OGY6NjRkZztnZDMzZDY1NkBpM3A7eXdnNXVtdTMzNmkzM0AtNjEtX2MzXzAxLjNhYGEzYSNkbi8wYWQ0cGhfLS1gLS9zcw%3D%3D&btag=c0000e00008000&cquery=100x_102u_100o_100w_100B&dy_q=1791204020&l=2026100520402099D7EC8FBB4F4FEBEDD5&testst=1791204037222"  
    now_str = datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒%f")[:-3]
    save_path = f"/Users/teacher/Desktop/百度网盘下载/{now_str}.mp4"

    # 把 headers 以 dict 形式传进去（针对抖音防盗链）
    headers = {
        "Referer": "https://www.douyin.com/",
        "User-Agent": ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                       "Version/17.5 Mobile/15E148 Safari/604.1"),
    }

    download_m3u8(url, save_path, headers=headers)