import subprocess
import os
from datetime import datetime

def resize_video(input_path, output_path, width=None, height=None, mode='scale', offset_x = 0, offset_y = 0):
    """
    改变视频宽高功能
    
    :param input_path: 输入视频路径
    :param output_path: 输出视频路径
    :param width: 目标宽度 (int)
    :param height: 目标高度 (int)
    :param mode: 当同时指定宽高时的处理模式
                 'scale'  - 同比缩放 (默认，忽略另一个参数)
                 'crop'   - 裁剪后缩放 (保持比例，裁剪边缘)
                 'stretch'- 铺满/拉伸 (不保持比例，画面可能变形)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到输入文件: {input_path}")
        
    if width is None and height is None:
        raise ValueError("至少需要指定宽度或高度")

    # 1. 自动处理输出文件路径
    if not output_path:
        # 获取输入文件的目录、文件名和扩展名
        input_dir = os.path.dirname(input_path)
        input_filename_no_ext = os.path.splitext(os.path.basename(input_path))[0]
        input_ext = os.path.splitext(input_path)[1]
        
        # 生成当前时间戳，精确到毫秒
        timestamp = datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒%f")[:-3]
        
        # 构建新的文件名：原文件名_时间戳.扩展名
        new_filename = f"{input_filename_no_ext}_加水印_{timestamp}{input_ext}"
        
        # 组合成完整的输出路径
        output_path = os.path.join(input_dir, new_filename)
        print(f"ℹ️ 未指定输出路径，将自动生成: {output_path}")

    # 构建 FFmpeg 滤镜字符串
    vf_filters = []

    # 情况1：同比缩放 (只传宽或只传高，或者明确指定scale模式)
    if mode == 'scale' or (width is not None and height is None) or (width is None and height is not None):
        # FFmpeg 中 -1 表示自动计算并保持宽高比，-2 表示自动计算并对齐到偶数(推荐)
        w = str(width) if width else '-2'
        h = str(height) if height else '-2'
        vf_filters.append(f"scale={w}:{h}")

    # 情况2：铺满/拉伸改变宽高
    elif mode == 'stretch':
        vf_filters.append(f"scale={width}:{height}")

    # 情况3：裁剪改变宽高 (先裁剪中心区域，再缩放)
    elif mode == 'crop':
        # 1. 先按比例缩放，使视频刚好能覆盖目标宽高 (相当于 CSS 的 background-size: cover)
        # 公式: scale='max(target_w, iw*target_h/ih)':'max(target_h, ih*target_w/iw)'
        # 为了兼容性和偶数对齐，使用更稳健的写法：
        vf_filters.append(f"scale={width}:{height}:force_original_aspect_ratio=increase")
        # 2. 从中心裁剪出目标尺寸
        vf_filters.append(f"crop={width}:{height}:(iw-{width})/2+{offset_x}:(ih-{height})/2+{offset_y}")

    else:
        raise ValueError(f"不支持的模式: {mode}，请使用 'scale', 'crop' 或 'stretch'")

    # 拼接滤镜
    vf_string = ",".join(vf_filters)

    # 构建 FFmpeg 命令
    # -c:v libx264: 使用 H.264 编码
    # -crf 18: 高质量压缩 (数值越小质量越高，18-23为推荐范围)
    # -preset medium: 编码速度与压缩率的平衡
    # -c:a copy: 音频直接复制，不重新编码
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf_string,
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",
        "-c:a", "copy",
        output_path
    ]

    print(f"正在执行命令: {' '.join(command)}")
    
    try:
        # 运行命令并捕获输出
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✅ 视频处理成功！输出文件: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg 处理失败:")
        print(e.stderr)
        raise


if __name__ == "__main__":
    input_path = "/Volumes/西数4T外置/ffmpeg_output/test.mp4"
    output_path = None
    width=400 
    height=600 
    mode='crop' # crop 或 scale 


    resize_video(
        input_path = input_path, 
        output_path = output_path, 
        width=width, 
        height=height, 
        mode=mode, 
    )