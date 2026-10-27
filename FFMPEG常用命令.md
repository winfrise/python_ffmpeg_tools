## ffmpeg提取音乐

###  提取为 MP3 格式

```
ffmpeg -i "/Users/teacher/Downloads/未命名文件夹/下载 (1).mp4" -vn -acodec libmp3lame -ab 192k output.mp3
```