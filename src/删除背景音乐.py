import subprocess
import os
from datetime import datetime

def remove_audio_from_video(video_path, save_path):
    """
    使用 FFmpeg 去除视频中的音频（音乐/人声），并以时间戳命名保存。
    
    :param video_path: 原始视频文件的路径
    :param output_dir: 输出文件夹路径（默认为当前目录下的 output 文件夹）
    """
    # 1. 检查输入文件是否存在
    if not os.path.exists(video_path):
        print(f"[错误] 找不到视频文件: {video_path}")
        return



    # 4. 构建 FFmpeg 命令
    # -i video_path : 指定输入文件
    # -an           : 禁用音频流 (Audio No)
    # -c:v copy     : 视频流直接复制，不重新编码（速度极快，画质无损）
    # save_path     : 指定输出文件路径
    cmd = [
        "ffmpeg", "-y",      # -y 表示如果文件已存在则直接覆盖
        "-i", video_path, 
        "-an", 
        "-c:v", "copy", 
        save_path
    ]

    print(f"[处理中] 正在去除音频并保存至: {save_path}")
    
    # 5. 执行命令并捕获输出
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[成功] 视频处理完成！")
        else:
            print(f"[失败] FFmpeg 处理出错: \n{result.stderr}")
            
    except FileNotFoundError:
        print("[错误] 未找到 FFmpeg，请确保已安装并将其添加到系统环境变量中。")

# === 测试运行 ===
if __name__ == "__main__":
    # 替换为你本地视频的实际路径
    video_path = "/Users/teacher/Desktop/百度网盘下载/2026年10月05日20时56分32秒581.mp4" 

    base_name, ext = os.path.splitext(video_path)
    save_path = f"{base_name}_去背景音乐{ext}"



    remove_audio_from_video(
        video_path = video_path,
        save_path = save_path
    )