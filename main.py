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

# 在应用对象上注册蓝图
app.register_blueprint(imageblue, url_prefix='/imageblue')
app.register_blueprint(user_view, url_prefix='/user_view')
app.register_blueprint(cli) # 预置数据蓝图
app.register_blueprint(model_view,url_prefix='/model_view')
app.register_blueprint(menu_view,url_prefix='/menu_view')

# 连接数据库
app.config.from_object(Config)


# 初始化
db.init_app(app)

# 绑定app和数据库
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




# 调用实例对象
if __name__ == '__main__':

    # res = requests.get('http://192.168.14.93:5002/start_script')
    # if res.status_code == 500:
    #     print('----------寒武纪算法微服务未启动----------')
    # elif res.status_code == 200:
    #     print('----------寒武纪算微服务启动成功----------')
    app.run(debug=True, host='0.0.0.0', port=5000)

