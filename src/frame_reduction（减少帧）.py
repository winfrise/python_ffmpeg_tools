import subprocess
import os
from typing import Union, List, Dict, Any
from datetime import datetime

def _build_frame_reduction_cmd(
    input_path: str, 
    output_path: str, 
    target_fps: float
) -> List[str]:
    """
    【纯函数】构建用于降低视频帧率的 FFmpeg 命令列表。
    不产生任何副作用，仅返回命令结构。
    """
    return [
        "ffmpeg", "-y", 
        "-i", input_path, 
        "-vf", f"fps={target_fps}",  # 核心：使用 fps 滤镜降低帧率
        "-c:v", "libx264",          # 指定 H.264 编码器，保证兼容性
        "-crf", "23",               # 恒定质量因子（18-28，越小画质越好）
        "-preset", "medium",        # 编码速度预设
        "-an",                      # 移除音频（如果不需要的话，可删除此行）
        output_path
    ]

def reduce_video_frames(
    input_path: str, 
    output_path: None, 
    target_fps: float = 15.0
) -> Dict[str, Any]:
    """
    降低视频帧率（抽帧）的封装函数。
    
    :param input_path: 输入视频路径
    :param output_path: 输出视频路径
    :param target_fps: 目标帧率（例如：原视频30fps，设为15fps可减半帧数）
    :return: 包含执行状态的字典
    """



    # 1. 自动处理输出文件路径
    if not output_path:
        # 获取输入文件的目录、文件名和扩展名
        input_dir = os.path.dirname(input_path)
        input_filename_no_ext = os.path.splitext(os.path.basename(input_path))[0]
        input_ext = os.path.splitext(input_path)[1]
        
        # 生成当前时间戳，精确到毫秒
        timestamp = datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒%f")[:-3]
        
        # 构建新的文件名：原文件名_时间戳.扩展名
        new_filename = f"{input_filename_no_ext}_减少帧_{timestamp}{input_ext}"
        
        # 组合成完整的输出路径
        output_path = os.path.join(input_dir, new_filename)
        print(f"ℹ️ 未指定输出路径，将自动生成: {output_path}")

    try:
        # 1. 纯函数构建命令
        cmd = _build_frame_reduction_cmd(input_path, output_path, target_fps)
        
        # 2. 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 3. 执行 FFmpeg 进程
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # 4. 返回结构化结果
        if result.returncode == 0:
            return {"status": "success", "output": output_path, "target_fps": target_fps}
        else:
            return {"status": "error", "message": result.stderr}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    output_path = "/Users/teacher/Downloads/教学视频.txt/未命名文件夹"
    result = reduce_video_frames(
        input_path="https://vodbj.wqketang.com/30367605500071ef865d7fb2780c0102/f933eb9a47be4d06b3df4b907170962b-d67ce0e7afe6e3128f57244ce1b1001b-sd-nbv1.mp4?auth_key=1788854629-aded9909309740ae93dd9374f6cfffa4-0-2411d40ab392bde44c48a788d28cda9d", 
        output_path=output_path, 
        target_fps=10.0
    )

    print(result)