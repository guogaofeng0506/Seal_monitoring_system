"""
视频横波干扰诊断：帧差法（Frame Difference Method）计算帧间差异，判断是否存在横波干扰
"""
import cv2
import time
import math
import numpy as np

def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    # # 读取视频文件
    # cap = cv2.VideoCapture(video_stream_url)
    # if not cap.isOpened():
    #     return "失败"
    # else:
        # 获取帧率
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # 用于存储异常帧的数量
        abnormal_frames = 0

        # 用于存储每个帧的灰度图像
        prev_gray = None

        # 记录开始时间
        start_time = time.time()

        # 读取视频帧并进行处理
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 计算当前时间
            current_time = time.time()

            # 如果已经处理超过1秒，则退出循环
            if current_time - start_time > dtime:
                break

            # 将帧转换为灰度图像
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 计算帧间差异
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)

                # 计算帧间差异的均值作为干扰程度的指标
                mean_diff = np.mean(diff)

                # 设置阈值，判断是否存在横波干扰
                if mean_diff > 10:  # 适当调整阈值
                    abnormal_frames += 1
            prev_gray = gray

        # 释放视频捕获对象
        cap.release()

        # 根据异常帧数量判断视频质量
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