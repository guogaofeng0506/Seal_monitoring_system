"""
视频对比度异常检测： 先计算图片在灰度图上的均值和方差，当存在异常时，均值会偏离均值点(可以假设为128)，方差也会偏小，通过计算灰度图的均值和方差，
就可评估图像是否存在对比度异常情况。
"""
import cv2
import time
import math
import numpy as np

def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):

    # 获取帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # print(f"视频流的帧率为: {fps} FPS")


    # 定义均值点和方差阈值
    mean_threshold = 128
    variance_threshold = 1000

    # 定义异常帧计数器
    abnormal_frames = 0

    start_time = time.time()

    while True:
        # 读取一帧
        ret, frame = cap.read()

        # 检查是否成功读取帧
        if not ret:
            break
        # 计算当前时间
        current_time = time.time()

        # 如果已经处理超过1秒，则退出循环
        if current_time - start_time > dtime:
            break

        # 转换为灰度图像
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 计算均值和方差
        mean_value = np.mean(gray_frame)
        variance_value = np.var(gray_frame)
        # print(mean_value, variance_value)     # 111+, 3000+

        # 判断是否存在对比度异常
        if abs(mean_value - mean_threshold) > 20 and variance_value < variance_threshold:
            # print("Contrast anomaly detected in frame.")
            abnormal_frames += 1

    # 释放视频对象
    cap.release()

    # 返回结果
    prewarn_threshold = math.ceil(prewarn_threshold * fps / 100)
    warn_threshold = math.floor(warn_threshold * fps / 100)
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
              prewarn_threshold=prewarn_threshold,
              warn_threshold=warn_threshold,
              dtime=detect_time))