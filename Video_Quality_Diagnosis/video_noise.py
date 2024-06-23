"""
(1) 视频抽帧并转换为灰度图像并分割为16*16的子块；
(2) 对每个子块计算方差，并找出最大和最小方差；
(3) 计算信噪比（SNR）和峰值信噪比（PSNR）；
(4) 设置两个阈值，分别用于判定最大与最小方差之差、峰值信噪比是否超出或低于其阈值，判定是否出现视频噪声。
调参
"""
import cv2
import time
import math
import numpy as np

def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    # # 读取视频文件
    # #global max_variance, min_variance
    # cap = cv2.VideoCapture(video_stream_url)  # 打开视频文件
    # if not cap.isOpened():
    #     # print("无法打开视频流")
    #     return "失败"
    # else:
        # 获取帧率
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # print(f"视频流的帧率为: {fps} FPS")

        # 定义子块大小
        block_size = 16

        # 定义阈值
        variance_threshold = 1000 # 方差阈值, 用于判断视频是否出现噪声, 如果方差大于该阈值, 则认为视频出现噪声, 一般情况下, 方差越大, 说明视频质量越好。
        psnr_threshold = 20 # 信噪比阈值, 一般设置为 30, 用于判断视频是否出现噪声, 如果信噪比小于该阈值, 则认为视频出现噪声, 一般情况下, 信噪比越大, 说明视频质量越好。

        # 初始化帧计数器
        noise_frames = 0
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

            # 转换为灰度图像
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 获取图像尺寸
            h, w = gray.shape

            # 将图像分割为子块
            for i in range(0, h, block_size):
                for j in range(0, w, block_size):
                    block = gray[i:i+block_size, j:j+block_size]

                    # 计算子块的方差
                    variance = np.var(block)

                    # 更新最大和最小方差
                    if 'max_variance' not in locals() or variance > max_variance:
                        max_variance = variance
                    if 'min_variance' not in locals() or variance < min_variance:
                        min_variance = variance

            # 计算信噪比（SNR）
            noise = np.var(gray) - min_variance # 计算噪声方差
            snr = 10 * np.log10(np.var(gray) / noise)   # 计算信噪比

            # 计算峰值信噪比（PSNR）
            psnr = cv2.PSNR(gray, gray)

            # 判断是否出现视频噪声
            if max_variance - min_variance > variance_threshold and psnr < psnr_threshold:
                noise_frames += 1

        cap.release()

        # print(f"noise_frames: {noise_frames}")

        # 返回结果
        prewarn_threshold = math.ceil(prewarn_threshold * fps / 100)
        warn_threshold = math.floor(warn_threshold * fps / 100)
        if noise_frames > warn_threshold:
            return "报警"
        elif warn_threshold > noise_frames > prewarn_threshold:
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