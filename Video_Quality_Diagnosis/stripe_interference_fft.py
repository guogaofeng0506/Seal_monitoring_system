"""
条纹干扰检测：将从视频读取到的帧转化为灰度图像，进行傅里叶变换，计算频谱图的幅度谱，并对其进行对数变换以增强显示效果。
设置并调节阈值大小，进行条纹干扰检测。频域图像中幅度值大于该阈值的区域被认为是条纹干扰。
"""
import cv2
import time
import math
import numpy as np

# 条纹干扰检测
def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):

    # 获取帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # print(f"视频流的帧率为: {fps} FPS")

    # 初始化参数
    abnormal_frames = 0
    start_time = time.time()

    while True:     #开始循环，用于逐帧处理视频
        ret, frame = cap.read()     #读取视频的一帧，ret 表示读取是否成功，frame 是读取到的帧。
        if not ret:
            break

        # 计算当前时间
        current_time = time.time()

        # 如果已经处理超过1秒，则退出循环
        if current_time - start_time > dtime:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #将读取到的帧转换为灰度图像
        f = np.fft.fft2(gray)   #对灰度图像进行傅里叶变换
        fshift = np.fft.fftshift(f) #将零频率分量移到频谱中心
        magnitude_spectrum = 20 * np.log(np.abs(fshift))    #计算频谱图的幅度谱，并对其进行对数变换以增强显示效果。
        # print(magnitude_spectrum)

        threshold = 1000      #设置一个阈值，用于检测条纹干扰。频域图像中幅度值大于该阈值的区域被认为是条纹干扰。
        interference_mask = magnitude_spectrum > threshold
        # print(interference_mask)

        if np.any(interference_mask):  # 如果发生条纹干扰
            abnormal_frames += 1
    cap.release()  # 释放 VideoCapture 对象


    prewarn_threshold = math.ceil(prewarn_threshold * fps / 100)
    warn_threshold = math.floor(warn_threshold * fps / 100)
    if abnormal_frames > warn_threshold: # 如果视频中有条纹干扰
        return "报警"
    elif warn_threshold > abnormal_frames > prewarn_threshold: # 如果视频中的条纹干扰帧数超过预警阈值
        return "预警"
    else:
        return "正常"

if __name__ == '__main__':
    prewarn_threshold = 30
    warn_threshold = 70
    detect_time = 0.5
    print(run(cap=cv2.VideoCapture("rtsp://admin:Pc@12138@192.168.7.31"),
              prewarn_threshold=prewarn_threshold,
              warn_threshold=warn_threshold,
              dtime=detect_time))
