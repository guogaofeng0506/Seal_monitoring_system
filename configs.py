import pymysql
import base64
import pytz
import redis
import os
import subprocess
import cv2
import numpy as np
import paramiko
import stat

import multiprocessing
import time
import requests
import xml.etree.ElementTree as ET
import configparser
from getDevStatus import getRunStatus
from requests.auth import HTTPDigestAuth
from flask_bcrypt import Bcrypt  # 密码操作
from datetime import datetime
from sqlalchemy import and_,func,update
from modules.Tables import *


def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

config_path = "config.ini"
config = load_config(config_path)

# 从配置文件中读取数据库和Redis配置
DB_HOST = config['database']['DB_HOST']
DB_USER = config['database']['DB_USER']
DB_PASSWORD = config['database']['DB_PASSWORD']
DB_NAME = config['database']['DB_NAME']

Redis_ip = config['redis']['Redis_ip']
Redis_port = config['redis']['Redis_port']
Redis_password = config['redis']['Redis_password']

Box_ip = config['box_ip']['Box_ip']
Box_user = config['box_ip']['Box_user']
Box_password = config['box_ip']['Box_password']

bcrypt = Bcrypt()  # 加密配置

# 盒子服务器上传类 （算法包上传）
class SSH_Func(object):
    def __init__(self):

        self.Folder_SSH = '/var/model_algorithm_package/'  # 华为云上传文件默认地址
        self.ssh_host = Box_ip
        self.ssh_user = Box_user
        self.ssh_password = Box_password
        self.ssh = paramiko.SSHClient()

    # ssh连接华为云服务器
    def connect_ssh(self):
        # SSH连接信息
        # 标识符
        connected = False
        # 最大连接次数
        attempts = 0

        while connected == False and attempts < 180:
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.ssh_host, username=self.ssh_user, password=self.ssh_password)
                print("SSH连接成功")
                connected = True
            except Exception as e:
                print("SSH连接失败:", e)
                print("正在进行连接重试...")
                attempts += 1
                print(attempts, '次数')
                time.sleep(1)
        if connected == False:
            print('连接超过最大次数限制,无法连接到SSH服务器')
            return None
        return self.ssh


    # 华为云文件夹创建相关逻辑
    def Add_Folder(self):

        ssh = self.connect_ssh()
        if ssh is None:
            return

        sftp = self.ssh.open_sftp()
        # 判断文件夹是否存在，如果不存在进行创建
        remote_folder_1st_level = os.path.dirname(self.Folder_SSH)

        try:
            sftp.mkdir(remote_folder_1st_level)
            print('成功创建算法模型目录:', remote_folder_1st_level)
        except Exception as e:
            print('算法模型目录已经存在，无法创建目录:', remote_folder_1st_level, e)

        sftp.close()
        ssh.close()


    # 上传文件方法
    def upload_send_file(self,file):
        ssh = self.connect_ssh()
        sftp = ssh.open_sftp()
        try:
            # 查找默认路径+当前文件夹文件下列表
            remote_file_list = sftp.listdir(os.path.join(self.Folder_SSH))

            # 文件名
            filename = file.filename

            # 远程路径
            remote_item_path = os.path.join(self.Folder_SSH,filename).replace('\\', '/')

            # 当文件不存在于云服务器时执行上传操作
            if filename not in remote_file_list:
                try:
                    # 本地文件流上传至云服务器
                    with file.stream as local_file:
                        sftp.putfo(local_file, remote_item_path)
                    print('成功上传文件:', filename, '到', remote_item_path)
                    return remote_item_path
                except Exception as e:
                    print('无法上传文件:', filename, e)

            else:
                print('文件已存在，跳过上传:', filename)
                return remote_item_path

        except Exception as e:
            print('文件目录不存在', e)


        finally:
            sftp.close()
            ssh.close()

# arr =SSH_Func()
# arr.Add_Folder()


# 默认静态文件路径获取
def get_static_path():
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录路径
    current_directory = os.path.dirname(current_file_path)
    # 构建目标路径
    target_path = os.path.join(current_directory, 'static')

    return target_path


# 静态路径赋值
FILE_SAVE_PATH = get_static_path()


# 预警筛选
type_status = [
    {'id': '1', 'value': '报警'},
    {'id': '2', 'value': '一般'},
    {'id': '3', 'value': '严重'},
    {'id': '4', 'value': '断电'},
    {'id': '5', 'value': '正常'},
]

# 算法运行停止状态
status = [
    {'id': '1', 'value': '运行'},
    {'id': '2', 'value': '停止'},
]

# 定时任务状态
vcr_status = [
    {'id': '1', 'value': '启用'},
    {'id': '2', 'value': '禁用'},
]

# 算法类型
algorithm_type = [
    {'id': '1', 'value': '通用检测模型'},
    {'id': '2', 'value': '单类检测模型'},
]

# 设备类型筛选
equipment_type = [
    {'id': '1', 'value': '摄像头'},
    {'id': '2', 'value': '录像机'},
    {'id': '3', 'value': '特殊摄像头'},
    {'id': '4', 'value': '浙江双视热成像'},
]


# 厂商类型筛选
manufacturer_type = [
    {'id': '1', 'value': '海康'},
    {'id': '2', 'value': '大华'},
    {'id': '3', 'value': '索尼'},
    {'id': '4', 'value': '宇视'},
    {'id': '5', 'value': '天地伟业'},
    {'id': '6', 'value': '三星'},
    {'id': '7', 'value': '浙江双视'},
]


# 码流类型
equipment_codetype = [
    {'id': '1', 'value': 'H265'},
    {'id': '2', 'value': 'H264'},
]

# 接入方式
vcr_way = [
    {'id': '1', 'value': '私有SDK'},
    {'id': '2', 'value': 'Onvif'},
    {'id': '3', 'value': 'GB28181'},
]


# SQLAlchemy数据库配置
class Config(object):
    """配置参数"""
    # sqlalchemy的配置参数
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:3306/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

    # 设置sqlalchemy自动更新跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True


# 图片转换base64方法
def return_img_stream(img_local_path):
    with open(img_local_path, 'rb') as img:
        # 使用base64进行编码
        b64encode = base64.b64encode(img.read())
        s = b64encode.decode()
        b64_encode = 'data:image/jpg;base64,%s' % s
        # print(b64_encode[0:30])
        # 返回base64编码字符串
        # print(type(b64_encode))
        return b64_encode


def convert_to_dict(item, fields):
    item_dict = {}  # 创建一个空字典，用于存储对象字段的键-值对
    for field in fields:
        # 遍历传入的字段列表
        if hasattr(item, field):
            # 使用 hasattr 函数检查对象 item 是否包含字段 field
            # 如果对象包含该字段，则为 True；否则为 False
            item_dict[field] = getattr(item, field)
            # 如果字段存在，使用 getattr 函数获取字段的值，并将其添加到字典中
    return item_dict
    # 返回包含对象字段的字典


# 序列化器
def convert_folder_to_dict_list(folder_res, fields):
    if isinstance(folder_res, list):
        # 检查输入参数 folder_res 是否为列表
        # 如果是列表，表示要处理多个对象
        # 对列表中的每个对象应用 convert_to_dict 函数
        return [convert_to_dict(item, fields) for item in folder_res]
    else:
        # 如果输入参数不是列表，表示要处理单个对象
        # 直接应用 convert_to_dict 函数来将单个对象转换为字典
        return convert_to_dict(folder_res, fields)


# 密码进行加密
def password_encryption(password):
    # 使用 bcrypt 来加密密码
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed_password


# 用户登录时验证密码
def password_decryption(input_password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, input_password)


# 字符串时间转换 # Mon, 27 Nov 2023 14:42:12 GMT
def time_to_gmt_format(input_str, input_format="%Y-%m-%d %H:%M:%S", output_format="%a, %d %b %Y %H:%M:%S GMT",
                       output_timezone='GMT'):
    # 将字符串转换为 datetime 对象
    input_datetime = datetime.strptime(input_str, input_format)

    # 设置时区
    input_timezone = pytz.timezone(output_timezone)
    input_datetime = input_timezone.localize(input_datetime)

    # 将 datetime 对象格式化为指定字符串格式
    output_str = input_datetime.strftime(output_format)

    time_obj = datetime.strptime(output_str, "%a, %d %b %Y %H:%M:%S %Z")

    formatted_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_str


# 数据库类配置
class MySQL:
    """ mysql类 """

    def __init__(self):
        """ 连接数据库 """
        try:
            self.conn = pymysql.connect(host=DB_HOST,
                                        user=DB_USER,
                                        password=DB_PASSWORD,
                                        database=DB_NAME,
                                        charset='utf8',
                                        cursorclass=pymysql.cursors.DictCursor)
        # 出现异常时执行的代码
        except Exception as e:
            print(e)
        # 没有异常时执行的代码
        else:
            print(" * Database connection succeeded!")
            # 获取游标
            self.cursor = self.conn.cursor()

    def insert(self, sql):
        """
        插入方法
        :param sql:
        :return:
        """

        # 执行sql语句
        self.cursor.execute(sql)
        # 提交sql
        self.conn.commit()

        return "insert ok"

    def delete(self, sql):
        """
        删除
        :param sql:
        :return:
        """
        # 执行sql语句
        self.cursor.execute(sql)
        # 提交sql
        self.conn.commit()

        return "delete ok"

    def update(self, sql):
        """
        修改方法
        :param sql:
        :return:
        """

        # 执行sql语句
        self.cursor.execute(sql)
        # 提交sql
        self.conn.commit()

        return "update ok"

    def get_one(self, sql):
        """
        查询单个数据
        :param sql:
        :return:对象
        """

        # 执行sql语句
        self.cursor.execute(sql)
        # 获取数据
        res = self.cursor.fetchone()
        # 返回结果集
        return res

    def get_all(self, sql):
        """
        查询多个数据
        :param sql:
        :return:数据集
        """

        # 执行sql语句
        self.cursor.execute(sql)
        # 获取数据
        res = self.cursor.fetchall()
        # 返回结果集
        return res

    def __del__(self):
        """
        析构方法
        :return:
        """

        # 关闭游标
        self.cursor.close()
        # 关闭数据库链接
        self.conn.close()


# redus 队列
class TestQueue:
    def __init__(self):
        self.r = redis.Redis(host=Redis_ip, port=Redis_port,password=Redis_password,decode_responses=True, db=1)
        self.key = "queue"

    # 入队
    # def push(self,total):
    #
    #     if total == 0 :
    #         # 在尾部加入数据
    #         self.r.rpush(self.key,'1')
    #     else:
    #         # 在尾部加入数据
    #         data_to_push = [total] * total
    #         self.r.rpush(self.key, *data_to_push)
    #     return '队列数据添加成功'

    # 入队
    def push(self):
        # 在尾部加入数据
        self.r.rpush(self.key,'1')
        return '队列数据添加成功'

    # 出队
    def pop(self):
        # 阻塞地从头部移除数据
        result = self.r.blpop(self.key, timeout=0)
        if result:
            return result[1]  # 返回数据
        else:
            return None  # 如果超时返回 None

    # 返回队列数据列表
    def get_all(self):
        return self.r.lrange(self.key, 0, -1)



# redis类配置   第一个参数为ip，第二个参数端口号，第三个参数为key值
class Redis(object):
    def __init__(self, Redis_ip, Redis_port, dada_list, decode_responses=True):

        self.connection = redis.Redis(host=Redis_ip, port=Redis_port,password=Redis_password,decode_responses=decode_responses)
        # list
        self.dada_list = dada_list

    # 插入绘制区域图片数据
    def set_string(self, data, value):
        self.connection.set(data, value)
        return '插入成功'

    # 根据key查找数据
    def get_string(self, data):
        res = self.connection.get(data)
        return res

    # 队列数据添加
    def list_insert(self, data):

        if self.list_length() >= 3:
            return '该队列数据已经超出,队列长度为{}'.format(self.list_length())

        self.connection.rpush(self.dada_list, data)
        return '添加成功'

    # 队列数据根据已知value删除
    def list_dell(self, data):
        deleted_count = self.connection.lrem(self.dada_list, 0, data)
        print(deleted_count)
        if deleted_count > 0:
            return '删除成功'
        else:
            return '未找到要删除的元素'

    # 队列数据删除
    def list_lpop(self):

        if self.list_length() == 0:
            return '该队列数据为空,无法删除'
        self.connection.lpop(self.dada_list)
        return '删除成功'

    # 队列数据查看
    def list_show(self):

        result = self.connection.lrange(self.dada_list, 0, -1)
        return result

    # 队列长度
    def list_length(self):

        result = self.connection.llen(self.dada_list)
        return result

    # 判断key是否存在
    def list_exists(self):

        result = self.connection.exists(self.dada_list)
        return result

    # 删除某个key
    def list_del(self):

        self.connection.delete(self.dada_list)
        return 'key删除成功'


# 获取子集默认通道 code
def children_list_get_code(children_list):

    # 通道编码
    equipment_aisles_value = 1

    current_value = 101  # 起始值，递增分配

    for i in range(len(children_list)):
        # 为每个子集项分配当前值
        children_list[i]['code'] = current_value
        children_list[i]['equipment_aisles'] = equipment_aisles_value
        # 递增当前值
        current_value += 100
        equipment_aisles_value+=1

    return children_list



# 将h265流转换opencv可编译格式返回
def get_frame_from_rtsp(rtsp_url,img_resolution):

    print(img_resolution.split('x'),'字符串分割')
    # （ linux，windwos）  docker容器内部使用  两者兼容  当环境为linux时将传输协议改为tcp，否则转换失败 ( '-rtsp_transport', 'tcp')
    command = [
        'ffmpeg',
        #  rtsp_transport 参数，通过设定这个参数值为 tcp ，使得ffmpeg强制使用tcp协议传输RTSP流（RTSP流模式使用UDP方式传输）。
        '-rtsp_transport', 'tcp',
        # 设置探测大小，指定用于探测输入流的大小。在这里，150M 表示 150 兆字节的探测大小。
        '-analyzeduration', '150M',
        '-probesize', '150M',
        # 指定输入文件（RTSP 流）的 URL。
        '-i', rtsp_url,
        '-vf', 'fps=1,scale={}:{}'.format(img_resolution.split("x")[0],img_resolution.split("x")[1]),  # 设置帧率和图像大小
        # 指定输出格式为图像流。在这里，将输出格式设置为图像流，以便后续通过管道读取。
        '-f', 'image2pipe',
        #         # 设置像素格式为 BGR24。在这里，将像素格式设置为 24 位 BGR 格式，即每个像素占据 3 字节。
        '-pix_fmt', 'bgr24',
        #         # 设置视频编解码器为原始视频。 如果设置为264需要额外增添参数   '-vcodec', 'libx264'
        '-vcodec', 'rawvideo', '-'
    ]


    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 从 ffmpeg 进程中读取一帧数据
    # raw_frame = process.stdout.read(int(img_resolution.split("x")[0]) * int(img_resolution.split("x")[1]) * 3)
    raw_frame = process.stdout.read(int(img_resolution.split("x")[0]) * int(img_resolution.split("x")[1]) * 3)

    if not raw_frame:
        return None

    # 将帧数据转换为 numpy 数组
    frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((int(img_resolution.split("x")[1]), int(img_resolution.split("x")[0]), 3))
    return frame





def check_rtsp_url(rtsp_url, timeout_seconds=6):

    # 创建管道用于与子进程通信
    parent_conn, child_conn = multiprocessing.Pipe()

    # 启动 RTSP 捕获进程，并传递连接对象和 RTSP URL
    capture_process = multiprocessing.Process(target=rtsp_capture_process, args=(child_conn, rtsp_url))
    capture_process.start()

    start_time = time.time()

    # 等待进程执行完成或超时
    while capture_process.is_alive():
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout_seconds:
            # 如果超时，终止子进程并返回 False
            capture_process.terminate()
            capture_process.join()
            return False

        time.sleep(0.5)  # 小睡一段时间，避免过于频繁检查

    # 获取结果
    result = parent_conn.recv()

    # 返回结果
    return result


def rtsp_capture_process(conn, rtsp_url):
    try:
        cap = cv2.VideoCapture(rtsp_url)

        # 检查是否成功打开
        if cap.isOpened():
            success = True
        else:
            success = False

        # 释放资源
        cap.release()

    except Exception as e:
        print(f"错误：{e}")
        success = False

    # 发送结果到主进程
    conn.send(success)
    conn.close()


# 获取区域图片数据
def get_img_from_camera_net(path, equipment_id, type,img_resolution):
    r = Redis(Redis_ip, Redis_port, 'list')
    # 同步

    if type == 1:
        if path:
            # 判断rtsp是否存在 如果不存在返回falsk
            result = check_rtsp_url(path)
            # print(result, '111')
            if result == False:
                return {'code': 400, 'msg': '无法获取到图像', 'z': path}
            frame = get_frame_from_rtsp(path,img_resolution)
            if frame is not None:
                # 图片名称
                images = 'em_{}'.format(equipment_id) + '.jpg'
                # 文件保存
                img_path = os.path.join(FILE_SAVE_PATH, images)
                cv2.imwrite(img_path, frame)

                # 保存数据到redis
                r.set_string('em_{}'.format(equipment_id), img_path.replace('\\', '/'))
                # 从 Redis 中读取图像数据
                res_image = r.get_string('em_{}'.format(equipment_id))
                res_image = os.path.basename(res_image)
                return {'code': 200, 'msg': '/static/' + str(res_image)}
            else:
                return {'code': 400, 'msg': '无法获取到图像', 'l': frame, 'z': path}
        else:
            return {'code': 400, 'msg': '请选择录像机子集'}
    else:
        # 检查是否存在缓存
        cached_path = r.get_string('em_{}'.format(equipment_id))

        if cached_path:
            res_image = os.path.basename(cached_path)

            return {'code': 200, 'msg': '/static/' + str(res_image)}
        else:
            # 判断rtsp是否存在 如果不存在返回falsk

            result = check_rtsp_url(path)

            # print(result, '111')
            if result == False:
                return {'code': 400, 'msg': '无法获取到图像', 'z': path}
            if path:
                frame = get_frame_from_rtsp(path,img_resolution)
                if frame is not None:
                    # 图片名称
                    images = 'em_{}'.format(equipment_id) + '.jpg'
                    # 文件保存
                    img_path = os.path.join(FILE_SAVE_PATH, images)
                    cv2.imwrite(img_path, frame)  # 存储为图像

                    # 保存数据到redis
                    r.set_string('em_{}'.format(equipment_id), img_path.replace('\\', '/'))
                    # 从 Redis 中读取图像数据
                    res_image = r.get_string('em_{}'.format(equipment_id))
                    res_image = os.path.basename(res_image)
                    return {'code': 200, 'msg': '/static/' + str(res_image)}
                else:
                    return {'code': 400, 'msg': '无法获取到图像', 'l': frame, 'z': path}
            else:
                return {'code': 400, 'msg': '请选择录像机子集'}


# 查询算法配置数据总条数写入队列，算法程序进行重启
def total_count():
    total_records = db.session.query(Algorithm_config). \
        join(Algorithm_library, Algorithm_config.Algorithm_library_id == Algorithm_library.id). \
        join(Mine, Algorithm_config.Mine_id == Mine.id). \
        join(Equipment, Algorithm_config.Equipment_id == Equipment.id). \
        join(Algorithm_test_type, Algorithm_config.Algorithm_test_type_id == Algorithm_test_type.id). \
        filter(Algorithm_library.algorithm_status == 1). \
        filter(Algorithm_config.status == 1). \
        count()
    return total_records


# 递归查找 parent_id 直到没有 向下找
def find_parent_id(parent_id):
    # 使用生成器
    def recursive_query(parent_id):
        from sqlalchemy.orm import aliased

        # 创建别名，用于查询父设备
        parent_alias = aliased(Equipment)

        with_parent_id = db.session.query(
            Equipment.id, Equipment.equipment_type,
            Equipment.manufacturer_type, Equipment.equipment_name,
            Equipment.equipment_ip, Equipment.equipment_uname,
            Equipment.equipment_password, Equipment.equipment_aisles,
            Equipment.equipment_codetype, Equipment.user_status,
            Equipment.create_time, Equipment.parent_id,
            Equipment.code, Equipment.flower_frames,
            parent_alias.equipment_ip.label('parent_ip')  # 加入父设备的IP

        ).join(
            parent_alias, Equipment.parent_id == parent_alias.id, isouter=True
        ).filter(Equipment.parent_id == parent_id).all()

        for folder in with_parent_id:
            # 根据设备类型生成 rtsp 字段
            if folder.equipment_type == '摄像头':
                rtsp = f'rtsp://{folder.equipment_uname}:{folder.equipment_password}@{folder.equipment_ip}'
            elif folder.equipment_type == '特殊摄像头':
                rtsp = get_children_rtsp(folder.parent_id, folder.code, 2)
            elif folder.equipment_type == '录像机':
                rtsp = get_children_rtsp(folder.parent_id, folder.code, 1)
            elif folder.equipment_type == '浙江双视热成像':
                rtsp = 'rtsp://{}:{}@{}:554/live/chn0'.format(folder.equipment_uname, folder.equipment_password, folder.equipment_ip)

            # 添加 rtsp 到结果
            result = {
                'id': folder.id,
                'equipment_type': folder.equipment_type,
                'manufacturer_type': folder.manufacturer_type,
                'equipment_name': folder.equipment_name,
                'equipment_ip': folder.equipment_ip,
                'equipment_uname': folder.equipment_uname,
                'equipment_password': folder.equipment_password,
                'equipment_aisles': folder.equipment_aisles,
                'equipment_codetype': folder.equipment_codetype,
                'user_status': folder.user_status,
                'create_time': folder.create_time,
                'parent_id': folder.parent_id,
                'code': folder.code,
                'flower_frames': folder.flower_frames,
                'parent_ip': folder.parent_ip,
                'rtsp': rtsp
            }

            yield result
            # 递归查找子设备
            yield from recursive_query(folder.id)

    return list(recursive_query(parent_id))


# 转换函数
def row_to_dict(row, keys):
    return {key: value for key, value in zip(keys, row)}

# 子数据
def children_data(equipment_list,vcr_ids):
    for i, equipment in enumerate(equipment_list):
        # 定义子集列表，如果有数据则填入
        # children = []
        id = equipment['id']
        # 在 vcr_ids 中查找匹配的 id
        if id in vcr_ids:
            # 使用 find_parent_id 获取与当前录像机关联的设备
            results = find_parent_id(id)
            # 检查是否有结果
            if results:
                # 获取字段名列表 sqlalemy专属
                # keys = results[0]._mapping.keys()
                # 使用 find_parent_id 获取与当前录像机关联的设备
                # children = [row_to_dict(result, keys) for result in results]

                # 将 children 赋值给当前记录的 'children' 字段
                equipment_list[i]['children'] = results
            else:
                equipment_list[i]['children'] = []
    return equipment_list

# 获取监控点下方详情  默认为当天
def datainfo(equipment_id,now):
    # 1为以前时间  2为当天时间
    if now == 1:
        filters = [Algorithm_result.Equipment_id == equipment_id, db.func.date(Algorithm_result.res_time) < datetime.now().date()]
    else:
        filters = [Algorithm_result.Equipment_id == equipment_id, db.func.date(Algorithm_result.res_time) == datetime.now().date()]

    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None

    res = db.session.query(Algorithm_library.algorithm_name,Algorithm_config.conf_name,Algorithm_result.res_time,Algorithm_result.res_type,Algorithm_result.id.label('res_id')
                           ).join(Algorithm_config, Algorithm_config.Algorithm_library_id == Algorithm_library.id
                           ).join(Algorithm_result,Algorithm_config.id == Algorithm_result.Algorithm_config_id
                           ).filter(query_filter).order_by(Algorithm_result.res_time.desc()).limit(50).all()
    data = [{'algorithm_name': i.algorithm_name, 'conf_name':i.conf_name,'res_time':(i.res_time).strftime("%Y-%m-%d %H:%M:%S"),'res_type':type_status[int(i.res_type)-1]['value'],'res_id':i.res_id} for i in res]
    return data


# 获取视频为录像机子集或者特殊摄像头的返回格式  参数为  父级id  子集通道code
def get_children_rtsp(id,code,type):


    parent_data = db.session.query(Equipment).filter(Equipment.id == id).first()

    if parent_data:

        user = parent_data.equipment_uname
        password = parent_data.equipment_password
        ip = parent_data.equipment_ip

        if type == 1:

            result = 'rtsp://{}:{}@{}:554/Streaming/Unicast/Channels/{}'.format(user,password,ip,code)
        else:
            result = 'rtsp://{}:{}@{}:554/Streaming/Channels/{}'.format(user, password, ip, code)
    else:
        result = None
    return result


# 获取录像机下方设备基础信息-与状态
def VCR_data_info(username,password,ip,port):
    # 如果有命名空间前缀，则去掉
    def remove_namespace(tag):
        return tag.split('}')[-1] if '}' in tag else tag

    def xml_to_dict(element):
        result_list = []
        for child in element:
            result = {}
            if child.text is not None:
                result[remove_namespace(child.tag)] = child.text.strip()
            if len(child) > 0:
                result[remove_namespace(child.tag)] = xml_to_dict(child)
            result_list.append(result)
        return result_list

    # 状态xml序列化
    def parse_xml(response_info):

        # 使用 strip() 去除响应文本中的空白字符
        root = ET.fromstring(response_info.text.strip())

        # 将 XML 转换为列表套字典结构
        xml_dict = (xml_to_dict(root))

        # 定义存储结果的列表
        device_status_list = []

        for i in xml_dict:
            channel_info = {}

            # 获取通道ID
            channel_info['id'] = i['InputProxyChannelStatus'][0]['id']

            # 获取IP地址
            channel_info['ip_address'] = i['InputProxyChannelStatus'][1]['sourceInputPortDescriptor'][2]['ipAddress']

            # 获取是否在线状态
            channel_info['online'] = i['InputProxyChannelStatus'][2]['online']

            # 获取用户名
            channel_info['username'] = i['InputProxyChannelStatus'][1]['sourceInputPortDescriptor'][5]['userName']

            # 获取密码强度状态
            channel_info['password_status'] = i['InputProxyChannelStatus'][6]['SecurityStatus'][0]['PasswordStatus']

            device_status_list.append(channel_info)

        return device_status_list

    # 数据xml序列化
    def xml_data(response_info):

        # 使用 strip() 去除响应文本中的空白字符
        root = ET.fromstring(response_info.text.strip())

        # 将 XML 转换为列表套字典结构
        xml_dict = (xml_to_dict(root))

        device_status_list = []

        for i in xml_dict:
            channel_info = {}

            # 监控点ID
            channel_info['id'] = i['InputProxyChannel'][0]['id']

            # 名称
            channel_info['name'] = i['InputProxyChannel'][1]['name']

            # IP地址
            channel_info['ip_address'] = i['InputProxyChannel'][2]['sourceInputPortDescriptor'][2]['ipAddress']

            # # 管理端口号
            channel_info['managePortNo'] = i['InputProxyChannel'][2]['sourceInputPortDescriptor'][3]['managePortNo']

            # # 用户名
            channel_info['username'] = i['InputProxyChannel'][2]['sourceInputPortDescriptor'][5]['userName']

            device_status_list.append(channel_info)
        return device_status_list

    try:

        # 录像机下方信息
        url = 'http://{}:{}/ISAPI/ContentMgmt/InputProxy/channels'.format(ip,port)
        response = requests.get(url, auth=HTTPDigestAuth(username, password),timeout=5)

        # 录像机下方状态
        url_status = 'http://{}:{}/ISAPI/ContentMgmt/InputProxy/channels/status/1'.format(ip, port)
        response_status = requests.get(url_status, auth=HTTPDigestAuth(username, password),timeout=5)

        # 当请求状态为200的时候
        if response_status.status_code == 200 and response.status_code == 200:

            # device_status_list1 为录像机状态数据   device_status_list2 为录像机信息数据
            device_status_list1,device_status_list2 = parse_xml(response_status),xml_data(response)

            # 合并数据
            merged_data = [
                {**status, **next(info for info in device_status_list1 if info['id'] == status['id'])}
                for status in device_status_list2
            ]

            return merged_data

        else:
            return []

    except Exception as e:
        return []


# print(VCR_data_info('admin','1qaz2wsx!@QW','192.168.7.38',80))
# print(VCR_data_info('admin','1qaz2wsx!@QW','192.168.7.38',80))


#获取监测点的运行状态
def getDevRunStatus(device_list):
    getRunStatus(device_list)
