# 预祝数据文件

from flask import Blueprint
from flask.cli import with_appcontext
from configs import *

from modules.Tables import *  # 导入的模型

import json

cli = Blueprint('cli', __name__)

# 模型类型数据预置
@cli.cli.command('insert_predefined_data')
@with_appcontext
def insert_predefined_data_command():
    if not Menu.query.first():

        meuu_data = [
            {'id':1,'menu_name':'实时视频','menu_link':None,'menu_order':1,'menu_parent_id':None,'menu_permission_list':json.dumps([1,2])},
            {'id':2,'menu_name':'报警信息','menu_link':None,'menu_order':2,'menu_parent_id':None,'menu_permission_list':json.dumps([1,2])},
            {'id':3,'menu_name':'报警列表','menu_link':None,'menu_order':3,'menu_parent_id':2,'menu_permission_list':json.dumps([1,2])},
            {'id':4,'menu_name':'报警统计','menu_link':None,'menu_order':4,'menu_parent_id':2,'menu_permission_list':json.dumps([1,2])},
            {'id':5,'menu_name':'算法管理','menu_link':None,'menu_order':5,'menu_parent_id':None,'menu_permission_list':json.dumps([1,2])},
            {'id':6,'menu_name':'算法仓','menu_link':None,'menu_order':6,'menu_parent_id':5,'menu_permission_list':json.dumps([1,2])},
            {'id':7,'menu_name':'算法配置','menu_link':None,'menu_order':7,'menu_parent_id':5,'menu_permission_list':json.dumps([1,2])},
            {'id':8,'menu_name':'基础配置','menu_link':None,'menu_order':8,'menu_parent_id':None,'menu_permission_list':json.dumps([1,2])},
            {'id':9,'menu_name':'设备添加','menu_link':None,'menu_order':9,'menu_parent_id':8,'menu_permission_list':json.dumps([1,2])},
        ]

        for i in meuu_data:
            menu_res = Menu(id=i['id'],menu_name=i['menu_name'],menu_link=i['menu_link'],menu_order=i['menu_order'],
                            menu_parent_id=i['menu_parent_id'],menu_permission_list=i['menu_permission_list'])
            db.session.add(menu_res)
        db.session.commit()
        print('菜单预置数据插入完成！')

    if not Permission.query.first():

        permission_data = [
            {'id':1,'permission_name':'超级管理员','permission_code':None,},
            {'id':2,'permission_name':'普通用户','permission_code':None,},
        ]

        for i in permission_data:
            permission_res = Permission(id=i['id'],permission_name=i['permission_name'],permission_code=i['permission_code'])
            db.session.add(permission_res)
        db.session.commit()

        print('权限数据预置数据插入完成！')


    if not User.query.first():
        user_res = User(id=1,username='admin',password=password_encryption('admin'))
        db.session.add(user_res)

        userper = UserPermission(user_id=1, permission_id=[1,2])
        db.session.add(userper)

        db.session.commit()


        print('用户数据预置数据插入完成！')




