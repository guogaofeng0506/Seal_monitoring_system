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

