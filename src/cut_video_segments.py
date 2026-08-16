import subprocess
import os
from typing import List, Tuple, Union

# 定义时间输入类型：支持 数字(秒) 或 字符串('MM:SS', 'HH:MM:SS')
TimeInput = Union[int, float, str]

def _parse_time(time_val: TimeInput) -> float:
    """
    内部辅助方法：将各种格式的时间统一转换为秒数。
    - 数字：直接作为秒返回
    - 字符串：支持 'MM:SS' 或 'HH:MM:SS' 格式
    """
    if isinstance(time_val, (int, float)):
        return float(time_val)
    
    if isinstance(time_val, str):
        parts = list(map(float, time_val.strip().split(':')))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        else:
            raise ValueError(f"无法识别的时间字符串格式: {time_val} (请使用 MM:SS 或 HH:MM:SS)")
            
    raise TypeError(f"不支持的时间类型: {type(time_val)}，请传入数字或字符串。")

def cut_video_segments(
    input_path: str, 
    segments: List[Tuple[TimeInput, TimeInput]], 
    output_dir: str = "./output",
    codec: str = "copy"
) -> List[str]:
    """
    基于 FFmpeg 截取视频的多个片段（支持多种时间格式）。
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入视频不存在: {input_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    generated_files = []

    for idx, (start_raw, end_raw) in enumerate(segments):
        # 在函数内部自动解析时间格式
        start = _parse_time(start_raw)
        end = _parse_time(end_raw)
        
        if start >= end or start < 0:
            print(f"[警告] 第 {idx+1} 个片段时间无效 (start={start}, end={end})，已跳过。")
            continue
            
        duration = round(end - start, 3)
        output_path = os.path.join(output_dir, f"{base_name}_seg{idx+1}_{start}s-{end}s.mp4")
        
        cmd = [
            "ffmpeg", "-y", 
            "-ss", str(start), 
            "-i", input_path, 
            "-t", str(duration), 
            "-c", codec, 
            "-avoid_negative_ts", "make_zero", 
            output_path
        ]
        
        print(f"⏳ 正在截取第 {idx+1} 个片段: {start}s -> {end}s ...")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            generated_files.append(output_path)
            print(f"✅ 成功: {output_path}")
        except subprocess.CalledProcessError:
            print(f"❌ 失败: 截取第 {idx+1} 个片段时发生错误。")
        except FileNotFoundError:
            raise EnvironmentError("未找到 ffmpeg 命令，请确保已安装 FFmpeg 并配置到环境变量中。")

    return generated_files
if __name__ == "__main__":
    video_file = "/Volumes/西数4T外置/thu-2026-0813/xxx.mp4"
    ouput_dir = "/Volumes/西数4T外置/ffmpeg_output"
    # 定义需要截取的多个片段 (开始秒数, 结束秒数)
    my_segments = [
        ("3:03", "3:38"),
        ("7:40", "8:40"),
        ("10:00", "10:20"),
    ]
    
    # 一行代码搞定批量截取
    results = cut_video_segments(
        input_path=video_file, 
        segments=my_segments,
        output_dir=ouput_dir
    )
    
    print("\n所有生成的文件:", results)