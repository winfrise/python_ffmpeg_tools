import subprocess
import os

def merge_video_audio(video_path, audio_path, output_path):
    """
    将视频和音频合并，保持视频原画质和音频原音质（无损流复制）。
    
    :param video_path: 输入视频文件的路径 (str)
    :param audio_path: 输入音频文件的路径 (str)
    :param output_path: 输出合并后文件的路径 (str)
    """
    command = [
        "ffmpeg",
        "-y",                # 覆盖已存在的输出文件
        "-i", video_path,    # 输入视频
        "-i", audio_path,    # 输入音频
        "-c:v", "copy",      # 视频流直接复制，不重新编码，保证原画质
        "-c:a", "copy",      # 音频流直接复制，不重新编码，保证原音质
        "-map", "0:v:0",     # 精确指定取第一个输入的视频流
        "-map", "1:a:0",     # 精确指定取第二个输入的音频流
        "-shortest",         # 若音视频时长不一致，以较短的为准，避免黑屏或静音
        output_path          # 输出文件路径
    ]
    
    try:
        # 执行命令并捕获标准输出和错误信息
        result = subprocess.run(command, capture_output=True, text=True)
        
        # 检查命令是否成功执行
        if result.returncode == 0:
            print(f"✅ 音视频合并成功！已保存至: {output_path}")
        else:
            print(f"❌ FFmpeg 处理失败，错误信息:\n{result.stderr}")
            
    except FileNotFoundError:
        print("❌ 错误：未找到 ffmpeg 命令，请确保已安装 FFmpeg 并配置了系统环境变量。")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

# --- 使用示例 ---
if __name__ == "__main__":
    video_file = "/Users/teacher/Downloads/未命名文件夹/下载.mp4"
    audio_file = "/Users/teacher/Downloads/未命名文件夹/下载 (1).mp3"

    base_name, ext = os.path.splitext(video_file)
    output_file = f"{base_name}_合并背景音乐.{ext}"

    
    merge_video_audio(video_file, audio_file, output_file)