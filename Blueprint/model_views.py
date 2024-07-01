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


# --------新筛选，录像机-监控点--------
@model_views.route('/vcr_em_select', methods=['GET'])
def vcr_em_select():
    # 录像机ip
    vcr_id = request.args.get('vcr_id')

    # 当选择录像机的时候展示录像机下子集数据
    if vcr_id:
        # 录像机下监控点列表数据
        em_list = db.session.query(Equipment).filter(Equipment.VCR_data_id==vcr_id,Equipment.parent_id!=None).all()
        # 序列化
        data = convert_folder_to_dict_list(em_list,['id','equipment_name','VCR_data_id','equipment_ip'])
        return jsonify({'code':200,'msg':'查询成功','em_data':data})

    # 当未选择录像机展示全部
    else:

        var_data = convert_folder_to_dict_list(db.session.query(VCR_data).all(),['id','vcr_name','vcr_ip'])
        em_data = convert_folder_to_dict_list(db.session.query(Equipment).filter(Equipment.parent_id !=None,Equipment.equipment_type == '录像机').all(),
                                              ['id','equipment_name','VCR_data_id','equipment_ip'])

        return jsonify({'code': 200, 'msg': '查询成功',
                        'var_data_name': '录像机列表',
                        'var_data': var_data,
                        'em_data_name': '监控点列表',
                        'em_data': em_data,

                        })


# --------诊断数据展示接口--------
@model_views.route('/diagnosis_all', methods=['GET'])
def diagnosis_all():

    # 录像机设备id
    vcr_id = request.args.get('vcr_id')

    # 监控点设备id
    equipment_id = request.args.get('equipment_id')

    # 诊断状态   达标  一般  很差  失败
    diagnosis_type = request.args.get('diagnosis_type')

    # 开始时间
    start_time = request.args.get('start_time')
    # 结束时间
    end_time = request.args.get('end_time')

    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=15, type=int)

    # 假设前端传递的参数为可能有一个或多个
    filters = []

    # 如果存在录像机id
    if vcr_id:
        filters.append(VCR_data.id == vcr_id)

    # 如果存在监控点id
    if equipment_id:
        filters.append(and_(Diagnosis_data.equipment_id == equipment_id))  # 修改为使用 and_ 函数
        # filters.append(and_(Diagnosis_data.parent_id != None))  # 修改为使用 and_ 函数

    # 如果存在状态参数，加入过滤条件
    if diagnosis_type:
        filters.append(Diagnosis_data.diagnosis_type == diagnosis_type)

    # 如果存在开始时间和结束时间参数，加入过滤条件
    if start_time and end_time:
        # 查询在开始时间跟结束时间之内
        filters.append(Diagnosis_data.create_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))


    # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and
    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None

    if query_filter is not None:
        res = db.session.query(
            Diagnosis_data.id,
            Diagnosis_data.equipment_id,Diagnosis_data.equipment_ip,
            Diagnosis_data.equipment_name,Diagnosis_data.vcr_ip,
            Diagnosis_data.diagnosis_type,Diagnosis_data.db101,Diagnosis_data.db102,
            Diagnosis_data.db103,Diagnosis_data.db104,Diagnosis_data.db105,
            Diagnosis_data.db106,Diagnosis_data.db107,Diagnosis_data.db108,
            Diagnosis_data.db109,Diagnosis_data.db110,Diagnosis_data.db111,
            Diagnosis_data.db112,Diagnosis_data.db113,Diagnosis_data.db114,
            Diagnosis_data.db115,Diagnosis_data.create_time,VCR_data.vcr_name,
            VCR_data.id.label('vcr_id'),
        ).join(
            VCR_data,
            Diagnosis_data.vcr_ip==VCR_data.vcr_ip
        ).filter(query_filter).paginate(page=page, per_page=per_page,error_out=False)

    else:
        res = db.session.query(
            Diagnosis_data.id,
            Diagnosis_data.equipment_id,Diagnosis_data.equipment_ip,
            Diagnosis_data.equipment_name,Diagnosis_data.vcr_ip,
            Diagnosis_data.diagnosis_type,Diagnosis_data.db101,Diagnosis_data.db102,
            Diagnosis_data.db103,Diagnosis_data.db104,Diagnosis_data.db105,
            Diagnosis_data.db106,Diagnosis_data.db107,Diagnosis_data.db108,
            Diagnosis_data.db109,Diagnosis_data.db110,Diagnosis_data.db111,
            Diagnosis_data.db112,Diagnosis_data.db113,Diagnosis_data.db114,
            Diagnosis_data.db115,Diagnosis_data.create_time,VCR_data.vcr_name,
            VCR_data.id.label('vcr_id'),
        ).join(
            VCR_data,
            Diagnosis_data.vcr_ip==VCR_data.vcr_ip
        ).paginate(page=page, per_page=per_page, error_out=False)


    res_data = [{
        'id': i.id,
        'equipment_id': i.equipment_id,
        'equipment_ip': i.equipment_ip,
        'equipment_name': i.equipment_name,
        'vcr_ip': i.vcr_ip,
        'vcr_name': i.vcr_name,
        'vcr_id': i.vcr_id,
        'diagnosis_type': i.diagnosis_type,
        'db101': i.db101,'db102': i.db102,'db103': i.db103,
        'db104': i.db104,'db105': i.db105,'db106': i.db106,
        'db107': i.db107,'db108': i.db108,'db109': i.db109,
        'db110': i.db110,'db111': i.db111,'db112': i.db112,
        'db113': i.db113,'db114': i.db114,'db115': i.db115,
        'create_time': (i.create_time).strftime("%Y-%m-%d %H:%M:%S"),

    } for i in res.items]


    response_data = {
        'total_items': res.total,
        'total_pages': res.pages,
        'current_page': res.page,
        'per_page': per_page,
        'data': res_data,
    }

    return jsonify({'code': 200, 'msg': '查询成功', 'data': response_data})



#监测点离线信息
@model_views.route('/monitorPoint_offline',methods=['GET'])
def monitorPoint_offline():
    # '设备名称'
    equipmentInfo = db.session.query(Equipment.id, Equipment.equipment_ip, Equipment.online,Equipment.duration_time,Equipment.equipment_online_time,Equipment.equipment_offline_time).all()
    #设备状态字典
    equipmentStatusList = convert_folder_to_dict_list(equipmentInfo, ['id', 'equipment_ip', 'online','duration_time','equipment_online_time','equipment_offline_time'])
    getDevRunStatus(equipmentStatusList)

    for equip_item in equipmentInfo:
        for equipStatus_item in equipmentStatusList:
            if equip_item.id == equipStatus_item['id']:
                #设备表中的状态为离线  获取的设备状态为在线
                if equip_item.online == 2 and equipStatus_item['online'] == 1:
                    db.session.execute(
                        update(Equipment)
                        .where(Equipment.id == equip_item.id)
                        .values(online=equipStatus_item['online'],
                                duration_time=None,
                                equipment_online_time=datetime.now(),
                                equipment_offline_time=None,
                        )
                    )
                    db.session.commit()
                elif equip_item.online == 1 and equipStatus_item['online'] == 2:
                    db.session.execute(
                        update(Equipment)
                        .where(Equipment.id == equip_item.id)
                        .values(
                            online=equipStatus_item['online'],
                            equipment_offline_time=datetime.now(),
                            equipment_online_time=None,
                            duration_time='0天0时0分0秒'
                        )
                    )
                    db.session.commit()
                    #记录离线的设备信息
                    offline_info = Offline_info(
                        equipment_id=equip_item.id,
                        equipment_ip=equip_item.equipment_ip
                    )
                    db.session.add(offline_info)
                    db.session.commit()
                elif equip_item.online == 2 and equipStatus_item['online'] == 2:
                    offline_durationTime = (datetime.now() - equip_item.equipment_offline_time).seconds
                    days = offline_durationTime // (24 * 3600)
                    hours = (offline_durationTime % (24 * 3600)) // 3600
                    minutes = (offline_durationTime % 3600) // 60
                    seconds = offline_durationTime % 60
                    db.session.execute(
                        update(Equipment)
                        .where(Equipment.id == equip_item.id)
                        .values(
                            duration_time=f"{days}天{hours}时{minutes}分{seconds}秒"
                        )
                    )
                    db.session.commit()


    return jsonify({'code': 200, 'msg': '监测点离线数据写入成功'})
