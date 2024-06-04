import datetime

from flask import Response, jsonify, Flask, request, Blueprint
from configs import *
from modules.Tables import *
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required



# 创建蓝图，对应的register目录
user_view = Blueprint('user_view', __name__)

# 登录接口获取token
@user_view.route('/login', methods=['POST'])
def login():

    username = request.form.get('username', None)
    password = request.form.get('password', None)

    # 去除用户名和密码中的首尾空格
    username = username.strip() if username else None
    password = password.strip() if password else None

    if username is None or password is None:
        return jsonify({"msg": "用户名和密码必须提供",'code':400})

    # 尝试查询用户信息  (当没有数据的时候返回值为 None)
    user_info = db.session.query(User).filter(User.username == username).first()

    if user_info is None:
        return jsonify({"msg": "用户名或密码错误",'code':401})

    if user_info.user_status == '0':
        return jsonify({"msg": "账号禁用！", 'code': 400})

    # 如果用户名存在验证密码
    if user_info  and password_decryption(password, user_info.password):

        # 最后登录时间修改
        # user_info.end_login_time = datetime.datetime.now()
        db.session.add(user_info)
        db.session.commit()

        # token返回
        access_token = create_access_token(identity=username)
        return jsonify({
            'code':200,
            'msg':'登录成功！',
            'access_token': access_token,
        })
    else:
        # 登录失败，返回错误响应
        return jsonify({"msg" :"用户名或密码错误",'code': 401})




# token验证  如果失效 前端回退到登录页面
@user_view.route('/protected', methods=['GET', 'POST', 'DELETE', 'PUT', 'CATCH'])
@jwt_required()
def protected():

    # token验证  成功返回信息
    current_user = get_jwt_identity()

    # 查找token对应用户信息返回
    user_info = db.session.query(User).filter(User.username == current_user).first()

    # 获取用户多权限数据
    permission_data = db.session.query(User.id,User.username,Permission.id.label('userpermission_id'),Permission.permission_name,).join(UserPermission,User.id == UserPermission.user_id).\
        join(Permission,UserPermission.permission_id == Permission.id).filter(User.id == user_info.id).all()

    permission_data = [{'permission_id':i.userpermission_id,'permission_name':i.permission_name} for i in permission_data]

    # 序列化
    user_data = convert_folder_to_dict_list(user_info, ['id','username', 'email', 'create_time'])

    # dict数据拼接
    user_data = {**user_data, **{'permission_data':permission_data}}


    return jsonify({
        'logged_in_as': current_user,
        'code':200,
        'user_info': user_data
    })


# 用户注册接口
@user_view.route('/register', methods=['POST'])
def register():

    # 接受所传参数用户信息
    username = request.form.get('username', None)
    password = request.form.get('password', None)


    # 去除用户名和密码中的首尾空格
    username = username.strip() if username else None
    password = password.strip() if password else None

    if username is None or password is None:
        return jsonify({
            'code': 400,
            'msg': '用户名和密码必须提供！'
        })

    # 查找用户名称相同用户
    user = db.session.query(User).filter(User.username == username).first()

    if user:
        return jsonify({
            'code': 400,
            'msg': '该用户已经存在！'
        })

    # 创建新用户并将加密后的密码存储到数据库
    new_user = User(username=username, password=password_encryption(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
            'code': 200,
            'msg': '注册成功！',
    })

