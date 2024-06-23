from Video_Quality_Diagnosis import avg_brightness_gaussian, clearness_detect_ssim, scene_change_detected_init, stripe_interference_fft
# import avg_brightness_gaussian, clearness_detect_ssim, scene_change_detected_init, stripe_interference_fft
from Video_Quality_Diagnosis import video_color_cast, video_contrast_anomaly, video_frame_loss, video_freeze, video_occlusion
# import video_color_cast, video_contrast_anomaly, video_frame_loss, video_freeze, video_occlusion
# import video_horizontal_stripes_detect_fdm, video_horizontal_waves_detect, video_jitter_lucas
from Video_Quality_Diagnosis import video_horizontal_stripes_detect_fdm, video_horizontal_waves_detect, video_jitter_lucas
# import video_scroll_interference_fdm_sd,video_noise
from  Video_Quality_Diagnosis import  video_scroll_interference_fdm_sd,video_noise
import cv2
from datetime import datetime

# 视频质量诊断系统
class VQD:
    """
    视频质量诊断系统, 用于检测视频质量异常, 并将检测结果插入数据库
    """
    # 初始化
    def __init__(self, data1, data2):
        """
        初始化视频质量诊断系统
        data= [{'id':'1','name':'1','rtsp':'123'},{'id':'2','name':'2','rtsp':'123'}]
        """
        self.data1 = data1                                                          # 视频流数据
        self.data2 = data2                                                          # 视频流数据
        self.warn_threshold = None                                                  # 报警阈值
        self.prewarn_threshold = None                                               # 预警阈值
        self.brightness_detection = avg_brightness_gaussian                         # 亮度异常检测
        self.clearness_detection = clearness_detect_ssim                            # 清晰度异常检测
        self.scene_change_detection = scene_change_detected_init                    # 场景变化检测
        self.stripe_interference_detection = stripe_interference_fft                # 条纹干扰检测
        self.color_cast_detection = video_color_cast                                # 偏色检测
        self.contrast_anomaly_detection = video_contrast_anomaly                    # 对比度异常检测
        self.frame_loss_detection = video_frame_loss                                # 视频丢失检测
        self.freeze_detection = video_freeze                                        # 视频冻结检测
        self.occlusion_detection = video_occlusion                                  # 视频遮挡检测
        self.horizontal_stripes_detection = video_horizontal_stripes_detect_fdm     # 横波干扰检测
        self.horizontal_waves_detection = video_horizontal_waves_detect             # 横纹干扰检测
        self.jitter_detection = video_jitter_lucas                                  # 抖动检测
        self.scroll_interference_detection = video_scroll_interference_fdm_sd       # 滚动干扰检测
        self.noise_detection = video_noise                                          # 噪声检测

    # 视频质量诊断
    def detection(self):
        """
        调用各诊断程序进行视频质量诊断
        """
        det_data = []  # 诊断数据
        for data1 in self.data1:
            video_stream_url = data1['rtsp']  # 视频流地址
            # print(f"{video_stream_urls}")
            for data2 in self.data2:
                if data1['id'] == data2['id'] and cv2.VideoCapture(data1["rtsp"]).isOpened():
                    prewarn_threshold, warn_threshold, cap = data2['prewarn_threshold'], data2['warn_threshold'], cv2.VideoCapture(data1["rtsp"])
                    diagnosis_data = [
                            self.jitter_detection.run(cap, prewarn_threshold,warn_threshold) if "视频抖动" in data2["name"] else "",
                            self.stripe_interference_detection.run(cap, prewarn_threshold,warn_threshold) if "条纹干扰" in data2["name"] else "",
                            self.frame_loss_detection.run(cap, prewarn_threshold,warn_threshold) if "视频丢失" in data2["name"] else "",
                            self.occlusion_detection.run(cap, prewarn_threshold,warn_threshold) if "视频遮挡" in data2["name"] else "",
                            self.freeze_detection.run(cap, prewarn_threshold,warn_threshold) if "视频冻结" in data2["name"] else "",
                            self.brightness_detection.run(cap, prewarn_threshold,warn_threshold)[0] if "高亮度" in data2["name"] else "",
                            self.brightness_detection.run(cap, prewarn_threshold,warn_threshold)[1] if "低亮度" in data2["name"] else "",
                            self.noise_detection.run(cap, prewarn_threshold,warn_threshold) if "视频噪声" in data2["name"] else "",
                            self.color_cast_detection.run(cap, prewarn_threshold,warn_threshold) if "偏色" in data2["name"] else "",
                            self.clearness_detection.run(cap, prewarn_threshold,warn_threshold) if "清晰度" in data2["name"] else "",
                            self.scene_change_detection.run(cap, prewarn_threshold,warn_threshold) if "场景变化" in data2["name"] else "",
                            self.contrast_anomaly_detection.run(cap, prewarn_threshold,warn_threshold) if "对比度" in data2["name"] else "",
                            self.horizontal_waves_detection.run(cap, prewarn_threshold,warn_threshold) if "横纹干扰" in data2["name"] else "",
                            self.scroll_interference_detection.run(cap, prewarn_threshold,warn_threshold) if "滚动干扰" in data2["name"] else "",
                            self.horizontal_stripes_detection.run(cap, prewarn_threshold,warn_threshold) if "横波干扰" in data2["name"] else ""]

                    res_data = [data1["id"]] + [data1["name"]] + ["很差" if "报警" in diagnosis_data else
                                                                  "达标" if any(x == "正常" for x in diagnosis_data) and all(x in ["正常", ""] for x in diagnosis_data) else
                                                                  "一般"] + diagnosis_data
                    det_data.append(res_data)
                elif data1['id'] == data2['id'] and cv2.VideoCapture(data1["rtsp"]).isOpened() == False:
                    det_data.append([[data1["id"]]+[data1["name"]]+["失败"]+[""]*14])
        return det_data

    # 调用检测函数
    @staticmethod
    def run(data1, data2):
        """
        调用检测函数
        """
        vqd = VQD(data1, data2)  # 创建对象，参数为视频名称
        res = vqd.detection()  # 调用检测函数
        print("诊断完成！")
        return res

# if __name__ == "__main__":

    # print(datetime.now())
    # data1 = [{'id':'1','name':'监控点1','rtsp':'rtsp://admin:Pc@12138@192.168.7.77'}, {'id':'2','name':'监控点2','rtsp':'rtsp://admin:Pc@12138@192.168.7.31'}]
    # data2 = [{'id':'1','name':'场景变化','prewarn_threshold':30,'warn_threshold':70}, {'id':'2','name':'视频冻结','prewarn_threshold':30,'warn_threshold':70}]
    # res = VQD.run(data1, data2)
    # print(res)
    # print(datetime.now())