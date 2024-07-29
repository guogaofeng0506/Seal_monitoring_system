"""
场景变换检测: 计算初始帧与后续帧的差异，当差异超过设定的阈值时，认为场景发生变化
"""
import cv2
import time
import math
import numpy as np
from collections import deque

# 场景变化检测
def run(cap, prewarn_frame_thres=30, warn_frame_thres=70, dtime=1.0):
    # 获取帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # print(f"视频流的帧率为: {fps} FPS")

    # 初始化参数
    frame_sum = 0
    prewarn_change_thresh = 60
    warn_change_thresh = 80
    prewarn_frame = 0
    warn_frame = 0
    start_time = time.time()

    # 初始化背景建模器
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)   # 创建背景建模器

    # 用于存储最近几帧的变化值，以平滑处理
    change_buffer = deque(maxlen=fps)    # 创建一个双向队列，用于存储最近 N 帧的变化值

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 计算当前时间
        current_time = time.time()

        # 如果已经处理超过1秒，则退出循环
        if current_time - start_time > dtime:
            break

        frame = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)   # 缩小帧尺寸，加快处理速度
        frame_sum += 1

        if frame_sum == 1:
            bg_subtractor.apply(frame)  # 初始化背景建模器
            continue

        fg_mask = bg_subtractor.apply(frame)    # 使用背景建模器获取前景掩码
        fg_mask[fg_mask < 240] = 0
        fg_mask[fg_mask >= 240] = 255

        # 计算当前帧的变化值
        change_value = np.sum(fg_mask) / (fg_mask.shape[0] * fg_mask.shape[1])  # 计算前景的亮度均值
        change_buffer.append(change_value)          # 将变化值添加到双向队列中

        # 累积变化值超过预警阈值时触发预警
        if sum(change_buffer) > prewarn_change_thresh * len(change_buffer):
            prewarn_frame += 1
            change_buffer.clear()   # 清空双向队列

        # 累积变化值超过报警阈值时触发报警
        if sum(change_buffer) > warn_change_thresh * len(change_buffer):
            warn_frame += 1
            change_buffer.clear()

    cap.release()

    prewarn_frame_thres = math.ceil(prewarn_frame_thres * fps / 100)
    warn_frame_thres = math.floor(warn_frame_thres * fps / 100)

    if warn_frame > warn_frame_thres:
        return "报警"
    elif warn_frame_thres > prewarn_frame > prewarn_frame_thres:
        return "预警"
    else:
        return "正常"

if __name__ == '__main__':
    video_stream_url = "rtsp://admin:Pc@12138@192.168.7.31"
    print(run(cv2.VideoCapture(video_stream_url)))