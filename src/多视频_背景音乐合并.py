import os
import subprocess
import re
from pathlib import Path

def get_media_duration_ffmpeg(file_path):
    """
    不依赖 ffprobe，直接使用 ffmpeg 获取时长
    """
    cmd = [
        "ffmpeg", "-i", str(file_path)
    ]
    # ffmpeg 的版本信息输出在 stderr 中
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stderr
        
        # 正则匹配 Duration: 00:00:10.50, start: ...
        match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2})\.(\d+)", output)
        if match:
            h, m, s, ms = match.groups()
            duration = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / (10 ** len(ms))
            return duration
        else:
            print(f"[警告] 无法从 ffmpeg 输出中解析时长: {file_path}")
            return 0.0
            
    except Exception as e:
        print(f"[错误] 获取时长失败: {e}")
        return 0.0

def merge_videos(video_list, output_video="temp_merged_video.mp4"):
    """
    使用 concat demuxer 合并视频（忽略原始音频）
    """
    print("\n[1/3] 正在合并视频列表...")
    list_file = "temp_file_list.txt"
    
    with open(list_file, "w", encoding="utf-8") as f:
        for v in video_list:
            safe_path = str(v).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")
            
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
        "-i", list_file, 
        "-c:v", "copy", 
        "-an",           
        output_video
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"[成功] 视频合并完成: {output_video}")
        return output_video
    except subprocess.CalledProcessError as e:
        print(f"[错误] 视频合并失败: {e}")
        return None
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

def process_bgm(bgm_path, target_duration, output_audio="temp_processed_bgm.aac"):
    """
    处理背景音乐：短了循环，长了截取
    """
    print(f"\n[2/3] 正在处理背景音乐 (目标时长: {target_duration:.2f}s)...")
    
    cmd = [
        "ffmpeg", "-y", "-stream_loop", "-1", 
        "-i", str(bgm_path), 
        "-t", str(target_duration), 
        "-c:a", "aac", "-b:a", "192k", 
        "-shortest",
        output_audio
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"[成功] 背景音乐处理完成: {output_audio}")
        return output_audio
    except subprocess.CalledProcessError as e:
        print(f"[错误] 背景音乐处理失败: {e}")
        return None

def combine_video_audio(video_path, audio_path, final_output="final_output.mp4"):
    """
    将处理好的视频和音频合并
    """
    print(f"\n[3/3] 正在合成最终视频...")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",      
        "-c:a", "aac",       
        "-map", "0:v:0",     
        "-map", "1:a:0",     
        "-shortest",         
        final_output
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n🎉 全部完成！最终视频: {final_output}")
    except subprocess.CalledProcessError as e:
        print(f"[错误] 最终合成失败: {e}")

def main():
    # ================= 配置区域 =================
    # 视频列表（支持相对路径或绝对路径）
    video_files = [
        "/Users/teacher/Downloads/小狗视频/文件1.mp4",
        "/Users/teacher/Downloads/小狗视频/文件2.mp4",
        "/Users/teacher/Downloads/小狗视频/文件3.mp4",
        "/Users/teacher/Downloads/小狗视频/文件4.mp4",
        "/Users/teacher/Downloads/小狗视频/文件5.mp4"
    ]
    
    # 背景音乐（支持 mp3, mp4, wav 等）
    bgm_file = "/Users/teacher/Downloads/小狗视频/bg.mp4" 
    
    # 输出文件名
    final_name = "/Users/teacher/Downloads/小狗视频/output.mp4"
    # ===========================================

    for v in video_files:
        if not os.path.exists(v):
            print(f"[致命错误] 找不到视频文件: {v}")
            return
    if not os.path.exists(bgm_file):
        print(f"[致命错误] 找不到背景音乐: {bgm_file}")
        return

    # 1. 合并视频
    merged_video = merge_videos(video_files, "temp_merged_video.mp4")
    if not merged_video: return

    # 2. 获取时长 (使用修改后的函数)
    total_duration = get_media_duration_ffmpeg(merged_video)
    if total_duration <= 0:
        print("[致命错误] 合并后的视频时长异常，请检查视频文件是否损坏")
        # 即使获取失败，也可以尝试继续，或者在这里退出
        # return 

    # 3. 处理背景音乐
    processed_audio = process_bgm(bgm_file, total_duration, "temp_processed_bgm.aac")
    if not processed_audio: return

    # 4. 最终合成
    combine_video_audio(merged_video, processed_audio, final_name)

    # 5. 清理临时文件
    print("\n[清理] 正在删除临时文件...")
    for f in ["temp_merged_video.mp4", "temp_processed_bgm.aac"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()