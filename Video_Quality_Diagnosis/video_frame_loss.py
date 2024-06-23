"""
检测视频帧丢失：捕获视频帧。对于每一帧，它会计算当前帧与上一帧之间的时间差，然后与预期的帧间隔进行比较。
如果时间差超过了一个阈值（这里设置为0.01秒），则认为发生了帧丢失。最后输出检测到的帧丢失数量。
"""
import cv2
import time
import math

def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    # cap = cv2.VideoCapture(video_stream_url)      # 打开视频(摄像头，参数 0 表示第一个摄像头设备)
    #
    # if not cap.isOpened():  # 检查摄像头是否成功打开
    #     # print("视频丢失")
    #     return "失败"
    # else:
        # 获取帧率
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # print(f"视频流的帧率为: {fps} FPS")

        # 初始化参数
        last_frame_time = 0
        frame_losses = 0
        start_time = time.time()

        while True:
            ret, frame = cap.read()  # 读取摄像头图像
            if not ret:
                break
            # 计算当前时间
            current_time = time.time()

            # 如果已经处理超过1秒，则退出循环
            if current_time - start_time > dtime:
                break

            current_frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # 获取当前帧的时间
            if last_frame_time != 0:    # 如果不是第一帧
                time_diff = current_frame_time - last_frame_time    # 计算当前帧时间与上一帧时间的差值
                if time_diff > 0.05:  # 设置一个阈值，可以根据实际情况调整
                    frame_losses += 1   # 帧丢失数加 1

            last_frame_time = current_frame_time

        cap.release()

        # 返回结果
        prewarn_threshold = math.ceil(prewarn_threshold * fps / 100)
        warn_threshold = math.floor(warn_threshold * fps / 100)
        if frame_losses > warn_threshold:
            return "报警"
        elif warn_threshold > frame_losses > prewarn_threshold:
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