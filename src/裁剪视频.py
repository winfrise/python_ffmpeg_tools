import os
from tqdm import tqdm
from ffmpeg_progress_yield import FfmpegProgress

def crop_video(input_path, output_path, crop_params):
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    top = crop_params.get('top', 0)
    bottom = crop_params.get('bottom', 0)
    left = crop_params.get('left', 0)
    right = crop_params.get('right', 0)
    crop_filter = f"crop=iw-{left}-{right}:ih-{top}-{bottom}:{left}:{top}"

    # 构建 FFmpeg 命令列表（注意：这里用列表而不是字符串）
    cmd = [
        'ffmpeg', 
        '-i', input_path, 
        '-vf', crop_filter,
        '-c:v', 'libx264', 
        '-crf', '18',
        '-preset', 'medium',
        '-c:a', 'copy',
        '-y', 
        output_path
    ]

    print(f"✂️ 开始裁剪: {input_path}")
    
    # 核心：使用 FfmpegProgress 包装命令，并配合 tqdm 显示进度条
    with FfmpegProgress(cmd) as ff:
        with tqdm(total=100, desc="裁剪进度", unit="%") as pbar:
            for progress in ff.run_command_with_progress():
                pbar.update(progress - pbar.n)
                
    print("✅ 视频裁剪完成！")
# --- 使用示例 ---
if __name__ == "__main__":
    input_video = "/Users/teacher/Desktop/百度网盘下载/11.mp4"

    base_name, ext = os.path.splitext(input_video)

    output_video = f"{base_name}_output_裁剪{ext}"
    
    # 设定裁剪距离（单位：像素）
    params = {
        'top': 50,
        'bottom': 0,
        'left': 0,
        'right': 0
    }
    
    crop_video(input_video, output_video, params)