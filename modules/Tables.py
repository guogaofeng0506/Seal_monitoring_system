from exts import db



# 菜单表
S = '图片结果矩形框  1. 绘制   2.不绘制'


class Menu(db.Model):
    """菜单表"""
    __tablename__ = "t_menu"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '菜单表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='菜单id')
    menu_name = db.Column(db.String(32), comment='菜单名称')
    menu_link = db.Column(db.String(255), comment='url请求地址')
    menu_order = db.Column(db.Integer, comment='菜单顺序')
    menu_parent_id = db.Column(db.Integer, comment='父菜单id')  # 如果此项为 null，那么它就是顶级菜单
    menu_permission_list = db.Column(db.String(32),comment='权限标识列表')  # 【1,2,3】  parent_id 加权限列表来给出菜单


# 权限表
class Permission(db.Model):
    """权限表"""
    __tablename__ = "t_permission"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '权限表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='权限id')
    permission_name = db.Column(db.String(32), comment='权限名称')
    permission_code = db.Column(db.String(32), comment='权限代码')


# 用户权限关联表
class UserPermission(db.Model):
    """用户权限关联表"""
    __tablename__ = "t_user_permission"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '用户权限关联表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='关联表id')
    user_id = db.Column(db.Integer,comment='用户id')
    permission_id = db.Column(db.String(33),comment='权限id')


# 用户表
class User(db.Model):
    """用户表"""
    __tablename__ = "t_user"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '用户表'
    }

    id = db.Column(db.Integer, primary_key=True,autoincrement=True,comment='用户id')  # 整型的主键，会默认设置为自增主键
    username = db.Column(db.String(32),comment='用户名称')
    password = db.Column(db.Text,comment='用户密码')
    email = db.Column(db.String(32),comment='用户邮箱')
    user_status = db.Column(db.String(32),server_default='1',comment='账号状态 1.启用 0.禁用')
    create_time = db.Column(db.DateTime, server_default=db.func.now(),comment='创建时间')
    end_login_time = db.Column(db.DateTime,comment='最后登录时间')


# 矿名称表  单独作为一个表，来关联对应下方设备
class Mine(db.Model):
    """矿名称表"""
    __tablename__ = "t_mine"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '矿名称表'
    }

    id = db.Column(db.Integer, primary_key=True,autoincrement=True,comment='矿id')  # 整型的主键，会默认设置为自增主键
    mine_name = db.Column(db.String(100),comment='矿名称')


# 录像机同步表
class VCR_data(db.Model):
    """录像机同步表"""
    __tablename__ = "t_vcr_data"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '录像机同步表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='录像机id')  # 整型的主键，会默认设置为自增主键
    vcr_type = db.Column(db.Enum('海康', '大华','索尼','宇视','天地伟业','三星'),comment='厂商类型')
    vcr_way = db.Column(db.Enum('私有SDK', 'Onvif','GB28181'),comment='接入方式')
    vcr_name = db.Column(db.String(50), comment='录像机名称')
    vcr_ip = db.Column(db.String(50), comment='录像机ip')
    vcr_username = db.Column(db.String(50), comment='录像机用户')
    vcr_password = db.Column(db.String(50), comment='录像机密码')
    vcr_port = db.Column(db.String(50), comment='录像机端口')
    vcr_status = db.Column(db.String(50), comment='录像机同步状态 1 同步完成 2 同步未完成' )
    Mine_id = db.Column(db.Integer,comment='矿名称id')
    create_time = db.Column(db.DateTime, server_default=db.func.now(), comment='创建时间')



# 设备表
class Equipment(db.Model):

    """设备表"""
    __tablename__ = "t_equipment"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '设备表'
    }

    id = db.Column(db.Integer, primary_key=True,autoincrement=True,comment='设备id')  # 整型的主键，会默认设置为自增主键
    equipment_type = db.Column(db.Enum('摄像头','录像机','特殊摄像头'),comment='设备类型')
    manufacturer_type = db.Column(db.Enum('海康', '大华','索尼','宇视','天地伟业','三星'),comment='厂商类型')
    equipment_name = db.Column(db.String(255),comment='设备名称')
    equipment_ip = db.Column(db.String(32),comment='IP地址')
    equipment_uname = db.Column(db.String(32),comment='用户名')
    equipment_password = db.Column(db.String(255),comment='密码')
    equipment_aisles = db.Column(db.Integer,comment='通道')
    equipment_codetype = db.Column(db.Enum('H265','H264'),comment='码流类型')
    user_status = db.Column(db.String(32),server_default='1',comment='设备状态 1.启用 0.禁用')
    create_time = db.Column(db.DateTime, server_default=db.func.now(),comment='创建时间')
    flower_frames = db.Column(db.String(255),comment='花帧阈值')
    code = db.Column(db.String(255),comment='录像机子集默认通道配置')
    parent_id = db.Column(db.Integer,comment='录像机父id')


    Mine_id = db.Column(db.Integer,comment='矿名称id')
    VCR_data_id = db.Column(db.Integer,comment='录像机同步id，用于查找同步设备及下方子设备')
    online = db.Column(db.Integer,comment='是否在线  1 在线  2 离线')



# 算法仓表
class Algorithm_library(db.Model):

    """算法仓表"""
    __tablename__ = "t_algorithm_library"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '算法仓表'
    }
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='算法id')  # 整型的主键，会默认设置为自增主键
    algorithm_file_name =  db.Column(db.String(255),comment='文件名称')
    algorithm_name =  db.Column(db.String(255),comment='算法名称')
    algorithm_type =  db.Column(db.String(32),comment='算法类型 1（通用检测模型） 2（单类检测模型）')
    algorithm_type_list =  db.Column(db.Text,comment='算法检测类型，列表')
    algorithm_version =  db.Column(db.String(32),comment='算法版本')
    algorithm_status =  db.Column(db.String(32),server_default='1',comment='算法状态 1.运行 2.停止')
    algorithm_trade_type =  db.Column(db.String(32),server_default='1',comment='算法厂商 1.寒武纪 2.算能')
    algorithm_path = db.Column(db.Text, comment='算法包路径')
    create_time = db.Column(db.DateTime, server_default=db.func.now(),comment='安装时间')



class Algorithm_test_type(db.Model):
    """检测类型表"""
    __tablename__ = "t_algorithm_test_type"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '检测类型表'
    }


    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='检测类型id')  # 整型的主键，会默认设置为自增主键
    test_type_cname = db.Column(db.String(50), comment='检测类型中文名称')
    test_type_ename = db.Column(db.String(50), comment='检测类型英文名称')
    Algorithm_library_id = db.Column(db.Integer,comment='算法id')


# 算法配置表
class Algorithm_config(db.Model):

    """算法配置表"""
    __tablename__ = "t_algorithm_config"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '算法配置表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='算法配置id')  # 整型的主键，会默认设置为自增主键
    conf_name = db.Column(db.String(32),comment='名称')
    Algorithm_library_id=  db.Column(db.Integer,comment='算法id')
    Mine_id = db.Column(db.Integer,comment='分析矿id')
    Equipment_id = db.Column(db.Integer,comment='分析矿监控点id')
    Algorithm_test_type_id = db.Column(db.Integer,comment='检测类型id')
    conf_object = db.Column(db.String(32),comment='分析对象')
    conf_area = db.Column(db.String(255),comment='分析区域')
    status = db.Column(db.String(32),server_default='1',comment='算法配置算法运行状态 1 运行  2 停止')
    shield_status = db.Column(db.String(32),server_default='2',comment='遮挡参数 1 遮挡  2 未遮挡')
    conf_time = db.Column(db.DateTime, server_default=db.func.now(), comment='配置时间')
    tem_conf_area = db.Column(db.String(255),comment='热成像检测消除区域')
    tem_frames = db.Column(db.String(30),comment='温度阈值')
    confidence = db.Column(db.String(30),comment='置信度阈值')
    draw_type = db.Column(db.String(20),comment='绘制状态  1矩形 2线条')
    interval_time = db.Column(db.Integer,comment='报警间隔时间')
    duration_time = db.Column(db.Integer, comment='持续时间')
    conf_img_resolution = db.Column(db.String(20),comment='算法配置图片分辨率')
    # conf_type = db.Column(db.Integer, comment='报警类型   1 预警  2一般  3 严重 4 断电 5 正常')
    # 报警类型，数据传输，结果定义输出

    image_draw_type = db.Column(db.Integer, comment=('%s' % S))



# 算法(预警)结果表
class Algorithm_result(db.Model):

    """算法结果表"""
    __tablename__ = "t_algorithm_result"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '算法结果表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='算法结果id')  # 整型的主键，会默认设置为自增主键
    Algorithm_config_id = db.Column(db.Integer,comment='算法配置id')
    res_type = db.Column(db.String(32), comment='报警类型   1 预警  2一般  3 严重 4 断电 5 正常')
    res_image = db.Column(db.String(255), comment='报警图片')
    res_video = db.Column(db.String(32), comment='报警视频')
    res_frame_skip = db.Column(db.String(32), comment='跳帧数')
    res_time = db.Column(db.DateTime, server_default=db.func.now(),comment='分析时间')
    res_result = db.Column(db.String(32),comment='分析结果')
    res_temperature = db.Column(db.Text,comment='测温数据   0位最大值 1位最小值 2位温度')
    xmin_xmax_ymin_ymax = db.Column(db.Text,comment='检测结果框点坐标')
    res_confidence = db.Column(db.Text,comment='置信度结果')

# 字典表
class Dict_data(db.Model):
    """字典表"""
    __tablename__ = "t_dict_data"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '字典表'
    }


    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='id')  # 整型的主键，会默认设置为自增主键
    dict_cname = db.Column(db.String(50), comment='中文名称')
    dict_ename = db.Column(db.String(50), comment='英文名称')


# 定时任务表
class ScheduledTask(db.Model):
    """定时任务表"""
    __tablename__ = 't_scheduled_tasks'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '定时任务表'
    }

    # 任务ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='任务ID')
    # 任务名称 不能为空
    name = db.Column(db.String(255), nullable=False, comment='任务名称')
    # 任务执行的时间间隔（单位：秒）  不能为空
    interval_seconds = db.Column(db.Integer, nullable=False, comment='任务执行的时间间隔（单位：秒）')
    # 下一次任务执行的时间          可以为空
    next_run_time = db.Column(db.DateTime, nullable=True, comment='下一次任务执行的时间')

    # 时间类型  可以为空
    # weeks (int) – 间隔几周    days (int) – 间隔几天
    # hours (int) – 间隔几小时  minutes (int) – 间隔几分钟
    # seconds (int) – 间隔多少秒
    time_type = db.Column(db.String(255), nullable=False, comment='时间类型(字符串)')
    rtsp_list = db.Column(db.Text, nullable=False, comment='rtsp流')
    diagnosis_type_list = db.Column(db.Text, nullable=False, comment='诊断类型列表')
    scheduled_concent = db.Column(db.Text, nullable=False, comment='备注')
    scheduled_status = db.Column(db.Integer, nullable=False, comment='1 启用 0禁用')

    # 创建
    create_time = db.Column(db.DateTime, server_default=db.func.now(),comment='创建时间')

    def __repr__(self):
        return f'<ScheduledTask {self.name}>'


# 诊断类型检测项表
class Diagnosis_type(db.Model):
    """诊断类型检测项表"""
    __tablename__ = 't_diagnosis_type'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '诊断类型检测项表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='检测项ID')
    name = db.Column(db.String(255), comment='检测项名称')
    prewarn = db.Column(db.String(25),server_default='30',comment='预警值')
    warn = db.Column(db.String(25),server_default='70',comment='报警值')
    create_time = db.Column(db.DateTime, server_default=db.func.now(), comment='创建时间')



# 质量诊断数据表
class Diagnosis_data(db.Model):
    """质量诊断数据表"""
    __tablename__ = 't_diagnosis_data'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '质量诊断数据表'
    }


    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='诊断ID')
    equipment_id = db.Column(db.Integer, comment='设备id')
    diagnosis_type = db.Column(db.String(20), comment='诊断状态 1. 达标 2. 一般 3. 很差 4. 失败')
    db101 = db.Column(db.String(10), comment='视频抖动')
    db102 = db.Column(db.String(10), comment='条纹干扰')
    db103 = db.Column(db.String(10), comment='视频丢失')
    db104 = db.Column(db.String(10), comment='视频遮挡')
    db105 = db.Column(db.String(10), comment='视频冻结')
    db106 = db.Column(db.String(10), comment='高亮度')
    db107 = db.Column(db.String(10), comment='低亮度')
    db108 = db.Column(db.String(10), comment='视频噪声')
    db109 = db.Column(db.String(10), comment='偏色')
    db110 = db.Column(db.String(10), comment='清晰度')
    db111 = db.Column(db.String(10), comment='场景变化')
    db112 = db.Column(db.String(10), comment='对比度')
    db113 = db.Column(db.String(10), comment='横纹干扰')
    db114 = db.Column(db.String(10), comment='滚动条纹')
    db115 = db.Column(db.String(10), comment='横波干扰')
    create_time = db.Column(db.DateTime, server_default=db.func.now(), comment='创建时间')
