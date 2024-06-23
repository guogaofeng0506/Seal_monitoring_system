"""
(1) 视频逐帧抽图；
(2) 将每帧图像从RGB色彩空间转换到HSV色彩空间以提取色度分量H；
(3) 计算色度分量H的直方图；
(4) 找到直方图中的最大bin，并计算其占整个直方图的比例；
(5) 将这个比例作为偏色值，并可能根据阈值来判断是否存在偏色。

"""

import cv2
import time
import math
import numpy as np

# 计算偏色值
def calculate_color_cast(frame):
    # Convert frame from RGB to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Extract hue component
    hue = hsv_frame[:,:,0]
    # Calculate histogram of hue component
    hist = cv2.calcHist([hsv_frame],[0],None,[256],[0,256])
    # Find bin with maximum value
    max_bin = np.argmax(hist)
    # Calculate proportion of max bin to entire histogram
    max_bin_ratio = hist[max_bin] / np.sum(hist)
    return max_bin_ratio[0]

# 诊断视频是否出现偏色
def run(cap,prewarn_thres=30, warn_thres=70, dtime=1.0):

    # 获取帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # print(f"视频流的帧率为: {fps} FPS")

    # 初始化参数
    abnormal_frames = 0
    color_bias_threshold = 0.5
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # 计算当前时间
        current_time = time.time()

        # 如果已经处理超过1秒，则退出循环
        if current_time - start_time > dtime:
            break

        color_cast = calculate_color_cast(frame)
        if color_cast > color_bias_threshold:
            abnormal_frames += 1

    cap.release()

    prewarn_threshold = math.ceil(prewarn_thres * fps / 100)
    warn_threshold = math.floor(warn_thres * fps / 100)
    if abnormal_frames > warn_threshold:
        return "报警"
    elif warn_threshold > abnormal_frames > prewarn_threshold:
        return "预警"
    else:
        return "正常"

if __name__ == "__main__":
    prewarn_threshold = 30
    warn_threshold = 70
    detect_time = 0.5
    print(run(cap=cv2.VideoCapture("rtsp://admin:Pc@12138@192.168.7.31"),
              prewarn_thres=prewarn_threshold,
              warn_thres=warn_threshold,
              dtime=detect_time))