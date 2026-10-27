import subprocess
import os
import json

def add_background_music(video_path, music_path, output_path, bgm_volume=0.3):
    """
    智能添加背景音乐：自动处理无声视频和有声视频
    """
    if not os.path.exists(video_path) or not os.path.exists(music_path):
        raise FileNotFoundError("输入文件不存在")

    # 1. 探测视频是否包含音频流
    # 使用 ffprobe 获取流信息，输出为 JSON 格式方便解析
    probe_cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'a', 
        '-show_entries', 'stream=index', '-of', 'json', video_path
    ]
    
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        streams = json.loads(result.stdout).get('streams', [])
        has_audio = len(streams) > 0
    except Exception as e:
        print(f"⚠️ 无法探测视频信息，默认按有声处理: {e}")
        has_audio = True

    print(f"🔍 视频检测: {'包含音频' if has_audio else '纯视频(无音频)'}")

    # 2. 根据检测结果构建不同的命令
    if has_audio:
        # --- 情况 A: 视频有声音 -> 使用 amix 混音 ---
        # [1:a]volume=...[bgm]: 调整背景音乐音量并标记为 [bgm]
        # [0:a][bgm]amix=...: 将原声 [0:a] 和背景音乐 [bgm] 混合
        filter_complex = (
            f"[1:a]volume={bgm_volume}[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', music_path,
            '-filter_complex', filter_complex,
            '-map', '0:v',      # 映射视频流
            '-map', '[aout]',   # 映射混合后的音频流
            '-c:v', 'copy',     # 视频直接复制，不重编码
            '-c:a', 'aac',      # 音频重新编码为 aac
            output_path
        ]
    else:
        # --- 情况 B: 视频无声音 -> 直接使用背景音乐 ---
        # 不需要 filter_complex，直接映射音乐流即可
        # shortest 参数确保如果音乐比视频长，音频会被截断
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', music_path,
            '-map', '0:v',      # 映射视频流
            '-map', '1:a',      # 映射音乐流
            '-c:v', 'copy',     # 视频直接复制
            '-c:a', 'aac',      # 音频编码为 aac
            '-shortest',        # 以最短的流（视频）为准结束
            output_path
        ]

    # 3. 执行命令
    print("🚀 开始处理...")
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0:
            print(f"✅ 成功！文件已保存至: {output_path}")
        else:
            print("❌ 处理失败，FFmpeg 报错:")
            print(process.stderr)
    except FileNotFoundError:
        print("❌ 错误: 未在系统中找到 ffmpeg 或 ffprobe，请检查环境变量。")

# 使用示例
# add_background_music('001.mp4', '11.wav', 'output.mp4')
# 示例调用
if __name__ == "__main__":
    video_path = "/Users/teacher/Desktop/111111/001.mp4"
    music_path = "/Users/teacher/Desktop/111111/11.wav"

    base_name, ext = os.path.splitext(video_path)
    output_path = f"{base_name}_output_合并{ext}"    # 替换为你期望的输出路径
    add_background_music(
        video_path=video_path, 
        music_path=music_path, 
        output_path=output_path
    )