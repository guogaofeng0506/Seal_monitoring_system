"""
视频横纹干扰诊断：通过计算光流，检测视频帧中是否存在横向波动，以判断视频是否受到横纹干扰。
当视频帧中的光流横向波动值超过阈值时，认为视频帧中存在横向波动，当横向波动的帧数占比超过25%时，认为视频受到横纹干扰。
"""
import cv2
import time
import numpy as np

# 横纹干扰检测
def detect_horizontal_waves(cap, threshold, dtime=1.0):
    # 帧计数
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # 用于计算横向运动的光流
    prev_frame = None
    horizontal_waves_frames = 0
    start_time = time.time()
    for _ in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        # 计算当前时间
        current_time = time.time()

        # 如果已经处理超过1秒，则退出循环
        if current_time - start_time > dtime:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_frame is not None:
            # 计算光流
            # 创建一个与prev_gray相同大小和类型的矩阵来存储光流数据,因光流是二维的（水平和垂直分量），所以需要两个通道
            flow = np.zeros((prev_frame.shape[0], prev_frame.shape[1], 2), dtype=np.float32)
            flow = cv2.calcOpticalFlowFarneback(prev_frame, gray_frame, flow, 0.5, 5, 20, 5, 5, 1.2, 0) # 计算光流，返回光流向量

            # 提取水平方向的运动
            flow_horizontal = flow[:,:,0]
            # 检查是否存在横向波动
            if np.max(flow_horizontal) > threshold:
                horizontal_waves_frames += 1
        prev_frame = gray_frame

    cap.release()

    abnormal_ratio = (horizontal_waves_frames / frame_count) * 100

    return abnormal_ratio


def run(cap, prewarn_threshold=30, warn_threshold=70,dtime=1.0):
    # 阈值，用于确定横向波动的存在
        threshold = 5.0
    # 检测横向波动
    # cap = cv2.VideoCapture(video_stream_url)
    # if not cap.isOpened():
    #     return "失败"
    # else:
        ratio = detect_horizontal_waves(cap, threshold, dtime=dtime)
        # print(f"横向波动帧数占比: {ratio:.2f}%")

        # 如果横向波动的帧数占比超过30%，则认为视频出现横纹干扰
        if ratio > warn_threshold:
            return "报警"        # 报警
        elif warn_threshold > ratio > prewarn_threshold:
            return "预警"        # 预警
        else:
            return "正常"        # 正常

if __name__ == "__main__":
    prewarn_threshold = 30
    warn_threshold = 70
    detect_time = 0.5
    print(run(cap=cv2.VideoCapture("rtsp://admin:Pc@12138@192.168.7.31"),
              prewarn_threshold=prewarn_threshold,
              warn_threshold=warn_threshold,
              dtime=detect_time))