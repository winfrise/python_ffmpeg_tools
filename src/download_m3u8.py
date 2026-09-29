import subprocess
import os

def download_m3u8(m3u8_url, output_path):
    """
    下载并合并 m3u8 视频
    
    :param m3u8_url: m3u8 播放列表的 URL
    :param output_path: 最终 MP4 文件的保存路径（包含文件名）
    """
    # 1. 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. 构建 FFmpeg 命令
    cmd = [
        'ffmpeg', 
        '-i', m3u8_url, 
        '-c', 'copy',           # 直接复制音视频流，不重新编码，速度极快
        '-bsf:a', 'aac_adtstoasc', # 处理 AAC 音频兼容性，防止无声
        '-y',                    # 覆盖已存在的同名文件
        output_path
    ]

    print(f"🚀 开始下载: {m3u8_url}")
    print(f"💾 保存路径: {output_path}")

    # 3. 执行下载
    try:
        subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("✅ 下载并合并完成！")
    except subprocess.CalledProcessError as e:
        print(f"❌ 下载失败，错误信息:\n{e.stderr}")
    except FileNotFoundError:
        print("❌ 错误：未找到 ffmpeg，请确保已安装并配置到系统环境变量中。")

# --- 使用示例 ---
if __name__ == "__main__":
    url = "https://k0uday1dyb8y9azw2408x8722xc900x3xx1az.djvod.ndcimgs.com/vod-rt-remux/hls-ts/v0/REALTIME_REMUX_TS_4999/video-def/enc_5243879015455678287_b.mp4/5243879015455678287_7cf51140f8c64705_9636_hlsob.m3u8?x-ks-ptid=199118655772&x-kcdn-pid=12021&kwai-not-alloc=self-cdn&ocid=1100000215&kcdntag=p:Henan;i:ChinaUnicom;ft:UNKNOWN;h:UNKNOWN;pn:webserverHls&ss=vpm"  # 替换为你的 m3u8 链接
    save_path = "/Users/teacher/Desktop/百度网盘下载/11.mp4"    # 替换为你的保存路径
    
    download_m3u8(url, save_path)