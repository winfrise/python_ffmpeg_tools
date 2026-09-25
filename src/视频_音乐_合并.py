import subprocess
import os

def merge_video_and_music(video_path: str, music_path: str, output_path: str):
    """
    将视频循环播放，并与背景音乐合并，最终视频长度与背景音乐一致。
    
    :param video_path: 输入视频文件的路径
    :param music_path: 输入背景音乐文件的路径
    :param output_path: 输出合成后视频的文件路径
    """
    # 检查文件是否存在
    if not os.path.exists(video_path) or not os.path.exists(music_path):
        raise FileNotFoundError("视频文件或音乐文件不存在，请检查路径！")

    # 构建 FFmpeg 命令
    # -stream_loop -1: 无限循环输入的视频流
    # -i video_path: 输入视频
    # -i music_path: 输入背景音乐
    # -c:v copy: 视频流直接复制，不重新编码（处理速度极快）
    # -c:a aac: 音频流重新编码为 AAC 格式（保证兼容性）
    # -map 0:v:0 -map 1:a:0: 明确指定输出流来源（视频取第一个输入，音频取第二个输入）
    # -shortest: 以最短的输入流（即背景音乐）时长为准结束输出
    # -y: 覆盖已存在的输出文件
    command = [
        "ffmpeg",
        "-stream_loop", "-1",
        "-i", video_path,
        "-i", music_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-y",
        output_path
    ]

    try:
        # 执行命令
        subprocess.run(command, check=True)
        print(f"✅ 视频合成成功！输出文件: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg 执行出错: {e}")


# --- 使用示例 ---
if __name__ == "__main__":
    video_file = "/Users/teacher/Downloads/未命名文件夹/父亲的货车很大，大的能装下月亮，父亲的货车又很小唯独装不下对.mp4"      # 替换为你的视频路径
    music_file = "/Users/teacher/Downloads/未命名文件夹/父亲的货车很大，大的能装下月亮，父亲的货车又很小唯独装不下对.mp3" # 替换为你的背景音乐路径
    
    base_name, ext = os.path.splitext(video_file)
    output_file = f"{base_name}_output_合并{ext}"    # 替换为你期望的输出路径
    
    merge_video_and_music(video_file, music_file, output_file)