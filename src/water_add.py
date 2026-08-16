import subprocess
import os

def add_multiple_watermarks(
    input_video: str, 
    output_video: str, 
    watermarks: list[dict], 
    default_font_path: str = "simhei.ttf"
) -> None:
    """
    支持同时添加多个文字水印，包含水平垂直居中及位置偏移功能
    
    :param input_video: 输入视频路径
    :param output_video: 输出视频路径
    :param watermarks: 水印配置列表，每个元素是一个字典
                       新增 offset 参数: (x_offset, y_offset)
    :param default_font_path: 默认字体路径
    """
    
    # 1. 位置映射逻辑
    def get_position_xy(pos: str):
        # 基础坐标表达式，不包含偏移
        pos_map = {
            "top_left":     "x=10:y=10",
            "top_right":    "x=w-tw-10:y=10",
            "bottom_left":  "x=10:y=h-th-10",
            "bottom_right": "x=w-tw-10:y=h-th-10",
            "center":       "x=(w-tw)/2:y=(h-th)/2"
        }
        return pos_map.get(pos, "x=10:y=10") 

    filter_parts = []

    # 2. 遍历配置生成滤镜链
    for wm in watermarks:
        text = wm.get("text", "")
        position = wm.get("position", "bottom_right")
        custom_xy = wm.get("custom_xy")
        offset = wm.get("offset", (0, 0))  # 获取偏移量，默认为 (0, 0)
        font_size = wm.get("font_size", 24)
        font_color = wm.get("font_color", "white")
        font_path = wm.get("font_path", default_font_path)

        # 处理坐标逻辑
        if custom_xy:
            # 如果是绝对坐标，直接加上偏移
            x_val = custom_xy[0] + offset[0]
            y_val = custom_xy[1] + offset[1]
            xy_str = f"x={x_val}:y={y_val}"
        else:
            # 如果是预设位置，在基础表达式上追加偏移计算
            base_xy = get_position_xy(position)
            x_offset, y_offset = offset
            
            # 构建带偏移的表达式，例如：x=10+20:y=10-5
            # 这里直接拼接字符串，利用 FFmpeg 的表达式计算能力
            xy_str = f"{base_xy}+{x_offset}:{base_xy.split(':')[-1].split('=')[1]}+{y_offset}"
            # 上面那行逻辑有点绕，为了代码可读性，我们换一种更清晰的写法：
            base_x_expr = base_xy.split(':')[0].split('=')[1] # 获取 "10" 或 "w-tw-10"
            base_y_expr = base_xy.split(':')[1].split('=')[1] # 获取 "10" 或 "h-th-10"
            
            # 重新组合，加上偏移量
            # 注意：如果偏移量是负数，这里会变成 "10+-5"，FFmpeg 也能识别，但为了美观可以处理一下
            x_op = "+" if x_offset >= 0 else ""
            y_op = "+" if y_offset >= 0 else ""
            
            xy_str = f"x={base_x_expr}{x_op}{x_offset}:y={base_y_expr}{y_op}{y_offset}"

        # 构建单个 drawtext 滤镜字符串
        filter_str = (
            f"drawtext="
            f"text='{text}':"
            f"fontfile='{font_path}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"{xy_str}"
        )
        filter_parts.append(filter_str)

    # 3. 使用逗号连接多个滤镜
    vf_string = ",".join(filter_parts)

    # 4. 构建并执行命令
    cmd = [
        "ffmpeg", "-y", 
        "-i", input_video,
        "-vf", vf_string,
        "-c:a", "copy",
        output_video
    ]

    print(f"正在执行命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"成功！水印已添加至: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 执行失败: {e}")




if __name__ == "__main__":
    input_video = "/Volumes/西数4T外置/ffmpeg_output/test.mp4"
    output_video = "/Volumes/西数4T外置/ffmpeg_output/test_222.mp4"
    font_path ="/Users/teacher/Library/Fonts/FZDHTJW.TTF"
    font_color="white@0.8"  # 80% 透明度的白色

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
        default_font_path=font_path # 记得替换为你电脑里的字体路径
    )




