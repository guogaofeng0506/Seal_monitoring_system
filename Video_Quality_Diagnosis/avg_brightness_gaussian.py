"""
创建背景减法器来计算每一帧的前景掩码，然后计算前景的亮度均值，如果亮度均值超过阈值，则认为是亮度异常。
目前效果较好，阈值待优化。
"""
import cv2
import time
import math

def analyze_one_second(cap, prewarn_threshold, warn_threshold, dtime):
    # 创建背景建模器
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    # 获取帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # print(f"视频流的帧率为: {fps} FPS")

    # 初始化参数
    start_time = time.time()
    frame_count = 0
    brightness_frame_count = 0
    darkness_frame_count = 0

    brightness_threshold = 150
    darkness_threshold = 50

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 计算当前时间
        current_time = time.time()

        # 如果已经处理超过1秒，则退出循环
        if current_time - start_time > dtime:
            break

        # 使用背景建模器获取前景掩码
        fg_mask = bg_subtractor.apply(frame)

        # 计算前景的亮度均值
        fg_pixels = frame[fg_mask > 0]
        if fg_pixels.size == 0:
            fg_brightness = 0
        else:
            fg_brightness = fg_pixels.mean()

        # 检测亮度异常
        if fg_brightness > brightness_threshold:
            brightness_frame_count += 1
        elif fg_brightness < darkness_threshold:
            darkness_frame_count += 1

        # 增加帧计数器
        frame_count += 1

    # 释放资源
    cap.release()

    # 返回结果
    prewarn_threshold = math.ceil(prewarn_threshold * fps / 100)
    warn_threshold = math.floor(warn_threshold * fps / 100)
    # print(f"prewarn_threshold: {prewarn_threshold}, warn_threshold: {warn_threshold}")
    if prewarn_threshold < brightness_frame_count < warn_threshold:
        return "过亮预警"
    elif brightness_frame_count > warn_threshold:
        return "过亮报警"
    elif prewarn_threshold < darkness_frame_count < warn_threshold:
        return "过暗预警"
    elif darkness_frame_count > warn_threshold:
        return "过暗报警"
    elif brightness_frame_count <= prewarn_threshold and darkness_frame_count <= prewarn_threshold:
        return "正常"

# 运行函数
def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    result = analyze_one_second(cap, prewarn_threshold, warn_threshold, dtime)
    if result == "过亮预警":
        return "预警", "正常"
    elif result == "过亮报警":
        return "报警", "正常"
    elif result == "过暗预警":
        return "正常", "预警"
    elif result == "过暗报警":
        return "正常", "报警"
    elif result == "正常":
        return "正常", "正常"

if __name__ == "__main__":
    prewarn_threshold = 30
    warn_threshold = 70
    detect_time = 0.5
    print(run(cap= cv2.VideoCapture("rtsp://admin:Pc@12138@192.168.7.77"),prewarn_threshold=prewarn_threshold,
              warn_threshold=warn_threshold,
              dtime=detect_time)[0])