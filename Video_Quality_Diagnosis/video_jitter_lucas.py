"""
(1) 每隔N帧取一帧；
(2) 对取到的每帧进行特征点提取；
(3) 对检测的相邻2帧进行特征点匹配，得到匹配矩阵；
(4) 设置阈值A与B，当匹配矩阵大于A时认为这2帧画面有抖动，当抖动帧数大于B时认为视频抖动异常。

改进：使用Lucas-Kanade光流方法来跟踪运动物体，从而减少匹配时受到运动物体影响的情况。

"""
import cv2
import time
import math
import numpy as np

def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    # cap = cv2.VideoCapture(video_stream_url)
    #
    # # 确保视频流已打开
    # if not cap.isOpened():
    #     # print("无法打开视频流")
    #     return "失败"
    # else:
        # 获取帧率
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # print(f"视频流的帧率为: {fps} FPS")

        N = 5   # 设置帧间隔
        frame_count = 0 # 累计帧数（用于每隔N帧取图）

        A = 10 # 设置特征差异阈值  100 -> 10   越小越敏感
        B = 3  # 设置抖动帧数阈值
        # warn_thres = 3  # 预警阈值

        jitter_frames = 0   # 抖动帧数
        abnormal_frames_count = 0   # 异常帧数


        prev_frame = None   # 上一帧
        prev_pts = None    # 上一帧的特征点

        lk_params = dict(winSize=(15, 15),
                         maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))  # 设置Lucas-Kanade光流法的参数

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

            frame_count += 1
            if frame_count % N != 0:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is None:  # 第一帧
                prev_frame = gray.copy()    # 将当前帧赋值给prev_frame
                prev_pts = cv2.goodFeaturesToTrack(prev_frame, mask=None, maxCorners=200, qualityLevel=0.01, minDistance=30)    # 使用Shi-Tomasi角点检测算法检测角点
                continue

            # Calculate optical flow
            next_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_frame, gray, prev_pts, None, **lk_params)   # 使用Lucas-Kanade光流法计算特征点的新位置

            # Select good points
            good_new = next_pts[status == 1]    # 选取光流法计算出的特征点中的好的特征点
            good_old = prev_pts[status == 1]    # 选取光流法计算出的特征点中的好的特征点

            # Calculate the difference in points
            diff = np.linalg.norm(good_new - good_old, axis=1).mean()   # 计算特征点的差异
            # print(diff)

            if diff > A:
                jitter_frames += 1      # 抖动帧数加一
            else:
                jitter_frames = 0       # 抖动帧数清零
            if jitter_frames > B:
                # print("视频抖动异常！")
                abnormal_frames_count += 1  # 报警异常
                # break


            prev_frame = gray.copy()
            prev_pts = cv2.goodFeaturesToTrack(prev_frame, mask=None, maxCorners=200, qualityLevel=0.01, minDistance=30)

        # 释放资源
        cap.release()

        # print(abnormal_frames_count)

        # 返回结果
        prewarn_threshold = math.ceil(prewarn_threshold * fps / 100)
        warn_threshold = math.floor(warn_threshold * fps / 100)
        if abnormal_frames_count > warn_threshold:
            return "报警"
        elif warn_threshold >= abnormal_frames_count > prewarn_threshold:
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