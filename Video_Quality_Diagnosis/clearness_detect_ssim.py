"""
计算视频帧的SSIM值, 用于检测视频帧的清晰度
目前效果最好
"""
import cv2
import time
import math
from skimage.metrics import structural_similarity as ssim

def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):

    # 获取帧率
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # print(f"视频流的帧率为: {fps} FPS")

    # 设置SSIM阈值
    ssim_low_threshold = 0.90
    ssim_high_threshold = 0.95

    # 初始化参数
    start_time = time.time()
    fram_warn_count = 0
    frame_prewarn_count = 0
    frame_normal_count = 0



    cn = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if cn == 0:
            _, ref_frame = cap.read()
            ref_frame_gray = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2GRAY)  # 将参考帧转换为灰度图像
        else:
            cn += 1
            # 计算当前时间
            current_time = time.time()

            # 如果已经处理超过1秒，则退出循环
            if current_time - start_time > dtime:
                break

            # 计算SSIM值
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    # 将视频帧转换为灰度图像
            score, _ = ssim(ref_frame_gray, frame_gray, full=True)  # 计算SSIM值，ssim值越大，图像越清晰


            # 返回诊断结果
            if score < ssim_low_threshold:
                fram_warn_count += 1
                # return "帧报警"
            elif ssim_low_threshold < score < ssim_high_threshold:
                frame_prewarn_count += 1
                # return "帧预警"
            else:
                frame_normal_count += 1
                # return "帧正常"

        # 释放视频捕获对象
        cap.release()

    # 统计诊断结果
    prewarn_thres = math.ceil(fps * prewarn_threshold / 100)
    warn_thres = math.floor(fps * warn_threshold / 100)
    if fram_warn_count > warn_thres:
        return "报警"
    elif warn_thres > frame_prewarn_count > prewarn_thres:
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