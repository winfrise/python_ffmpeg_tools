import subprocess
import os
from typing import List, Dict, Union, TypedDict, Optional

# 定义时间输入类型：支持 数字(秒) 或 字符串('MM:SS', 'HH:MM:SS')
TimeInput = Union[int, float, str]

# 定义 Segment 对象的结构
# start_time: 必填
# end_time: 可选，结束时间
# duration: 可选，持续时长
class SegmentConfig(TypedDict, total=False):
    start_time: TimeInput
    end_time: Optional[TimeInput]
    duration: Optional[TimeInput]

def _parse_time(time_val: TimeInput) -> float:
    """
    内部辅助方法：将各种格式的时间统一转换为秒数。
    """
    if isinstance(time_val, (int, float)):
        return float(time_val)
    if isinstance(time_val, str):
        parts = list(map(float, time_val.strip().split(':')))
        if len(parts) == 3: # HH:MM:SS
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2: # MM:SS
            return parts[0] * 60 + parts[1]
        elif len(parts) == 1: # S (纯秒数)
            return parts[0]
        else:
            raise ValueError(f"无法识别的时间字符串格式: {time_val}")
    raise TypeError(f"不支持的时间类型: {type(time_val)}")

def cut_video_segments(
    input_path: str,
    segments: List[SegmentConfig],
    output_dir: str = "./output",
    codec: str = "copy"
) -> List[str]:
    """
    基于 FFmpeg 截取视频的多个片段。
    
    参数 segments 是一个字典列表，每个字典代表一个片段配置:
    - start_time: (必填) 开始时间
    - end_time: (可选) 结束时间
    - duration: (可选) 持续时长
    
    优先级: duration > end_time
    即：如果同时提供了 duration 和 end_time，将以 duration 为准。
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入视频不存在: {input_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    generated_files = []

    for idx, seg in enumerate(segments):
        # 1. 获取并解析必填的开始时间
        if 'start_time' not in seg:
            print(f"[警告] 第 {idx+1} 个片段缺少 'start_time'，已跳过。")
            continue
        start_sec = _parse_time(seg['start_time'])
        
        # 2. 根据优先级计算 duration 和 end_sec
        duration = 0.0
        end_sec = 0.0
        mode_label = ""

        if 'duration' in seg:
            # duration 模式 (高优先级)
            duration = _parse_time(seg['duration'])
            end_sec = start_sec + duration
            mode_label = "时长模式"
        elif 'end_time' in seg:
            # end_time 模式 (低优先级)
            end_sec = _parse_time(seg['end_time'])
            duration = end_sec - start_sec
            mode_label = "区间模式"
        else:
            print(f"[警告] 第 {idx+1} 个片段缺少 'end_time' 或 'duration'，已跳过。")
            continue

        # 3. 参数校验
        if duration <= 0:
            print(f"[警告] 第 {idx+1} 个片段参数无效 (计算出的时长 <= 0)，已跳过。")
            continue
        if start_sec < 0:
            print(f"[警告] 第 {idx+1} 个片段开始时间不能为负数，已跳过。")
            continue

        # 4. 构建输出路径
        output_path = os.path.join(output_dir, f"{base_name}_seg{idx+1}_{start_sec}s-{end_sec}s.mp4")
        
        # 5. 构建 FFmpeg 命令
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_sec),
            "-i", input_path,
            "-t", str(round(duration, 3)),
            "-c", codec,
            "-avoid_negative_ts", "make_zero",
            output_path
        ]

        print(f"⏳ 正在截取第 {idx+1} 个片段 [{mode_label}]: 开始={start_sec}s, 参数={seg.get('duration') or seg.get('end_time')} ...")
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
    output_dir = "/Volumes/西数4T外置/ffmpeg_output"

    # --- 测试用例 ---
    my_segments: List[SegmentConfig] = [
        # 1. 传统模式：从 3分03秒 到 3分38秒
        {"start_time": "3:03", "end_time": "3:38"},
        
        # 2. 时长模式：从 7分40秒 开始，截取 60秒
        {"start_time": "7:40", "duration": "60"},
        
        # 3. 优先级测试：同时提供 end_time 和 duration
        # 程序会忽略 end_time="11:00"，而是从 10:00 开始截取 30秒
        {"start_time": "10:00", "end_time": "11:00", "duration": "30"},
        
        # 4. 纯数字模式：从 200秒 开始，截取 15.5秒
        {"start_time": 200, "duration": 15.5},
    ]

    results = cut_video_segments(
        input_path=video_file,
        segments=my_segments,
        output_dir=output_dir
    )
    print("\n所有生成的文件:", results)