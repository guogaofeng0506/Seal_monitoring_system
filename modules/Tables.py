from exts import db



# 菜单表
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



# 设备表
class Equipment(db.Model):

    """设备表"""
    __tablename__ = "t_equipment"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '设备表'
    }

    id = db.Column(db.Integer, primary_key=True,autoincrement=True,comment='设备id')  # 整型的主键，会默认设置为自增主键
    equipment_type = db.Column(db.Enum('摄像头','录像机'),comment='设备类型')
    manufacturer_type = db.Column(db.Enum('海康', '大华','索尼','宇视','天地伟业','三星'),comment='厂商类型')
    equipment_name = db.Column(db.String(255),comment='设备名称')
    equipment_ip = db.Column(db.String(32),comment='IP地址')
    equipment_uname = db.Column(db.String(32),comment='用户名')
    equipment_password = db.Column(db.String(255),comment='密码')
    equipment_aisles = db.Column(db.Integer,comment='通道')
    equipment_codetype = db.Column(db.Enum('H265','H264'),comment='码流类型')
    user_status = db.Column(db.String(32),server_default='1',comment='设备状态 1.启用 0.禁用')
    create_time = db.Column(db.DateTime, server_default=db.func.now(),comment='创建时间')
    preset_1 = db.Column(db.String(255),comment='预置字段1')
    code = db.Column(db.String(255),comment='录像机子集默认通道配置')
    parent_id = db.Column(db.Integer,comment='录像机父id')

    Mine_id = db.Column(db.Integer,comment='矿名称id')



# 算法仓表
class Algorithm_library(db.Model):

    """算法仓表"""
    __tablename__ = "t_algorithm_library"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '算法仓表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='算法id')  # 整型的主键，会默认设置为自增主键
    algorithm_file_name =  db.Column(db.String(32),comment='文件名称')
    algorithm_name =  db.Column(db.String(32),comment='算法名称')
    algorithm_type =  db.Column(db.String(32),comment='算法类型')
    algorithm_version =  db.Column(db.String(32),comment='算法版本')
    algorithm_status =  db.Column(db.String(32),server_default='1',comment='算法状态 1.运行 2.停止')
    create_time = db.Column(db.DateTime, server_default=db.func.now(),comment='安装时间')



# 算法配置表
class Algorithm_config(db.Model):

    """算法配置表"""
    __tablename__ = "t_algorithm_config"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'comment': '算法配置表'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='算法配置id')  # 整型的主键，会默认设置为自增主键
    conf_name =  db.Column(db.String(32),comment='名称')
    Algorithm_library_id=  db.Column(db.Integer,comment='算法id')
    Mine_id =  db.Column(db.Integer,comment='分析矿id')
    Equipment_id =  db.Column(db.Integer,comment='分析矿监控点id')
    conf_object =  db.Column(db.String(32),comment='分析对象')
    conf_area =  db.Column(db.String(32),comment='分析区域')
    conf_time = db.Column(db.DateTime, server_default=db.func.now(), comment='配置时间')


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
    res_type = db.Column(db.String(32), comment='报警类型  1 预警  2一般  3 严重')
    res_image = db.Column(db.String(32), comment='报警图片')
    res_video = db.Column(db.String(32), comment='报警视频')
    res_frame_skip = db.Column(db.String(32), comment='跳帧数')
    res_time = db.Column(db.DateTime, server_default=db.func.now(),comment='分析时间')
    res_result =  db.Column(db.String(32),comment='分析结果')

