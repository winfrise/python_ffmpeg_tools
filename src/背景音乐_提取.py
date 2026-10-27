import subprocess
import os

def extract_audio(input_video, output_video):
    """
    使用 FFmpeg 从视频中提取音频并转换为 MP3 格式。
    
    :param input_video: 输入视频文件的路径 (str)
    :param output_video: 输出音频文件的路径 (str)
    """
    # 构建 FFmpeg 命令列表
    command = [
        "ffmpeg",
        "-i", input_video,      # 指定输入文件
        "-vn",                  # 禁用视频流
        "-acodec", "libmp3lame",# 指定音频编码器为 MP3
        "-ab", "192k",          # 设置音频比特率为 192kbps
        output_video            # 指定输出文件
    ]
    
    try:
        # 执行命令并捕获标准输出和错误信息
        result = subprocess.run(command, capture_output=True, text=True)
        
        # 检查命令是否成功执行
        if result.returncode == 0:
            print(f"✅ 音频提取成功！已保存至: {output_video}")
        else:
            print(f"❌ FFmpeg 处理失败，错误信息:\n{result.stderr}")
            
    except FileNotFoundError:
        print("❌ 错误：未找到 ffmpeg 命令，请确保已安装 FFmpeg 并配置了系统环境变量。")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

# --- 使用示例 ---
if __name__ == "__main__":
    input_path = "/Users/teacher/Downloads/未命名文件夹/下载 (1).mp4"

    base_name, ext = os.path.splitext(input_path)
    output_path = f"{base_name}.mp3"
    extract_audio(input_path, output_path)