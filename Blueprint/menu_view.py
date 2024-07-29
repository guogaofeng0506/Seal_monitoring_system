from flask import jsonify,request, Blueprint
from configs import *
from modules.Tables import *
from sqlalchemy import and_
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required



# 创建蓝图，对应的register目录
menu_view = Blueprint('menu_view', __name__)

# 权限赋值接口
@menu_view.route('/permission_give', methods=['POST'])
def permission_give():

    # 获取权限id 用户id  写入用户权限表 进行赋值
    user_id = request.form.get('user_id')
    permission_id = request.form.get('permission_id')

    # 去除所传数据中的首尾空格
    user_id = user_id.strip() if user_id else None
    permission_id = permission_id.strip() if permission_id else None

    if user_id is None or permission_id is None:
        return jsonify({"msg": "用户权限数据必须填写",'code':400})

    # 查询 选择用户id跟权限id 如果权限不存在 将权限赋值到用户权限表
    userper_data = db.session.query(UserPermission).filter(UserPermission.user_id==user_id).first()
    if userper_data:

        userper_data.permission_id=permission_id
        db.session.commit()

        return jsonify({'code':400,'msg':'权限修改完成'})

    print(permission_id)
    userper = UserPermission(user_id=user_id, permission_id=permission_id)
    db.session.add(userper)
    db.session.commit()

    return jsonify({'code':200,'msg':'权限赋值完成'})



# 对应权限菜单展示接口
@menu_view.route('/menu_show', methods=['POST','GET'])
def menu_show():

    # 获取用户id    在用户权限表里查看关联关系 ，展示对应权限菜单
    user_id = request.args.get('user_id')

    # 获取用户权限数据
    permission_data = db.session.query(UserPermission).filter(UserPermission.user_id==int(user_id)).all()
    if not permission_data:
        return jsonify({'code': '400', 'message': '用户不存在'})

    permission_data = convert_folder_to_dict_list(permission_data,['id','user_id','permission_id'])
    print(permission_data,'ids')

    # 获取用户具有的权限列表（组装为uds 列表）
    user_permission_ids = eval(list([permission['permission_id'] for permission in permission_data if permission['user_id'] == int(user_id)])[0])
    print(user_permission_ids)

    # 查询用户权限对应菜单信息
    menu_data = db.session.query(Menu).all()
    menu_data = convert_folder_to_dict_list(menu_data, ['id', 'menu_name', 'menu_link','menu_order','menu_parent_id','menu_permission_list'])
    print(menu_data)

    menu_list = []
    for i in menu_data:
        i['menu_permission_list'] = eval(i['menu_permission_list'])
        # 检查用户的权限是否包含菜单的权限要求 如果符合要求将菜单写进新列表
        if any(permission in user_permission_ids for permission in i['menu_permission_list']):
            menu_list.append(i)

    # 自定义排序函数  按照菜单表自定义顺序来对菜单进行排序
    def custom_sort(menu):
        return menu.get('menu_order', 0)

    # 对菜单项列表进行排序
    sorted_menu_items = sorted(menu_list, key=custom_sort)

    # 从 menu_parent_id为none主节点开始找  （递归找出所有子类菜单）
    def build_tree(data, parent_id=None):
        tree = []
        for item in data:
            if item['menu_parent_id'] == parent_id:
                children = build_tree(data, item['id'])
                if children:
                    item['children'] = children
                tree.append(item)
        return tree

    # 调用方法获取父子菜单组装数据
    menu_list = build_tree(sorted_menu_items)

    print(menu_list)
    return jsonify({'code': 200, 'menu_list': menu_list})

