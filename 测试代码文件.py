from camera_discovery.CameraDiscovery import CameraONVIF

S = "http://192.168.7.38:80/ISAPI/Security/userCheck"
camera = CameraONVIF('192.168.7.38', 'admin', '1qaz2wsx!@QW')
# camera = CameraONVIF('192.168.7.36', 'admin', 'Pc@12138')
camera.camera_start()

# # 步骤2：获取设备的一般信息
# # device_info = camera.mycam.devicemgmt.GetDeviceInformation()
# device_info = camera.mycam.devicemgmt.GetUsers()
# print(device_info)

# 步骤3：获取视频源（通道）
profiles = camera.mycam.media.GetProfiles()


for profile in profiles:


    # print(profile)

    stream_uri = camera.mycam.media.GetStreamUri({
        'StreamSetup': {
            'Stream': 'RTP-Unicast','Transport': {'Protocol': 'RTSP'}
        },
        'ProfileToken': profile.token
    })
    # print(stream_uri)
    print(stream_uri.Uri)




# print(camera.__dir__())
# print(vars((camera.mycam)),'\n')
# print(vars(vars(camera.mycam)['devicemgmt']))

# # 怎么得到配置的信息如下，他们都在录像机里
# 通道号通道名称IP地址设备通道号管理端口安全性状态协议类型连接
# D1监控室前192.168.7.3918000强在线HIKVISION
# D2监控室后192.168.7.4018000强在线HIKVISION
# D3机房门口192.168.7.4118000强在线HIKVISION
# D4机房后192.168.7.4218000强在线HIKVISION
# D5涉密室门口192.168.7.4318000强在线HIKVISION



# print(dir(camera.mycam.devicemgmt))




# from onvif import ONVIFCamera
# import requests
# import time
# from requests.auth import HTTPDigestAuth
# # import zeep
# # def zeep_pythonvalue(self, xmlvalue):
# #     return xmlvalue
#
# #抓图
# def snap():
#     # Get target profile
#     # zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue
#     mycam = ONVIFCamera("192.168.7.38", 80, "admin", "1qaz2wsx!@QW")
#     media = mycam.create_media_service()  # 创建媒体服务
#     media_profile = media.GetProfiles()[6]  # 获取配置信息
#     print(media_profile.token)
#     res = media.GetSnapshotUri({'ProfileToken': media_profile.token})
#     print(res,'1111')
#     response = requests.get(res.Uri, auth=HTTPDigestAuth("admin", "1qaz2wsx!@QW",))
#     res = "{_time}.png".format(_time=time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())))
#     with open(res, 'wb') as f:
#         f.write(response.content)
#
# snap()


# import cv2
# for profile in profiles:
#     # 获取每个通道的Stream URI
#     stream_uri = camera.mycam.media.GetStreamUri({
#         'StreamSetup': {
#             'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}
#         },
#         'ProfileToken': profile.token
#     })
#
#     # 过滤子码流
#     if stream_uri.Uri[-1] == '2':
#         pass
#     else:
#
#         # 构建带有用户名和密码的完整RTSP URL
#         full_rtsp_url = f"rtsp://admin:1qaz2wsx!@QW@{(stream_uri.Uri).replace('rtsp://','')}"
#
#         # 打印完整的RTSP URL
#         print(f"Channel {profile.Name} RTSP URL: {full_rtsp_url}")
#
#         try:
#             cap = cv2.VideoCapture(full_rtsp_url)
#             if not cap.isOpened():
#                 print(f"RTSP流 {full_rtsp_url} 不在线")
#             else:
#                 print(f"RTSP流 {full_rtsp_url} 在线")
#                 cap.release()
#         except Exception as e:
#             print(f"检查RTSP流时出错：{e}")


