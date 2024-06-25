import os
import dbutils.steady_db
from flask import jsonify, request, Blueprint
from configs import *
from modules.Tables import *
from sqlalchemy import and_, func, update, desc
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# 创建数据操作蓝图1，对应的register目录
model_views = Blueprint('model_views', __name__)

#离线状态的全局变量 默认为True
offline_status = True
#本次离线持续时间
offline_keepTime = 0
#设备的离线开始时间
offline_start_time = None


# 接口
@model_views.route('/diagnosis_all', methods=['GET'])
def diagnosis_all():

    return jsonify({'code': 200, 'message':'123'})


#监测点离线信息
@model_views.route('/monitorPoint_offline',methods=['GET'])
def monitorPoint_offline():
    # '设备名称'
    equipmentInfo = db.session.query(Equipment.id, Equipment.equipment_ip, Equipment.online,Equipment.duration_time).all()
    resultList = convert_folder_to_dict_list(equipmentInfo, ['id', 'equipment_ip', 'online','duration_time'])
    getDevRunStatus(resultList)
    for item_i in resultList:
        # 获取当前监测点的最后一条离线信息
        off_newInfo = db.session.query(
            Offline_info
        ).filter(Offline_info.equipment_id == item_i['id']).order_by(desc(Offline_info.id)).first()
        if item_i['online'] == 2:
            #如果查询结果为空，就新增一条离线信息，否则就更新最后一条离线信息的离线结束时间，并更新离线持续时间
            if off_newInfo is None:
                # 离线设备的信息
                offline_info_data = Offline_info(
                    equipment_id=item_i['id'],
                    offline_start_time=datetime.now(),
                    status='2',
                    create_time=datetime.now(),
                    offline_end_time = None,
                    equipment_ip = item_i['equipment_ip']
                )
                db.session.add(offline_info_data)
                db.session.commit()
            if off_newInfo is not None:
                for equip_item in equipmentInfo:
                    if equip_item.id == item_i['id']:
                        offline_durationTime = (datetime.now() - off_newInfo.offline_start_time).seconds
                        days = offline_durationTime // (24 * 3600)
                        hours = (offline_durationTime % (24 * 3600)) // 3600
                        minutes = (offline_durationTime % 3600) // 60
                        seconds = offline_durationTime % 60
                        equip_item.duration_time = f"{days}天{hours}时{minutes}分{seconds}秒"
                        update_query = (
                            update(Equipment)
                            .where(equip_item.id == item_i['id'])
                            .values(
                                duration_time=f"{days}天{hours}时{minutes}分{seconds}秒"
                            )
                        )
                #提交会话保存修改
                db.session.execute(update_query)
                db.session.commit()
        else:
            offline_status = True
            if off_newInfo is not None:
                off_newInfo.offline_end_time = datetime.now()
                offline_durationTime = (off_newInfo.offline_end_time - off_newInfo.offline_start_time).seconds
                days = offline_durationTime // (24 * 3600)
                hours = (offline_durationTime % (24 * 3600)) // 3600
                minutes = (offline_durationTime % 3600) // 60
                seconds = offline_durationTime % 60
                off_newInfo.offline_keep_time = f"{days}天{hours}时{minutes}分{seconds}秒"
                update_query = (
                    update(Offline_info)
                    .where(Offline_info.id == off_newInfo.id)
                    .values(
                        offline_end_time = datetime.now(),
                        offline_keep_time = f"{days}天{hours}时{minutes}分{seconds}秒"
                    )
                )
                #提交会话保存修改
                db.session.execute(update_query)
                db.session.commit()
    return jsonify({'code': 200, 'msg': '监测点离线数据写入成功'})
