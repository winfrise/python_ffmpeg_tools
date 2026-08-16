import subprocess
import os
from datetime import datetime

def add_multiple_watermarks(
    input_video: str, 
    output_video: str = None,  # 修改：设置为可选参数
    watermarks: list[dict] = None, 
    default_font_path: str = "simhei.ttf",
    preserve_quality: bool = True
) -> None:
    """
    支持同时添加多个文字水印，包含水平垂直居中及位置偏移功能。
    如果未指定输出路径，将自动在原文件目录下生成带时间戳的新文件。
    """
    if watermarks is None:
        watermarks = []

    # 1. 自动处理输出文件路径
    if not output_video:
        # 获取输入文件的目录、文件名和扩展名
        input_dir = os.path.dirname(input_video)
        input_filename_no_ext = os.path.splitext(os.path.basename(input_video))[0]
        input_ext = os.path.splitext(input_video)[1]
        
        # 生成当前时间戳，精确到毫秒
        timestamp = datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒%f")[:-3]
        
        # 构建新的文件名：原文件名_时间戳.扩展名
        new_filename = f"{input_filename_no_ext}_{timestamp}{input_ext}"
        
        # 组合成完整的输出路径
        output_video = os.path.join(input_dir, new_filename)
        print(f"ℹ️ 未指定输出路径，将自动生成: {output_video}")

    # 2. 位置映射逻辑
    def get_position_xy(pos: str):
        pos_map = {
            "top_left":     "x=10:y=10",
            "top_right":    "x=w-tw-10:y=10",
            "bottom_left":  "x=10:y=h-th-10",
            "bottom_right": "x=w-tw-10:y=h-th-10",
            "center":       "x=(w-tw)/2:y=(h-th)/2"
        }
        return pos_map.get(pos, "x=10:y=10") 

    filter_parts = []

    # 3. 遍历水印配置，构建滤镜链
    for wm in watermarks:
        text = wm.get("text", "Watermark")
        pos = wm.get("position")
        font_size = wm.get("font_size", 24)
        font_color = wm.get("font_color", "white")
        offset = wm.get("offset", (0, 0))
        
        # 支持自定义坐标或预设位置
        if wm.get("custom_xy"):
            x_expr, y_expr = wm["custom_xy"]
        else:
            base_xy = get_position_xy(pos)
            x_expr = base_xy.split(":")[0].split("=")[1]
            y_expr = base_xy.split(":")[1].split("=")[1]

        # 应用偏移量
        if offset[0] != 0:
            x_expr = f"{x_expr}+{offset[0]}"
        if offset[1] != 0:
            y_expr = f"{y_expr}+{offset[1]}"
        
        # 构建完整 drawtext 滤镜
        filter_str = (
            f"drawtext="
            f"text='{text}':"
            f"fontfile='{default_font_path}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"x={x_expr}:"
            f"y={y_expr}"
        )
        filter_parts.append(filter_str)

    # 4. 合并所有滤镜
    vf_filter = ",".join(filter_parts)

    # 5. 构建 FFmpeg 命令
    cmd = ["ffmpeg", "-i", input_video, "-vf", vf_filter]

    # 6. 如果启用画质保留模式，尝试匹配原视频码率
    if preserve_quality:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=bit_rate", "-of", "default=noprint_wrappers=1:nokey=1", input_video],
                capture_output=True, text=True, check=True
            )
            original_bitrate = result.stdout.strip()
            if original_bitrate and original_bitrate != "N/A":
                cmd.extend(["-b:v", original_bitrate])
        except Exception:
            cmd.extend(["-b:v", "5000k"])
        
        cmd.extend(["-preset", "slow"])
    
    # 7. 复制音频流，避免音频重编码
    cmd.extend(["-c:a", "copy", output_video])

    # 8. 执行命令
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"✅ 水印添加完成: {output_video}")


# === 使用示例 ===
if __name__ == "__main__":
    watermarks_config = [
        {
            "text": "左上角水印",
            "position": "top_left",
            "font_size": 30,
            "font_color": "yellow",
            "offset": (20, 20)  # 向右下偏移20像素
        },
        {
            "text": "居中水印",
            "position": "center",
            "font_size": 40,
            "font_color": "red@0.8"
        },
        {
            "text": "右下角偏移",
            "position": "bottom_right",
            "font_size": 24,
            "font_color": "white",
            "offset": (-30, -30)  # 向左上偏移30像素
        }
    ]



if __name__ == "__main__":
    input_video = "/Volumes/西数4T外置/ffmpeg_output/test.mp4"
    output_video = None
    font_path ="/Users/teacher/Library/Fonts/FZDHTJW.TTF"
    font_color="white@0.8"  # 80% 透明度的白色
    preserve_quality = False # 是否开启画质保留模式

    my_watermarks = [
        {
            "text": "我的LogoCenter", 
            "position": "center", 
            "font_size": 30, 
            "font_color": "red",
            "offset": (0, 20),  # 向右偏移20，向下偏移20
        },
        {
            "text": "我的LogoCenter", 
            "position": "center", 
            "font_size": 30, 
            "font_color": "red"
        },
        {
            "text": "我的Logo左上", 
            "position": "top_left", 
            "font_size": 30, 
            "font_color": "yellow"
        },
        {
            "text": "版权所有 ©2024右下", 
            "position": "bottom_right", 
            "font_size": 20, 
            "font_color": "white@0.8" # @0.8 表示透明度
        },
        {
            "text": "我的Logo左下", 
            "position": "bottom_left", 
            "font_size": 30, 
            "font_color": "yellow"
        },
        {
            "text": "版权所有 ©2024右上", 
            "position": "top_right", 
            "font_size": 20, 
            "font_color": "white@0.8" # @0.8 表示透明度
        },
        {
            "text": "自定义位置测试", 
            "custom_xy": (100, 100), # 绝对坐标 x=100, y=100
            "font_size": 40, 
            "font_color": "red"
        }
    ]

    add_multiple_watermarks(
        input_video=input_video,
        output_video=output_video,
        watermarks=my_watermarks,
        default_font_path=font_path,
        preserve_quality = preserve_quality,
    )




