from  Video_Quality_Diagnosis import avg_brightness_gaussian, clearness_detect_ssim, scene_change_detected_init, stripe_interference_fft
from  Video_Quality_Diagnosis import video_color_cast, video_contrast_anomaly, video_frame_loss, video_freeze, video_occlusion
from  Video_Quality_Diagnosis import video_contrast_anomaly, video_frame_loss, video_freeze, video_occlusion
from  Video_Quality_Diagnosis import video_horizontal_stripes_detect_fdm, video_horizontal_waves_detect, video_jitter_lucas
from  Video_Quality_Diagnosis import video_scroll_interference_fdm_sd,video_noise
import cv2

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
        det_list = []
        for data2 in self.data2:
            det_list.append(data2['name'])
        # print(f"检测项目为{det_list}")
        prewarn_threshold, warn_threshold = [int(self.data2[i]['prewarn_threshold']) for i in range(len(self.data2))], \
                                            [int(self.data2[i]['warn_threshold']) for i in range(len(self.data2))]
        # print(f"监控点的预警阈值为{prewarn_threshold}, 报警阈值为{warn_threshold}")

        for data1 in self.data1:
            video_stream_url = data1['rtsp']  # 视频流地址
            # print(f"{video_stream_urls}")
            if cv2.VideoCapture(video_stream_url).isOpened():
                cap = cv2.VideoCapture(video_stream_url)
                # print(cap, prewarn_threshold[13], warn_threshold[13])
                diagnosis_data = [
                    self.jitter_detection.run(cap, prewarn_threshold[0],warn_threshold[0]) if "视频抖动" in det_list else "",
                    self.stripe_interference_detection.run(cap, prewarn_threshold[1],warn_threshold[1]) if "条纹干扰" in det_list else "",
                    self.frame_loss_detection.run(cap, prewarn_threshold[2],warn_threshold[2]) if "视频丢失" in det_list else "",
                    self.occlusion_detection.run(cap, prewarn_threshold[3],warn_threshold[3]) if "视频遮挡" in det_list else "",
                    self.freeze_detection.run(cap, prewarn_threshold[4],warn_threshold[4]) if "视频冻结" in det_list else "",
                    self.brightness_detection.run(cap, prewarn_threshold[5],warn_threshold[5])[0] if "高亮度" in det_list else "",
                    self.brightness_detection.run(cap, prewarn_threshold[6],warn_threshold[6])[1] if "低亮度" in det_list else "",
                    self.noise_detection.run(cap, prewarn_threshold[7],warn_threshold[7]) if "视频噪声" in det_list else "",
                    self.color_cast_detection.run(cap, prewarn_threshold[8],warn_threshold[8]) if "偏色" in det_list else "",
                    self.clearness_detection.run(cap, prewarn_threshold[9],warn_threshold[9]) if "清晰度" in det_list else "",
                    self.scene_change_detection.run(cap, prewarn_threshold[10],warn_threshold[10]) if "场景变化" in det_list else "",
                    self.contrast_anomaly_detection.run(cap, prewarn_threshold[11],warn_threshold[11]) if "对比度" in det_list else "",
                    self.horizontal_waves_detection.run(cap, prewarn_threshold[12],warn_threshold[12]) if "横纹干扰" in det_list else "",
                    self.scroll_interference_detection.run(cap, prewarn_threshold[13],warn_threshold[13]) if "滚动干扰" in det_list else "",
                    self.horizontal_stripes_detection.run(cap, prewarn_threshold[14],warn_threshold[14]) if "横波干扰" in det_list else ""]
                # print(f"监控点{data1['name']}的诊断结果为{diagnosis_data}")
                res_data = [str(data1["id"])] + [data1["ip"]] + [data1["name"]] + [data1["parent_ip"]] + \
                           ["很差" if "报警" in diagnosis_data else
                            "达标" if any(x == "正常" for x in diagnosis_data) and all(x in ["正常", ""] for x in diagnosis_data) else
                            "一般"] + diagnosis_data
                det_data.append(res_data)
            elif not cv2.VideoCapture(video_stream_url).isOpened():
                det_data.append([str(data1["id"])] + [data1["ip"]] + [data1["name"]] + [data1["parent_ip"]] + ["失败"]+[""]*15)
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
    # from datetime import datetime
    # print(datetime.now())
    # data1 = [{"id": 302, "ip": "192.168.11.115", "name": "Camera 01", "parent_ip": "192.168.7.38",
    #           "rtsp": "rtsp://admin:1qaz2wsx!@QW@192.168.7.38:554/Streaming/Unicast/Channels/801"},
    #          {"id": 306, "ip": "192.168.7.30", "name": "北门", "parent_ip": "192.168.7.50",
    #           "rtsp": "rtsp://admin:sxygsj123@192.168.7.50:554/Streaming/Unicast/Channels/101"}]
    # data2 = [{"id": 1, "name": "视频抖动", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 2, "name": "条纹干扰", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 3, "name": "视频丢失", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 4, "name": "视频遮挡", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 5, "name": "视频冻结", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 6, "name": "高亮度", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 7, "name": "低亮度", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 8, "name": "视频噪声", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 9, "name": "偏色", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 10, "name": "清晰度", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 11, "name": "场景变化", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 12, "name": "对比度", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 13, "name": "横纹干扰", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 14, "name": "滚动干扰", "prewarn_threshold": "30", "warn_threshold": "70"},
    #         {"id": 15, "name": "横波干扰", "prewarn_threshold": "30", "warn_threshold": "70"}]
    #
    # res = VQD.run(data1, data2)
    # print(res)
    # print(datetime.now())