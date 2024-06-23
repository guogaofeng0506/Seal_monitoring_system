"""
视频遮挡检测：通过查找前景中的最大连通区域，计算遮挡率，判断视频中是否存在遮挡异常。
"""
import cv2
import math
import time

# 视频遮挡检测
def frame_processing(frame):
    # 转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 二值化处理
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)    # 可根据实际情况调整二值化阈值
    return binary

def calculate_mask_rate(binary):
    # 查找前景中的连通区域
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)      # 查找轮廓
    # 找到最大的连通区域
    max_area = 0
    for contour in contours:    # 遍历所有连通区域
        area = cv2.contourArea(contour)    # 计算连通区域的面积
        if area > max_area:    # 找到最大的连通区域
            max_area = area   # 更新最大面积
    # 计算遮挡率
    total_area = binary.shape[0] * binary.shape[1]  # 计算总面积
    mask_rate = max_area / total_area   # 计算遮挡率
    return mask_rate

def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    # # 视频读取
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

        # 帧图像遮挡次数
        abnormal_frames = 0

        # 记录开始时间
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

            # 逐帧处理
            binary = frame_processing(frame)
            mask_rate = calculate_mask_rate(binary)

            # 设置阈值，判断是否出现遮挡异常
            threshold = 0.5
            if mask_rate > threshold:
                abnormal_frames += 1
            else:
                abnormal_frames += 0
        cap.release()   # 释放 VideoCapture 对象

        # 返回结果
        # print(f"遮挡帧数: {abnormal_frames}")
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