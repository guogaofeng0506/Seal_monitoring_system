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

        userper = UserPermission(user_id=1, permission_id=str([1,2]))
        db.session.add(userper)

        db.session.commit()


        print('用户数据预置数据插入完成！')


    if not Dict_data.query.first():

        dict_data = [
            {'id':1,'dict_cname':'人','dict_ename':'person',},
            {'id':2,'dict_cname':'自行车','dict_ename':'bicycle',},
            {'id':3,'dict_cname':'汽车','dict_ename':'car',},
            {'id':4,'dict_cname':'摩托车','dict_ename':'motorcycle',},
            {'id':5,'dict_cname':'飞机','dict_ename':'airplane',},
            {'id':6,'dict_cname':'公共汽车','dict_ename':'bus',},
            {'id':7,'dict_cname':'火车/列车','dict_ename':'train',},
            {'id':8,'dict_cname':'卡车','dict_ename':'truck',},
            {'id':9,'dict_cname':'小船/轮船','dict_ename':'boat',},
            {'id':10,'dict_cname':'红绿灯','dict_ename':'traffic light',},
            {'id':11,'dict_cname':'消防栓','dict_ename':'fire hydrant',},
            {'id':12,'dict_cname':'停车牌/停止标志','dict_ename':'stop sign',},
            {'id':13,'dict_cname':'停车计时器','dict_ename':'parking meter',},
            {'id':14,'dict_cname':'长凳/长椅','dict_ename':'bench',},
            {'id':15,'dict_cname':'鸟','dict_ename':'bird',},
            {'id':16,'dict_cname':'猫','dict_ename':'cat',},
            {'id':17,'dict_cname':'狗','dict_ename':'dog',},
            {'id':18,'dict_cname':'马','dict_ename':'horse',},
            {'id':19,'dict_cname':'羊','dict_ename':'sheep',},
            {'id':20,'dict_cname':'牛','dict_ename':'cow',},
            {'id':21,'dict_cname':'大象','dict_ename':'elephant',},
            {'id':22,'dict_cname':'熊','dict_ename':'bear',},
            {'id':23,'dict_cname':'斑马','dict_ename':'zebra',},
            {'id':24,'dict_cname':'长颈鹿','dict_ename':'giraffe',},
            {'id':25,'dict_cname':'背包','dict_ename':'backpack',},
            {'id':26,'dict_cname':'伞','dict_ename':'umbrella',},
            {'id':27,'dict_cname':'手提包','dict_ename':'handbag',},
            {'id':28,'dict_cname':'绳索/领带','dict_ename':'tie',},
            {'id':29,'dict_cname':'手提箱/行李箱','dict_ename':'suitcase',},
            {'id':30,'dict_cname':'飞盘/飞碟','dict_ename':'frisbee',},
            {'id':31,'dict_cname':'滑雪板/单板','dict_ename':'skis',},
            {'id':32,'dict_cname':'滑雪雪板/一对狭长的板','dict_ename':'snowboard',},
            {'id':33,'dict_cname':'运动球','dict_ename':'sports ball',},
            {'id':34,'dict_cname':'风筝','dict_ename':'kite',},
            {'id':35,'dict_cname':'棒球棒','dict_ename':'baseball bat',},
            {'id':36,'dict_cname':'棒球手套','dict_ename':'baseball glove',},
            {'id':37,'dict_cname':'滑板','dict_ename':'skateboard',},
            {'id':38,'dict_cname':'冲浪板','dict_ename':'surfboard',},
            {'id':39,'dict_cname':'网球拍','dict_ename':'tennis racket',},
            {'id':40,'dict_cname':'瓶子','dict_ename':'bottle',},
            {'id':41,'dict_cname':'酒杯','dict_ename':'wine glass',},
            {'id':42,'dict_cname':'杯子','dict_ename':'cup',},
            {'id':43,'dict_cname':'叉子','dict_ename':'fork',},
            {'id':44,'dict_cname':'刀','dict_ename':'knife',},
            {'id':45,'dict_cname':'勺子','dict_ename':'spoon',},
            {'id':46,'dict_cname':'碗','dict_ename':'bowl',},
            {'id':47,'dict_cname':'香蕉','dict_ename':'banana',},
            {'id':48,'dict_cname':'苹果','dict_ename':'apple',},
            {'id':49,'dict_cname':'三明治','dict_ename':'sandwich',},
            {'id':50,'dict_cname':'橘子','dict_ename':'orange',},
            {'id':51,'dict_cname':'西蓝花','dict_ename':'broccoli',},
            {'id':52,'dict_cname':'胡萝卜','dict_ename':'carrot',},
            {'id':53,'dict_cname':'热狗','dict_ename':'hot dog',},
            {'id':54,'dict_cname':'披萨饼','dict_ename':'pizza',},
            {'id':55,'dict_cname':'甜甜圈','dict_ename':'donut',},
            {'id':56,'dict_cname':'蛋糕','dict_ename':'cake',},
            {'id':57,'dict_cname':'椅子','dict_ename':'chair',},
            {'id':58,'dict_cname':'沙发','dict_ename':'couch',},
            {'id':59,'dict_cname':'盆栽','dict_ename':'potted plant',},
            {'id':60,'dict_cname':'床','dict_ename':'bed',},
            {'id':61,'dict_cname':'餐桌','dict_ename':'dining table',},
            {'id':62,'dict_cname':'厕所','dict_ename':'toilet',},
            {'id':63,'dict_cname':'电视','dict_ename':'tv',},
            {'id':64,'dict_cname':'笔记本','dict_ename':'laptop',},
            {'id':65,'dict_cname':'老鼠','dict_ename':'mouse',},
            {'id':66,'dict_cname':'遥控器','dict_ename':'remote',},
            {'id':67,'dict_cname':'键盘','dict_ename':'keyboard',},
            {'id':68,'dict_cname':'手机','dict_ename':'cell phone',},
            {'id':69,'dict_cname':'微波炉','dict_ename':'microwave',},
            {'id':70,'dict_cname':'烤炉','dict_ename':'oven',},
            {'id':71,'dict_cname':'烤箱','dict_ename':'toaster',},
            {'id':72,'dict_cname':'水槽','dict_ename':'sink',},
            {'id':73,'dict_cname':'冰箱','dict_ename':'refrigerator',},
            {'id':74,'dict_cname':'书','dict_ename':'book',},
            {'id':75,'dict_cname':'时钟','dict_ename':'clock',},
            {'id':76,'dict_cname':'花瓶','dict_ename':'vase',},
            {'id':77,'dict_cname':'剪刀','dict_ename':'scissors',},
            {'id':78,'dict_cname':'泰迪熊','dict_ename':'teddy bear',},
            {'id':79,'dict_cname':'吹风机','dict_ename':'hair drier',},
            {'id':80,'dict_cname':'牙刷','dict_ename':'toothbrush',},
            {'id':81,'dict_cname':'玩手机','dict_ename':'phone',},
            {'id':82,'dict_cname':'遮挡','dict_ename':'cover',},
            {'id':83,'dict_cname':'未遮挡','dict_ename':'no_cover',},


        ]

        for i in dict_data:
            dict_res = Dict_data(id=i['id'],dict_cname=i['dict_cname'],dict_ename=i['dict_ename'])
            db.session.add(dict_res)
        db.session.commit()

        print('字典翻译数据插入完成！')

    if not Mine.query.first():

        mine_data = [
            {'id':1,'mine_name':'煤业'},
        ]

        for i in mine_data:
            mine_res = Mine(id=i['id'],mine_name=i['mine_name'])
            db.session.add(mine_res)
        db.session.commit()
        print('矿数据插入完成！')

    if not Diagnosis_type.query.first():

        diag_data = [
            {'id':1,'name':'视频抖动','prewarn':30,'warn':70},
            {'id':2,'name':'条纹干扰','prewarn':30,'warn':70},
            {'id':3,'name':'视频丢失','prewarn':30,'warn':70},
            {'id':4,'name':'视频遮挡','prewarn':30,'warn':70},
            {'id':5,'name':'视频冻结','prewarn':30,'warn':70},
            {'id':6,'name':'高亮度','prewarn':30,'warn':70},
            {'id':7,'name':'低亮度','prewarn':30,'warn':70},
            {'id':8,'name':'视频噪声','prewarn':30,'warn':70},
            {'id':9,'name':'偏色','prewarn':30,'warn':70},
            {'id':10,'name':'清晰度','prewarn':30,'warn':70},
            {'id':11,'name':'场景变化','prewarn':30,'warn':70},
            {'id':12,'name':'对比度','prewarn':30,'warn':70},
            {'id':13,'name':'横纹干扰','prewarn':30,'warn':70},
            {'id':14,'name':'滚动条纹','prewarn':30,'warn':70},
            {'id':15,'name':'横波干扰','prewarn':30,'warn':70},
        ]

        for i in diag_data:
            diag_res = Diagnosis_type(id=i['id'],name=i['name'],prewarn=i['prewarn'],warn=i['warn'])
            db.session.add(diag_res)
        db.session.commit()
        print('诊断类型检测项表！')

