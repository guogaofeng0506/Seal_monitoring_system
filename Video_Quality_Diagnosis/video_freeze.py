"""
视频冻结检测: 通过比较连续帧之间的差异来检测视频中的冻结画面
(1) 每隔T帧从视频中取帧(防止相邻帧太相似引起误检)；
(2) 对所取的每帧求直方图；
(3) 求相邻2帧直方图的相似度；
(4) 当相似度大于A时认为帧差图像一致,当一致的帧差图像数达到B时认为画面发生冻结。
调节A与B的大小可以改变冻结检测的灵敏度。
"""
import cv2
import time
import math

# 计算帧的直方图
def compute_histogram(frame):
    hist = cv2.calcHist([frame], [0], None, [256], [0, 256])    # 计算帧的直方图
    hist = cv2.normalize(hist, hist).flatten()  # 归一化直方图
    return hist

# 计算帧之间的相似度
def compute_frame_similarity(hist1, hist2):
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)  # 计算帧之间的相似度
    return similarity

# 检测视频冻结
def run(cap, prewarn_threshold=30, warn_threshold=70, dtime=1.0):
    # cap = cv2.VideoCapture(video_stream_url)  # 打开视频文件
    # if not cap.isOpened():
    #     return "失败"
    # else:
        # 获取帧率
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # print(f"视频流的帧率为: {fps} FPS")

        # 初始化参数
        T = 25  # 每隔 T 帧取一帧
        A = 0.999 # 相似度阈值
        B = 30  # 连续 B 帧冻结判定为冻结
        hist1 = None    # 初始化帧的直方图
        freeze_count = 0    # 初始化冻结帧计数器
        freeze_frame = 0     # 初始化冻结帧
        start_time = time.time()    # 记录开始时间

        while True:    # 开始循环，用于逐帧处理视频
            ret, frame = cap.read()   # 读取视频的一帧
            if not ret:
                break
            # 计算当前时间
            current_time = time.time()

            # 如果已经处理超过1秒，则退出循环
            if current_time - start_time > dtime:
                break

            if cap.get(cv2.CAP_PROP_POS_FRAMES) % T == 0:   # 每隔 T 帧取一帧
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将读取到的帧转换为灰度图像
                hist2 = compute_histogram(gray)   # 计算帧的直方图
                if hist1 is not None:   # 如果不是第一帧
                    similarity = compute_frame_similarity(hist1, hist2)  # 计算帧之间的相似度
                    if similarity > A:  # 如果相似度大于阈值 A
                        freeze_count += 1   # 冻结帧计数器加一
                        # print(similarity)
                    else:
                        freeze_count = 0    # 冻结帧计数器清零

                    if freeze_count >= B:   # 如果连续 B 帧冻结
                        # print(f"视频帧发生冻结，帧数：{cap.get(cv2.CAP_PROP_POS_FRAMES) - B + 1} 至 {cap.get(cv2.CAP_PROP_POS_FRAMES)}")
                        freeze_frame += 1
                    else:
                        # print("视频帧未发生冻结")
                        freeze_frame += 0
                hist1 = hist2
        cap.release()
        # print(freeze_frame)
        prewarn_threshold = math.ceil(prewarn_threshold * fps / 100)
        warn_threshold = math.floor(warn_threshold * fps / 100)
        if freeze_frame > warn_threshold:    # 如果视频中冻结画面累计达到报警阈值
            return "报警"
        elif warn_threshold > freeze_frame > prewarn_threshold:  # 如果视频中冻结画面累计达到预警阈值
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

