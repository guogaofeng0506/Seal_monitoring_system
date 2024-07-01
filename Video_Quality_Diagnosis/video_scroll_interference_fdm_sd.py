"""
视频滚动干扰检测：帧差法+稳定性检测
"""
import cv2
import math
import time
import numpy as np


def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    # # 读取视频
    # cap = cv2.VideoCapture(video_stream_url)
    # # 确保视频流已打开
    # if not cap.isOpened():
    #     # print("无法打开视频流")
    #     return "失败"
    # else:
        # 获取帧率
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # print(f"视频流的帧率为: {fps} FPS")

        # 初始化参数
        frame_diff_threshold = 30  # 帧差异阈值
        stability_threshold = 10  # 稳定性阈值
        region_of_interest = (100, 100, 200, 200)  # 感兴趣区域的左上角和右下角坐标
        start_time = time.time()  # 记录开始时间

        # 用于存储异常帧的数量
        abnormal_frames = 0

        cn = 0
        while True:
            # 读取当前帧
            ret, frame = cap.read()
            if not ret:
                break
            if cn == 0:
                # 获取第一帧
                ret, prev_frame = cap.read()
                prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            else:
                cn += 1
                # 计算当前时间
                current_time = time.time()

                # 如果已经处理超过1秒，则退出循环
                if current_time - start_time > dtime:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # 计算帧间差异
                frame_diff = cv2.absdiff(prev_gray, gray)
                _, frame_diff_binary = cv2.threshold(frame_diff, frame_diff_threshold, 255, cv2.THRESH_BINARY)

                # 计算感兴趣区域内像素平均灰度值的稳定性
                roi = gray[region_of_interest[1]:region_of_interest[3], region_of_interest[0]:region_of_interest[2]]
                mean_intensity = np.mean(roi)

                # 判断帧差异和稳定性是否超过阈值
                if np.mean(frame_diff_binary) > frame_diff_threshold and abs(
                        mean_intensity - prev_mean_intensity) > stability_threshold:
                    abnormal_frames += 1

                # 更新上一帧的平均灰度值
                prev_mean_intensity = mean_intensity

                # 更新上一帧
                prev_gray = gray.copy()

            cap.release()

        # 返回结果
        # print(f"abnormal_frames: {abnormal_frames}")
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