import os
import dbutils.steady_db
from flask import jsonify, request, Blueprint
from configs import *
from modules.Tables import *
from sqlalchemy import and_,func,update
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# 创建数据操作蓝图1，对应的register目录
model_views = Blueprint('model_views', __name__)


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

