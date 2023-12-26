import pymysql
import base64
import pytz
import redis
import os
import subprocess
import cv2
import numpy as np

from flask_bcrypt import Bcrypt  # 密码操作
from datetime import datetime

DB_HOST = '192.168.14.93'  # ip
DB_USER = 'root'  # 用户名
DB_PASSWORD = 'abc123'  # 密码
DB_NAME = 'seal_system'  # 数据库
bcrypt = Bcrypt()  # 加密配置
Redis_ip = '192.168.14.93'
Redis_port = '6379'




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
    {'id': '1', 'value': '预警'},
    {'id': '2', 'value': '一般'},
    {'id': '3', 'value': '严重'},
]

# 算法运行停止状态
status = [
    {'id': '1', 'value': '运行'},
    {'id': '2', 'value': '停止'},
]

# 设备类型筛选
equipment_type = [
    {'id': '1', 'value': '摄像头'},
    {'id': '2', 'value': '录像机'},
]

# 厂商类型筛选
manufacturer_type = [
    {'id': '1', 'value': '海康'},
    {'id': '2', 'value': '大华'},
    {'id': '3', 'value': '索尼'},
    {'id': '4', 'value': '宇视'},
    {'id': '5', 'value': '天地伟业'},
    {'id': '6', 'value': '三星'},
]

# 码流类型
equipment_codetype = [
    {'id': '1', 'value': 'H265'},
    {'id': '2', 'value': 'H264'},
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
    print(output_str, '111')

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


# redis类配置   第一个参数为ip，第二个参数端口号，第三个参数为key值
class Redis(object):
    def __init__(self, Redis_ip, Redis_port, dada_list, decode_responses=True):

        self.connection = redis.Redis(host=Redis_ip, port=Redis_port, decode_responses=decode_responses)
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
    current_value = 101  # 起始值，递增分配

    for i in range(len(children_list)):
        # 为每个子集项分配当前值
        children_list[i]['code'] = current_value

        # 递增当前值
        current_value += 100

    return children_list


# 将h265流转换opencv可编译格式返回
def get_frame_from_rtsp(rtsp_url):
    # # (windwos默认为udp) 使用 ffmpeg 获取 RTSP 流
    # command = [
    #     'ffmpeg',
    #     '-i', rtsp_url,
    #     '-vf', 'fps=1,scale=1920:1080',  # 设置帧率和图像大小
    #     '-f', 'image2pipe',
    #     '-pix_fmt', 'bgr24',
    #     '-vcodec', 'rawvideo', '-',
    # ]

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
        '-vf', 'fps=1,scale=1920:1080',  # 设置帧率和图像大小
        # 指定输出格式为图像流。在这里，将输出格式设置为图像流，以便后续通过管道读取。
        '-f', 'image2pipe',
        # 设置像素格式为 BGR24。在这里，将像素格式设置为 24 位 BGR 格式，即每个像素占据 3 字节。
        '-pix_fmt', 'bgr24',
        # 设置视频编解码器为原始视频。 如果设置为264需要额外增添参数   '-vcodec', 'libx264'
        '-vcodec', 'rawvideo', '-'
    ]


    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 从 ffmpeg 进程中读取一帧数据
    raw_frame = process.stdout.read(1920 * 1080 * 3)
    if not raw_frame:
        return None

    # 将帧数据转换为 numpy 数组
    frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((1080, 1920, 3))
    return frame


# 获取区域图片数据
def get_img_from_camera_net(path, equipment_id, type):
    r = Redis(Redis_ip, Redis_port, 'list')
    # 同步
    if type == 1:
        if path:
            frame = get_frame_from_rtsp(path)

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
    else:
        # 检查是否存在缓存
        cached_path = r.get_string('em_{}'.format(equipment_id))
        if cached_path:
            res_image = os.path.basename(cached_path)
            return {'code': 200, 'msg': '/static/' + str(res_image)}
        else:
            if path:
                frame = get_frame_from_rtsp(path)
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
