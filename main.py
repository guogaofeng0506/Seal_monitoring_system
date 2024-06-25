import datetime

import requests
from flask_migrate import Migrate
from exts import db
from configs import *
from flask_cors import CORS
from flask import Response, jsonify, Flask, request
from flask_jwt_extended import JWTManager

# 蓝图导入
from Blueprint.Image_blue import imageblue
from Blueprint.user_view import user_view
from Blueprint.commands import cli  # 预置数据导入
from Blueprint.model_view import model_view
from Blueprint.menu_view import menu_view
from Blueprint.model_views import model_views
from Blueprint.scheduler_task import scheduler_task,run_task
from flask_apscheduler import APScheduler

import time
import threading


# 建立flask实例
app = Flask(__name__)
# 注册CORS, "/*" 允许访问所有api
CORS(app, resources=r'/*')

# 获取 Flask 应用的根路径
root_path = app.root_path

# 配置密钥
app.config['JWT_SECRET_KEY'] = 'my_secret_key'

# 初始化 JWTManager
jwt = JWTManager(app)

# 过期时间
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 1800

# 解决中文乱码
app.config['JSON_AS_ASCII'] = False

# --------定时任务配置--------
# 配置 APScheduler
class Config_APScheduler:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config_APScheduler)

# 初始化 APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


# --------在应用对象上注册蓝图--------
app.register_blueprint(imageblue, url_prefix='/imageblue')
app.register_blueprint(user_view, url_prefix='/user_view') # 用户蓝图
app.register_blueprint(cli) # 预置数据蓝图
app.register_blueprint(model_view,url_prefix='/model_view') # 数据操作蓝图
app.register_blueprint(menu_view,url_prefix='/menu_view')  # 菜单蓝图
app.register_blueprint(model_views,url_prefix='/model_views') # 新增数据操作蓝图1
app.register_blueprint(scheduler_task,url_prefix='/scheduler_task') # 定时任务蓝图

# --------连接数据库--------
app.config.from_object(Config)

# --------初始化--------
db.init_app(app)

# --------绑定app和数据库--------
migrate = Migrate(app,db)

# 测试模拟模型训练长时间操作
def long_running_function():
    # 模拟一个长时间运行的操作
    time.sleep(10)
    print("长时间运行操作!")


# 创建线程立即返回，并后台调用模型方法
@app.route('/api/background_task', methods=['GET'])
def background_task():
    # 在一个新线程中运行
    thread = threading.Thread(target=long_running_function)
    thread.start()
    print('后台运行')
    # 主线程立即返回响应
    return jsonify({'message': '任务后台运行完成!'})


@app.route('/', methods=['GET', 'POST', 'DELETE', 'PUT', 'CATCH'])
def def1():
    print('启动成功！')
    return jsonify({'code': 200})


# 录像机设备信息定时同步
# -----先查找录像机父表是否有数据，如果有数据循环读取（录像机ip），
# 用录像机ip去调用isapi来获取摄像头实时信息进行修改，如果不存在则进行添加操作-----
def vcr_update_task():  # 运行的定时任务的函数
    with app.app_context():
        # 查找录像机信息
        vcr_dict_list = convert_folder_to_dict_list(db.session.query(VCR_data).all(),['id','vcr_ip','vcr_username','vcr_password','vcr_port','Mine_id'])
        # 当录像机设备存在时执行逻辑
        if vcr_dict_list:
            # 因为录像机ip是多个，所以要进行循环获取每一个录像机ip
            for vcr in vcr_dict_list:

                # 获取父亲的id
                db_equipment_parent_id = db.session.query(Equipment).filter(Equipment.VCR_data_id == vcr['id'],
                                                                       Equipment.parent_id == None).first()

                # 获取外部设备信息
                external_data_list = VCR_data_info(vcr['vcr_username'], vcr['vcr_password'], vcr['vcr_ip'],
                                                   vcr['vcr_port'])

                # 获取外部设备信息列表,用于查询数据表存在矿上不存在删除操作
                external_data_ip_list = [ i.get('ip_address') for i in external_data_list]

                # 从数据库中获取设备信息并转换为字典
                db_equipment_list = db.session.query(Equipment).filter(Equipment.VCR_data_id == vcr['id'],
                                                                       Equipment.parent_id != None).all()

                # 如果db_equipment_list查到的数据不在external_data_list里，进行db_equipment_list数据的删除操作
                for i in db_equipment_list:
                    if i.equipment_ip not in external_data_ip_list:
                        db.session.delete(i)
                db.session.commit()



                # 转换为字典
                db_equipment_dict = {device.equipment_ip: device for device in db_equipment_list}


                # 循环isapi信息
                for i in external_data_list:
                    ip_address = i['ip_address']
                    name = i['name']
                    id = i['id']
                    online = 1 if i['online'] == 'true' else 0
                    # 当isapi信息存在于数据库中进行修改
                    if ip_address in db_equipment_dict:
                        # 如果存在，检查并更新信息
                        db_device = db_equipment_dict[ip_address]
                        db_device.equipment_name = name
                        db_device.online = online
                        db_device.equipment_ip = ip_address
                        db_device.equipment_aisles = id
                        db.session.commit()

                    else:
                        # 如果不存在，添加新设备
                        print(f"添加新设备: {i['name']}")
                        new_device = Equipment(
                            VCR_data_id=vcr['id'],
                            parent_id=db_equipment_parent_id.id,
                            equipment_aisles=id,  # 使用外部数据中的字段作为 equipment_aisles
                            equipment_name=name,
                            equipment_ip=ip_address,
                            online=online,
                            code = str(id)+'01',
                            equipment_type='录像机',
                            manufacturer_type='海康',
                            equipment_uname=vcr['vcr_username'],
                            equipment_password=vcr['vcr_password'],
                            user_status='1',
                            create_time=datetime.now(),
                            Mine_id=vcr['Mine_id'],

                        )
                        db.session.add(new_device)
                        db.session.commit()
                print('录像机设备定时同步更新成功!')
        else:
                print('录像机设备不存在！')


scheduler.add_job(func=vcr_update_task, args=[], id="vcr_update_task_1", trigger="interval", minutes=5, replace_existing=True)

#监测点离线时间统计定时任务
def monitorPoint_updata_task():
    with app.app_context():
        offline_equipmentList = db.session.query(Equipment).join(Offline_info,Equipment.equipment_ip == Offline_info.equipment_ip).all()
        offline_infoList = db.session.query(Offline_info).all()
        for equip_item in offline_equipmentList:
            for offline_item in offline_infoList:
                if equip_item.equipment_ip == offline_item.equipment_ip and offline_item.offline_end_time == None:
                    offline_durationTime = (datetime.now() - offline_item.offline_start_time).seconds
                    days = offline_durationTime // (24 * 3600)
                    hours = (offline_durationTime % (24 * 3600)) // 3600
                    minutes = (offline_durationTime % 3600) // 60
                    seconds = offline_durationTime % 60
                    equip_item.duration_time = f"{days}天{hours}时{minutes}分{seconds}秒"
                    update_query = (
                        update(Equipment)
                        .where(equip_item.id == offline_item.equipment_id)
                        .values(
                            duration_time=f"{days}天{hours}时{minutes}分{seconds}秒"
                        )
                    )
                    # 提交会话保存修改
                    db.session.execute(update_query)
                    db.session.commit()
                    print('离线时间统计定时任务更新成功!')

scheduler.add_job(func=monitorPoint_updata_task, args=[], id="monitorPoint_updata_task_1", trigger="interval", minutes=5, replace_existing=True)


# 定时任务初始化
def setup_scheduler_tasks():
    try:
        with app.app_context():
            # 查询数据库获取所有定时任务配置
            tasks = db.session.query(ScheduledTask).all()
            if tasks:
                tasks_data = convert_folder_to_dict_list(tasks,['id','name','interval_seconds','time_type',
                                                                'rtsp_list','diagnosis_type_list',
                                                                'scheduled_concent','scheduled_status',
                                                                ])
                for task in tasks_data:
                    job_id = f"task_{task['id']}"
                    name = f"task_{task['name']}"
                    interval_seconds = int(task['interval_seconds'])
                    time_type = task['time_type']
                    rtsp_list =task['rtsp_list']
                    diagnosis_type_list = task['diagnosis_type_list']
                    scheduled_concent = task['scheduled_concent']
                    scheduled_status = str(task['scheduled_status'])

                    #当任务类型为启用的时候运行
                    if int(scheduled_status) == 1:

                        if time_type == 'seconds':
                            # 添加定时任务到 APScheduler
                            scheduler.add_job(
                                id=job_id,
                                func=run_task,
                                args=[job_id, name, interval_seconds,time_type,rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                                trigger='interval',
                                seconds=interval_seconds,
                            )
                        elif time_type == 'minutes':
                            # 添加定时任务到 APScheduler
                            scheduler.add_job(
                                id=job_id,
                                func=run_task,
                                args=[job_id, name, interval_seconds,time_type,rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                                trigger='interval',
                                minutes=interval_seconds,
                            )

                        elif time_type == 'hours':
                            # 添加定时任务到 APScheduler
                            scheduler.add_job(
                                id=job_id,
                                func=run_task,
                                args=[job_id, name, interval_seconds,time_type,rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                                trigger='interval',
                                hours=interval_seconds,
                            )

                        elif time_type == 'days':
                            # 添加定时任务到 APScheduler
                            scheduler.add_job(
                                id=job_id,
                                func=run_task,
                                args=[job_id, name, interval_seconds,time_type,rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                                trigger='interval',
                                days=interval_seconds,
                            )

                        elif time_type == 'weeks':
                            # 添加定时任务到 APScheduler
                            scheduler.add_job(
                                id=job_id,
                                func=run_task,
                                args=[job_id, name, interval_seconds,time_type,rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                                trigger='interval',
                                weeks=interval_seconds,
                            )

                        print(f"已添加定时任务: {name}，触发类型: {time_type}   触发间隔{interval_seconds} ")

                    else:
                        print('任务状态禁用！')
            else:
                print('暂无定时任务!')

    except Exception as e:
        print(f"初始化定时任务时发生异常: {e}")


# 调用实例对象
if __name__ == '__main__':
    setup_scheduler_tasks()
    app.run(debug=False, host='0.0.0.0', port=5000)

