import datetime

import dbutils.steady_db
from flask import jsonify, request, Blueprint
import configs
from configs import *
from modules.Tables import *
from sqlalchemy import and_,func,update


import os

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# 创建蓝图，对应的register目录
model_view = Blueprint('model_view', __name__)


# 设备添加接口
@model_view.route('/equipment_create', methods=['POST'])
def equipment_create():

    equipment_type = request.json.get('equipment_type', None)  # '设备类型' ('摄像头','录像机','特殊摄像头','浙江双视热成像')
    manufacturer_type = request.json.get('manufacturer_type', None)  # ('海康', '大华','索尼','宇视','天地伟业','三星','浙江双视觉') 厂商类型
    equipment_name = request.json.get('equipment_name', None)  # '设备名称'
    equipment_ip = request.json.get('equipment_ip', None)  # 'IP地址'
    equipment_uname = request.json.get('equipment_uname', None)  # '用户名'
    equipment_password = request.json.get('equipment_password', None)  # '密码'
    equipment_aisles = request.json.get('equipment_aisles', None)  # '通道'
    equipment_codetype = request.json.get('equipment_codetype', None)  # ('H265','H264') '码流类型'
    Mine_id = request.json.get('Mine_id', None)  # '矿名称id'
    flower_frames = request.json.get('flower_frames', None)  # '花帧阈值'

    # 当为录像机的时候传子设备数据
    children_list = request.json.get('children_list', None)

    equipment_type = (configs.equipment_type[int(equipment_type)-1])['value'] if equipment_type else 1
    manufacturer_type = (configs.manufacturer_type[int(manufacturer_type)-1])['value'] if manufacturer_type else 1
    equipment_codetype = (configs.equipment_codetype[int(equipment_codetype)-1])['value'] if  equipment_codetype else 1

    # 参数构建判断是否为空
    params = [equipment_type, equipment_name, equipment_ip, equipment_uname,equipment_password,Mine_id]

    if not all(params):
        return jsonify({'code': 400, 'msg': '设备数据有未填写项'})

    # 查询user_id是否存在
    equipment_result = db.session.query(Equipment).filter(Equipment.equipment_ip == equipment_ip).first()
    if equipment_result:
        return jsonify({'code': 400, 'msg': '设备已经存在'})


    # 判断当添加数据类型为 '录像机'  子列表数据添加
    if equipment_type == '录像机':
        # 添加录像机父设备
        equipment_data = Equipment(

            equipment_type=equipment_type if equipment_type in ['摄像头', '录像机', '特殊摄像头', '浙江双视热成像'] else None,
            manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业',
                                                                         '三星','浙江双视'] else None,
            equipment_name=equipment_name if equipment_name else None,
            equipment_ip=equipment_ip if equipment_ip is not None else None,
            equipment_uname=equipment_uname if equipment_uname else None,
            equipment_password=equipment_password if equipment_password else None,
            equipment_aisles=equipment_aisles if equipment_aisles else None,
            equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
            Mine_id=int(Mine_id) if Mine_id else None,
            flower_frames=flower_frames if flower_frames else None,
        )
        db.session.add(equipment_data)
        db.session.commit()

        if children_list:

            # 获取对应子集数据的  默认通道 code 数据
            children_list = children_list_get_code(children_list)

            for i in children_list:
                # 添加录像机子设备
                child_equipment_data = Equipment(
                    equipment_type=equipment_data.equipment_type if equipment_data.equipment_type else None,
                    manufacturer_type=equipment_data.manufacturer_type if equipment_data.manufacturer_type  else None,
                    equipment_name=i['equipment_name'] if i.get('equipment_name') else None,
                    equipment_ip=i['equipment_ip'] if i.get('equipment_ip') is not None else None,
                    equipment_uname=equipment_data.equipment_uname if equipment_data.equipment_uname else None,
                    equipment_password=equipment_data.equipment_password if equipment_data.equipment_password else None,
                    equipment_aisles=i.get('equipment_aisles') if i.get('equipment_aisles') else None,
                    equipment_codetype=equipment_data.equipment_codetype if equipment_data.equipment_codetype else None,
                    Mine_id=int(equipment_data.Mine_id) if equipment_data.Mine_id else None,
                    parent_id=int(equipment_data.id) if equipment_data.id else None,
                    code=i.get('code') if i.get('code') else None,
                    flower_frames=flower_frames if flower_frames else None,

                )
                db.session.add(child_equipment_data)
                db.session.commit()

    #  判断当类型为特殊摄像头的时候，特殊摄像头下方账密子集继承特殊摄像头的账密ip
    elif equipment_type == '特殊摄像头':
        # 添加录像机父设备
        equipment_data = Equipment(

            equipment_type=equipment_type if equipment_type in ['摄像头', '录像机', '特殊摄像头', '浙江双视热成像'] else None,
            manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业',
                                                                         '三星','浙江双视'] else None,
            equipment_name=equipment_name if equipment_name else None,
            equipment_ip=equipment_ip if equipment_ip is not None else None,
            equipment_uname=equipment_uname if equipment_uname else None,
            equipment_password=equipment_password if equipment_password else None,
            equipment_aisles=equipment_aisles if equipment_aisles else None,
            equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
            Mine_id=int(Mine_id) if Mine_id else None,
            flower_frames=flower_frames if flower_frames else None,
        )
        db.session.add(equipment_data)
        db.session.commit()

        if children_list:

            # 获取对应子集数据的  默认通道 code 数据
            children_list = children_list_get_code(children_list)

            for i in children_list:
                # 添加录像机子设备
                child_equipment_data = Equipment(
                    equipment_type=equipment_data.equipment_type if equipment_data.equipment_type else None,
                    manufacturer_type=equipment_data.manufacturer_type if equipment_data.manufacturer_type else None,
                    equipment_name=equipment_data.equipment_name if equipment_data.equipment_name else None,
                    equipment_ip=equipment_data.equipment_ip if equipment_data.equipment_ip is not None else None,
                    equipment_uname=equipment_data.equipment_uname if equipment_data.equipment_uname else None,
                    equipment_password=equipment_data.equipment_password if equipment_data.equipment_password else None,
                    equipment_aisles=i.get('equipment_aisles') if i.get('equipment_aisles') else None,
                    equipment_codetype=equipment_data.equipment_codetype if equipment_data.equipment_codetype else None,
                    Mine_id=int(equipment_data.Mine_id) if equipment_data.Mine_id else None,
                    parent_id=int(equipment_data.id) if equipment_data.id else None,
                    code=i.get('code') if i.get('code') else None,
                    flower_frames=flower_frames if flower_frames else None,
                )
                db.session.add(child_equipment_data)
                db.session.commit()

    elif equipment_type == '摄像头':
        equipment_data = Equipment(
            equipment_type=equipment_type if equipment_type in ['摄像头', '录像机', '特殊摄像头', '浙江双视热成像'] else None,
            manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业',
                                                                         '三星','浙江双视'] else None,
            equipment_name=equipment_name if equipment_name else None,
            equipment_ip=equipment_ip if equipment_ip is not None else None,
            equipment_uname=equipment_uname if equipment_uname else None,
            equipment_password=equipment_password if equipment_password else None,
            equipment_aisles=equipment_aisles if equipment_aisles else None,
            equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
            Mine_id=int(Mine_id) if Mine_id else None,
            flower_frames=flower_frames if flower_frames else None,
        )
        db.session.add(equipment_data)
        db.session.commit()
    elif equipment_type == '浙江双视热成像':
        equipment_data = Equipment(
            equipment_type=equipment_type if equipment_type in ['摄像头', '录像机', '特殊摄像头', '浙江双视热成像'] else None,
            manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业',
                                                                         '三星','浙江双视'] else None,
            equipment_name=equipment_name if equipment_name else None,
            equipment_ip=equipment_ip if equipment_ip is not None else None,
            equipment_uname=equipment_uname if equipment_uname else None,
            equipment_password=equipment_password if equipment_password else None,
            equipment_aisles=equipment_aisles if equipment_aisles else None,
            equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
            Mine_id=int(Mine_id) if Mine_id else None,
            flower_frames=flower_frames if flower_frames else None,
        )
        db.session.add(equipment_data)
        db.session.commit()


    return jsonify({'code': 200, 'msg': '设备添加成功', })


# 单设备数据详情展示接口
@model_view.route('/equipment_one_info', methods=['GET'])
def equipment_one_info():

    # 查找所传当前设备id
    equipment_id = request.args.get('equipment_id', None)

    # orm根据id查找对应详情
    equipment_info = db.session.query(
        Equipment.equipment_name,
        Equipment.equipment_type,
        Equipment.code.label('equipment_code'),
    ).filter(Equipment.id == equipment_id).first()

    # 序列化
    equipment_info = convert_folder_to_dict_list(equipment_info,['equipment_name','equipment_type','equipment_code'])
    return jsonify({'code':200,'msg':'查询成功','data':equipment_info})



# 设备数据展示接口 （新） 录像机父子
@model_view.route('/equipment_show', methods=['GET'])
def equipment_show():

    # '设备id'
    equipment_name = request.args.get('equipment_name', None)
    # '设备类型' ('摄像头','录像机','特殊摄像头',’浙江双视摄像头’)
    equipment_type = request.args.get('equipment_type', None)


    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=15, type=int)


    # 判断是否为子类，如果是子类数据  if parent_id 写对应代码逻辑 如果是父类走下面代码逻辑
    # 查询该设备的 parent_id，如果 parent_id 不为 None，说明是子类
    parent_id = db.session.query(Equipment.parent_id).filter(Equipment.id == equipment_name).scalar()

    # 当 parent_id 不为空
    if parent_id is not None:

        # 子类逻辑
        # 假设前端传递的参数为 equipment_name 和 equipment_type，可能有一个或两个
        filters = []

        if equipment_name:
            filters.append(Equipment.id == equipment_name)

        if equipment_type:

            equipment_type = (configs.equipment_type[int(equipment_type) - 1])['value']
            filters.append(Equipment.equipment_type == equipment_type)

        # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and

        if len(filters) >= 2:
            query_filter = and_(*filters)
        else:
            query_filter = filters[0] if filters else None

        if query_filter is not None:
            equipment_info = db.session.query(
                Equipment.id, Equipment.equipment_type,
                Equipment.manufacturer_type, Equipment.equipment_name,
                Equipment.equipment_ip, Equipment.equipment_uname,
                Equipment.equipment_password, Equipment.equipment_aisles,
                Equipment.equipment_codetype, Equipment.user_status,
                Equipment.create_time,Equipment.parent_id,Equipment.code,Equipment.flower_frames
            ).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
        else:
                equipment_info = db.session.query(
                Equipment.id, Equipment.equipment_type,
                Equipment.manufacturer_type, Equipment.equipment_name,
                Equipment.equipment_ip, Equipment.equipment_uname,
                Equipment.equipment_password, Equipment.equipment_aisles,
                Equipment.equipment_codetype, Equipment.user_status,
                Equipment.create_time,Equipment.parent_id,Equipment.code,Equipment.flower_frames
            ).paginate(page=page, per_page=per_page, error_out=False)


        # 连表查询获取模型应用数据列表
        equipment_list = [{
            'id': i.id, 'equipment_type': i.equipment_type,
            'manufacturer_type': i.manufacturer_type,
            'flower_frames': i.flower_frames,
            'equipment_name': i.equipment_name,
            'equipment_ip': i.equipment_ip,
            'equipment_uname': i.equipment_uname,
            'equipment_password': i.equipment_password,
            'equipment_aisles': i.equipment_aisles,
            'equipment_codetype': i.equipment_codetype,
            'equipment_code': i.code,
            'user_status': i.user_status,
            'parent_id': i.parent_id,
            'create_time': i.create_time,
        } for i in equipment_info.items]

        # 构建返回的 JSON
        response_data = {
            'total_items': equipment_info.total,
            'total_pages': equipment_info.pages,
            'current_page': equipment_info.page,
            'per_page': per_page,
            'data': equipment_list,
        }

        return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})

    # 当 parent_id 为空
    else:

        # 父类逻辑
        # 假设前端传递的参数为 equipment_name 和 equipment_type，可能有一个或两个
        filters = []

        filters.append(Equipment.parent_id == None)

        if equipment_name:
            filters.append(Equipment.id == equipment_name)

        if equipment_type:

            equipment_type = (configs.equipment_type[int(equipment_type) - 1])['value']
            filters.append(Equipment.equipment_type == equipment_type)

        # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and

        if len(filters) >= 2:
            query_filter = and_(*filters)
        else:
            query_filter = filters[0] if filters else None


        if query_filter is not None:
            equipment_info = db.session.query(
                Equipment.id, Equipment.equipment_type,
                Equipment.manufacturer_type, Equipment.equipment_name,
                Equipment.equipment_ip, Equipment.equipment_uname,
                Equipment.equipment_password, Equipment.equipment_aisles,
                Equipment.equipment_codetype, Equipment.user_status,
                Equipment.create_time,Equipment.parent_id,Equipment.code,Equipment.flower_frames
            ).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
        else:
                equipment_info = db.session.query(
                Equipment.id, Equipment.equipment_type,
                Equipment.manufacturer_type, Equipment.equipment_name,
                Equipment.equipment_ip, Equipment.equipment_uname,
                Equipment.equipment_password, Equipment.equipment_aisles,
                Equipment.equipment_codetype, Equipment.user_status,
                Equipment.create_time,Equipment.parent_id,Equipment.code,Equipment.flower_frames
            ).paginate(page=page, per_page=per_page, error_out=False)


        # 连表查询获取模型应用数据列表
        equipment_list = [{
            'id': i.id, 'equipment_type': i.equipment_type,
            'manufacturer_type': i.manufacturer_type,
            'flower_frames': i.flower_frames,
            'equipment_name': i.equipment_name,
            'equipment_ip': i.equipment_ip,
            'equipment_uname': i.equipment_uname,
            'equipment_password': i.equipment_password,
            'equipment_aisles': i.equipment_aisles,
            'equipment_codetype': i.equipment_codetype,
            'equipment_code': i.code,
            'user_status': i.user_status,
            'parent_id': i.parent_id,
            'create_time': i.create_time,
        } for i in equipment_info.items]


        # 使用列表推导式筛选设备类型为“录像机”的记录
        equipment_VCR = [record for record in equipment_info.items if record.equipment_type == '录像机' or record.equipment_type == '特殊摄像头']
        # 提取录像机的 ID
        vcr_ids = [record.id for record in equipment_VCR]

        equipment_list = children_data(equipment_list,vcr_ids)

        # 构建返回的 JSON
        response_data = {
            'total_items': equipment_info.total,
            'total_pages': equipment_info.pages,
            'current_page': equipment_info.page,
            'per_page': per_page,
            'data': equipment_list,
        }

        return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})


@model_view.route('/equipment_status', methods=['GET'])
def equipment_status():
    # '设备名称'
    equipmentInfo = db.session.query(Equipment.id, Equipment.equipment_ip, Equipment.online).all()
    resultList = convert_folder_to_dict_list(equipmentInfo, ['id', 'equipment_ip', 'online'])
    getDevRunStatus(resultList)
    for resultList_i in resultList:
        # 查询当前ip对应的设备是否存在
        equipment_result = db.session.query(Equipment).filter(
            Equipment.equipment_ip == resultList_i['equipment_ip']).first()
        print(equipment_result)
        if equipment_result is not None:
            equipment_result.online = resultList_i['online']
            # 提交会话以保存更改
        db.session.commit()
    print(resultList)
    return resultList


# 设备修改接口
@model_view.route('/equipment_update', methods=['POST'])
def equipment_update():

    # '设备id'
    equipment_name = request.form.get('equipment_name', None)

    # type 当type为1查询，当type为2修改
    type_s = request.form.get('type', None)

    params = [type_s, equipment_name]

    if not all(params):
        return jsonify({'code': 400, 'msg': '数据有未填写项'})

    if int(type_s) == 1:

        equipment_info = db.session.query(
            Equipment.id, Equipment.equipment_type,Equipment.Mine_id,
            Equipment.manufacturer_type, Equipment.equipment_name,
            Equipment.equipment_ip, Equipment.equipment_uname,
            Equipment.equipment_password, Equipment.equipment_aisles,
            Equipment.equipment_codetype, Equipment.user_status,
            Equipment.create_time, Equipment.parent_id, Equipment.code, Equipment.flower_frames
        ).filter(Equipment.id == equipment_name).first()

        # 设备应用数据列表
        equipment_list = {
            'id': equipment_info.id, 'equipment_type': equipment_info.equipment_type,
            'manufacturer_type': equipment_info.manufacturer_type,
            'flower_frames': equipment_info.flower_frames,
            'equipment_name': equipment_info.equipment_name,
            'equipment_ip': equipment_info.equipment_ip,
            'equipment_uname': equipment_info.equipment_uname,
            'equipment_password': equipment_info.equipment_password,
            'equipment_aisles': equipment_info.equipment_aisles,
            'equipment_codetype': equipment_info.equipment_codetype,
            'equipment_code': equipment_info.code,
            'user_status': equipment_info.user_status,
            'parent_id': equipment_info.parent_id,
            'Mine_id': equipment_info.Mine_id,
            'create_time': (equipment_info.create_time).strftime("%Y-%m-%d %H:%M:%S"),
        }

        return jsonify({'code': 200, 'data': equipment_list})


    else:
        id = request.form.get('id', None)
        equipment_type = request.form.get('equipment_type', None)  # '设备类型' ('摄像头','录像机','特殊摄像头','浙江双视热成像')
        manufacturer_type = request.form.get('manufacturer_type', None)  # ('海康', '大华','索尼','宇视','天地伟业','三星','浙江双视') 厂商类型
        equipment_name = request.form.get('equipment_name', None)  # '设备名称'
        equipment_ip = request.form.get('equipment_ip', None)  # 'IP地址'
        equipment_uname = request.form.get('equipment_uname', None)  # '用户名'
        equipment_password = request.form.get('equipment_password', None)  # '密码'
        equipment_aisles = request.form.get('equipment_aisles', None)  # '通道'
        equipment_codetype = request.form.get('equipment_codetype', None)  # ('H265','H264') '码流类型'
        Mine_id = request.form.get('Mine_id', None)  # '矿名称id'
        flower_frames = request.form.get('flower_frames', None)  # '花帧阈值'


        equipment_type = (configs.equipment_type[int(equipment_type) - 1])['value'] if equipment_type else 1
        manufacturer_type = (configs.manufacturer_type[int(manufacturer_type) - 1])['value'] if manufacturer_type else 1
        equipment_codetype = (configs.equipment_codetype[int(equipment_codetype) - 1])[
            'value'] if equipment_codetype else 1

        # print(equipment_type,manufacturer_type,equipment_codetype)


        # 查询user_id是否存在
        equipment_result = db.session.query(Equipment).filter(Equipment.id == id).first()
        print(equipment_result,'设备id是否存在',equipment_type)

        if equipment_result and equipment_type != '特殊摄像头' or equipment_type != '浙江双视热成像':

            equipment_result.equipment_type = equipment_type if equipment_type in ['摄像头', '录像机', '特殊摄像头', '浙江双视热成像'] else None
            equipment_result.manufacturer_type = manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业',
                                                                         '三星', '浙江双视'] else None
            equipment_result.equipment_name = equipment_name
            equipment_result.equipment_ip = equipment_ip
            equipment_result.equipment_uname = equipment_uname
            equipment_result.equipment_password = equipment_password
            equipment_result.equipment_aisles = equipment_aisles
            equipment_result.equipment_codetype = equipment_codetype if equipment_codetype in ['H265', 'H264'] else None
            equipment_result.Mine_id = Mine_id
            equipment_result.flower_frames = flower_frames if flower_frames and flower_frames != '0' else None

            update_query = (
                update(VCR_data)
                    .where(VCR_data.id == equipment_result.VCR_data_id)
                    .values(
                    vcr_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业', '三星','浙江双视'] else None,
                    vcr_name=equipment_name,
                    vcr_ip=equipment_ip,
                    vcr_username=equipment_uname,
                    vcr_password=equipment_password,
                    Mine_id=Mine_id,
                )
            )

            update_query_children = (
                update(Equipment)
                    .where(Equipment.VCR_data_id == equipment_result.VCR_data_id,Equipment.parent_id != None)
                    .values(
                    manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业', '三星','浙江双视'] else None,
                    Mine_id=Mine_id,
                )
            )

            # 执行更新
            db.session.execute(update_query)
            db.session.execute(update_query_children)

            # 提交会话以保存更改
            db.session.commit()

        # 当为特殊摄像头时，不管子类还是父类一个改都改变
        else:
            # 先确定是否为父类，如果不是父类，查找数据对应当前 (parent_id) 修改 再查找parent_id 为id数据进行修改
            if equipment_result.parent_id:
                print('不是父类',equipment_result.parent_id)
                # 查找id为父类id的数据和父类parent_id为id的数据
                # 构建更新查询
                update_query = (
                    update(Equipment)
                        .where((Equipment.id == equipment_result.parent_id) | (
                                Equipment.parent_id == equipment_result.parent_id))
                        .values(
                        equipment_name=equipment_name,
                        equipment_ip=equipment_ip,
                        equipment_uname=equipment_uname,
                        equipment_password=equipment_password,
                        Mine_id=Mine_id,
                        flower_frames=flower_frames,
                        equipment_aisles = equipment_aisles,
                        equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
                        manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视',
                                                                                            '天地伟业', '三星','浙江双视'] else None,
                    )
                )

                # 执行更新
                db.session.execute(update_query)
                db.session.commit()

            # 如果是父类，查找等于parent_id父类id数据，进行修改
            else:
                print('是父类',equipment_result.id)
                # 查找id为父类id的数据和父类parent_id为id的数据
                # 构建更新查询
                update_query = (
                    update(Equipment)
                        .where((Equipment.id == equipment_result.id) | (
                                Equipment.parent_id == equipment_result.id))
                        .values(
                        equipment_name=equipment_name,
                        equipment_ip=equipment_ip,
                        equipment_uname=equipment_uname,
                        equipment_password=equipment_password,
                        equipment_aisles = equipment_aisles,
                        Mine_id=Mine_id,
                        flower_frames=flower_frames,
                        equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
                        manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视',
                                                                                            '天地伟业', '三星','浙江双视'] else None,
                    )
                )
                # 执行更新
                db.session.execute(update_query)
                db.session.commit()


        # redis队列 当算法配置修改完成时，数据写入队列，寒武纪盒子redis监听到数据重新执行
        queue_redis = TestQueue()
        queue_redis.push()

        return jsonify({'code': 200, 'msg': '设备修改完成!'})



# 设备删除接口
@model_view.route('/equipment_delete', methods=['POST'])
def equipment_delete():

    # '设备id'
    equipment_id = request.json.get('equipment_id', None)
    print(equipment_id)


    # 查找 id 对应数据，如果该id的parent_id为none 查找她下方是否有子类 如果有子类删除  没有删除该值

    # 如果parent_id有值那么只删除该值
    if equipment_id:
        for i in equipment_id:
            if i.get('children'):
                db.session.query(Equipment).filter_by(id=i['id']).delete()
                db.session.commit()
                for i in i.get('children'):
                    db.session.query(Equipment).filter_by(id=i['id']).delete()
                    db.session.commit()
            else:
                db.session.query(Equipment).filter_by(id=i['id']).delete()
                db.session.commit()

        return jsonify({'code': 200, 'msg': '删除成功'})
    else:

        return jsonify({'code': 400, 'msg': '缺少设备id参数'})




# 选择算法，返回算法对应检测额类型
@model_view.route('/Algorithm_type_select', methods=['GET'])
def Algorithm_type_select():
    # 算法id
    Algorithm_library_id = request.args.get('id', None)
    # 查询对应算法数据
    algorithm_data = db.session.query(Algorithm_test_type.id,Algorithm_test_type.test_type_ename,Algorithm_test_type.Algorithm_library_id).filter(Algorithm_test_type.Algorithm_library_id==Algorithm_library_id).all()
    algorithm_data = convert_folder_to_dict_list(algorithm_data,['id','test_type_ename','Algorithm_library_id',])
    return jsonify({'code': 200, 'data': algorithm_data})




# 筛选返回接口
@model_view.route('/type_select', methods=['GET'])
def type_select():
    # 矿类型id
    mine_id = request.args.get('mine_id', None)


    # 算法数据返回
    algorithm_data = db.session.query(Algorithm_library.id,
                                      Algorithm_library.algorithm_name,
                                      Algorithm_library.algorithm_file_name,
                                      Algorithm_library.algorithm_type,
                                      ).all()
    # 算法列表组装
    algorithm_list = [{'id': i.id, 'algorithm_name': i.algorithm_name,
                       'algorithm_file_name': i.algorithm_file_name, 'algorithm_type': i.algorithm_type, } for i in
                      algorithm_data]

    # 算法配置项数据返回
    algorithm_conf = convert_folder_to_dict_list(db.session.query(Algorithm_config.id,Algorithm_config.conf_name).all(),['id','conf_name',])



    # 字典数据返回
    dict_data = convert_folder_to_dict_list(db.session.query(Dict_data.id,Dict_data.dict_cname,Dict_data.dict_ename).all(),['id','dict_cname','dict_ename'])

    # 质量诊断类型返回
    diagnosis_type_result = convert_folder_to_dict_list(
        db.session.query(Diagnosis_type.id, Diagnosis_type.name, Diagnosis_type.prewarn,Diagnosis_type.warn).all(),
        ['id', 'name', 'prewarn','warn'])

    # 当选择矿类型id，展示  （矿,矿下监控点,算法）筛选数据
    if mine_id:
        mine_data = db.session.query(Mine.id, Mine.mine_name, ).all()
        mine_list = [{'id': i.id, 'mine_name': i.mine_name, } for i in mine_data]

        equipment_data = db.session.query(Equipment).filter(
            Equipment.Mine_id == int(mine_id),Equipment.parent_id == None).all()

        # 定义接受列表
        equipment_list = []
        # 定义rtso局部变量
        rtsp = ''
        for i in equipment_data:

            # 判断摄像头类型获取rtsp流
            if i.equipment_type == '摄像头':
                rtsp = 'rtsp://{}:{}@{}'.format(i.equipment_uname, i.equipment_password,i.equipment_ip)
            elif i.equipment_type == '录像机':
                rtsp = get_children_rtsp(i.parent_id, i.code, 1)
            elif i.equipment_type ==  '特殊摄像头':
                rtsp = get_children_rtsp(i.parent_id, i.code, 2)
            elif i.equipment_type == '浙江双视热成像':
                rtsp = 'rtsp://{}:{}@{}:554/live/chn0'.format(i.equipment_uname,i.equipment_password,i.equipment_ip)

            dict_res = {'id':i.id,'equipment_name': i.equipment_name,'equipment_type':i.equipment_type,'rtsp':rtsp}

            equipment_list.append(dict_res)

        # print(equipment_list)


        # equipment_list = [
        #     {'id': i.id, 'equipment_name': i.equipment_name,'equipment_type':i.equipment_type,
        #
        #     'rtsp': 'rtsp://{}:{}@{}'.format(i.equipment_uname, i.equipment_password,i.equipment_ip)
        #     if i.equipment_type == '摄像头'
        #     else
        #     (
        #         get_children_rtsp(i.parent_id, i.code, 2)
        #         if i.equipment_type == '特殊摄像头' else get_children_rtsp(i.parent_id,i.code, 1)
        #
        #         (
        #
        #             'rtsp://{}:{}@{}'.format(1, 2, 3) if i.equipment_type == '浙江双视热成像' else get_children_rtsp(
        #                 i.parent_id, i.code, 1)
        #
        #         )
        #     ),
        #
        #      } for i in equipment_data]


        # 使用列表推导式筛选设备类型为“录像机”的记录 取录像机的 ID
        vcr_ids = [i['id'] for i in equipment_list if i['equipment_type'] == '录像机' or i['equipment_type'] == '特殊摄像头']

        # 调用方法数据构造
        equipment_list = children_data(equipment_list, vcr_ids)
        # print(equipment_list)


        return jsonify({'code': 200, 'msg': '筛选数据',
                        'mine_list': mine_list,
                        'mine_list_name': '矿数据返回列表',
                        'equipment_list': equipment_list,
                        'equipment_list_name': '监控点数据返回列表',
                        'algorithm_list': algorithm_list,
                        'algorithm_list_name': '算法数据返回列表',
                        'algorithm_conf_list': algorithm_conf,
                        'algorithm_conf_list_name': '算法配置返回列表',
                        'type_list': configs.type_status,
                        'type_list_name': '预警数据返回列表',
                        'equipment_type': configs.equipment_type,
                        'equipment_type_name': '设备类型数据返回列表',
                        'manufacturer_type': configs.manufacturer_type,
                        'manufacturer_type_name': '厂商类型数据返回列表',
                        'equipment_codetype': configs.equipment_codetype,
                        'equipment_codetype_name': '码流类型数据返回列表',
                        'vcr_way':configs.vcr_way,
                        'vcr_name': '接入方式数据返回列表',
                        'dict_data':dict_data,
                        'dict_data_name':'字段数据列表',
                        'diagnosis_type_result':diagnosis_type_result,
                        'diagnosis_type_result_name':'诊断类型列表返回',
                        })
    # 当不选择的时候展示全部数据
    else:
        mine_data = db.session.query(Mine.id, Mine.mine_name, ).all()
        mine_list = [{'id': i.id, 'mine_name': i.mine_name, } for i in mine_data]

        equipment_data = db.session.query(Equipment).filter(Equipment.parent_id==None).all()
        # equipment_list = [{'id': i.id, 'equipment_name': i.equipment_name,'equipment_type':i.equipment_type ,
        #
        # 'rtsp': 'rtsp://{}:{}@{}'.format(i.equipment_uname, i.equipment_password,i.equipment_ip)
        # if i.equipment_type == '摄像头'
        #
        # else
        # (
        #
        #  get_children_rtsp(i.parent_id, i.code, 2)
        #
        #  if i.equipment_type == '特殊摄像头' else get_children_rtsp(i.parent_id,i.code, 1)
        #
        #     (
        #
        #      'rtsp://{}:{}@{}'.format(1, 2,3) if i.equipment_type == '浙江双视热成像' else get_children_rtsp(i.parent_id, i.code, 1)
        #
        #     )
        #
        #  ),
        #
        #                    } for i in equipment_data]
        # 定义接受列表

        equipment_list = []
        # 定义rtso局部变量
        rtsp = ''
        for i in equipment_data:

            # 判断摄像头类型获取rtsp流
            if i.equipment_type == '摄像头':
                rtsp = 'rtsp://{}:{}@{}'.format(i.equipment_uname, i.equipment_password, i.equipment_ip)
            elif i.equipment_type == '录像机':
                rtsp = get_children_rtsp(i.parent_id, i.code, 1)
            elif i.equipment_type == '特殊摄像头':
                rtsp = get_children_rtsp(i.parent_id, i.code, 2)
            elif i.equipment_type == '浙江双视热成像':
                rtsp = 'rtsp://{}:{}@{}:554/live/chn0'.format(i.equipment_uname, i.equipment_password, i.equipment_ip)

            dict_res = {'id': i.id, 'equipment_name': i.equipment_name, 'equipment_type': i.equipment_type,
                        'rtsp': rtsp}

            equipment_list.append(dict_res)

        # print(equipment_list)



        # 使用列表推导式筛选设备类型为“录像机”的记录 取录像机的 ID
        vcr_ids = [i['id'] for i in equipment_list if i['equipment_type'] == '录像机' or i['equipment_type'] == '特殊摄像头']
        # 调用方法数据构造
        equipment_list = children_data(equipment_list, vcr_ids)

        # print(equipment_list)

        return jsonify({'code': 200, 'msg': '筛选数据',

                        'mine_list': mine_list,
                        'mine_list_name': '矿数据返回列表',
                        'equipment_list': equipment_list,
                        'equipment_list_name': '监控点数据返回列表',
                        'algorithm_list': algorithm_list,
                        'algorithm_list_name': '算法数据返回列表',
                        'algorithm_conf_list': algorithm_conf,
                        'algorithm_conf_list_name': '算法配置返回列表',
                        'type_list': configs.type_status,
                        'type_list_name': '预警数据返回列表',
                        'equipment_type': configs.equipment_type,
                        'equipment_type_name': '设备类型数据返回列表',
                        'manufacturer_type': configs.manufacturer_type,
                        'manufacturer_type_name': '厂商类型数据返回列表',
                        'equipment_codetype': configs.equipment_codetype,
                        'equipment_codetype_name': '码流类型数据返回列表',
                        'vcr_way': configs.vcr_way,
                        'vcr_name': '接入方式数据返回列表',
                        'dict_data': dict_data,
                        'dict_data_name': '字典数据列表',
                        'diagnosis_type_result': diagnosis_type_result,
                        'diagnosis_type_result_name': '诊断类型列表返回',
                        })




# 选取监控点图片返回接口
@model_view.route('/image_show', methods=['GET'])
def image_show():

    equipment_id = request.args.get('equipment_id',None)
    type = request.args.get('type') if  request.args.get('type') else 0
    # 获取指定的分辨率值 img_resolution
    img_resolution = request.args.get('img_resolution')

    equipment_data = db.session.query(Equipment.id,Equipment.equipment_uname,Equipment.equipment_password,Equipment.equipment_ip,Equipment.equipment_type,
                                      Equipment.parent_id,Equipment.code
                                      ).filter(Equipment.id==equipment_id).first()


    if equipment_data:
        rtsp = ''
        # 判断摄像头类型获取rtsp流
        if equipment_data.equipment_type == '摄像头':
            rtsp = 'rtsp://{}:{}@{}'.format(equipment_data.equipment_uname, equipment_data.equipment_password, equipment_data.equipment_ip)
        elif equipment_data.equipment_type == '录像机':
            rtsp = get_children_rtsp(equipment_data.parent_id, equipment_data.code, 1)
        elif equipment_data.equipment_type == '特殊摄像头':
            rtsp = get_children_rtsp(equipment_data.parent_id, equipment_data.code, 2)
        elif equipment_data.equipment_type == '浙江双视热成像':
            rtsp = 'rtsp://{}:{}@{}:554/live/chn0'.format(equipment_data.equipment_uname, equipment_data.equipment_password, equipment_data.equipment_ip)

        result = get_img_from_camera_net(rtsp,equipment_data.id,int(type),img_resolution)
        return jsonify(result)
    else:
        return jsonify({'code':400,'msg':'请传递参数'})




# 算法上传接口
@model_view.route('/algorithm_upload', methods=['POST'])
def algorithm_upload():


    # 盒子服务器上传类实例化
    SSH = SSH_Func()

    # 接收压缩文件
    # uploaded_file = request.files.get('files')   # 上传文件
    # algorithm_name = request.json.get('algorithm_name', None)  # 算法名称
    # algorithm_type = request.json.get('algorithm_type', None)  # 算法类型 1 通用检测模型,2 单类检测模型
    # algorithm_type_list = request.json.get('algorithm_type_list', None)  # 算法检测类型列表
    # algorithm_status = request.json.get('algorithm_status', None)  # 算法运行状态 1运行 2停止

    uploaded_file = request.files.get('files')   # 上传文件
    algorithm_name = request.form.get('algorithm_name', None)  # 算法名称
    algorithm_type = request.form.get('algorithm_type', None)  # 算法类型 1 通用检测模型,2 单类检测模型
    algorithm_type_list = request.form.get('algorithm_type_list', None)  # 算法检测类型列表
    algorithm_status = request.form.get('algorithm_status', None)  # 算法运行状态 1运行 2停止
    algorithm_version = request.form.get('algorithm_version', None)  # 算法版本
    algorithm_trade_type = request.form.get('algorithm_trade_type', None)  # 算法厂商 1.寒武纪 2. 算能  3. 华为
    algorithm_ps = request.form.get('algorithm_ps', None)  # 算法备注


    if uploaded_file:
        # file_name为上传文件名字
        file_name = uploaded_file.filename

        # 查找算法名称数据相同信息
        name_repeat = db.session.query(Algorithm_library).filter(Algorithm_library.algorithm_file_name==str(file_name)).first()


        if name_repeat:
            return jsonify({'code': 400, 'msg': '该算法名称已存在'})

        SSH.Add_Folder()
        res = SSH.upload_send_file(uploaded_file)



        config_data = Algorithm_library(
            algorithm_file_name=file_name if file_name else None,
            algorithm_name=algorithm_name  if algorithm_name else None,
            algorithm_type=algorithm_type if algorithm_type else None,
            algorithm_type_list=algorithm_type_list if eval(algorithm_type_list) else None,
            algorithm_status=algorithm_status if algorithm_status else None,
            algorithm_version=algorithm_version if algorithm_version else None,
            algorithm_path=res if res else None,
            algorithm_trade_type = algorithm_trade_type if algorithm_trade_type else None,
            algorithm_ps = algorithm_ps if algorithm_ps else None
        )
        db.session.add(config_data)
        db.session.commit()


        # 当算法上传成功， 将算法id以及算法，算法检测列表写入 检测类型表
        for i in eval(config_data.algorithm_type_list):
            algorithm_test_type_res = Algorithm_test_type(test_type_ename=i,Algorithm_library_id=config_data.id)
            db.session.add(algorithm_test_type_res)
        db.session.commit()

        # db.session.add(config_data)


        result = {'code': 200, 'msg': '算法添加完成'}
    else:
        result = {'code': 400, 'msg': '请导入算法上传包'}


    # algorithm_file_name =  request.form.get('algorithm_file_name', None) # '文件名称'
    # algorithm_name =  request.form.get('algorithm_name', None)  # '算法名称'
    # algorithm_type =  request.form.get('algorithm_type', None)  # '算法类型'
    # algorithm_version =  request.form.get('algorithm_version', None) # 算法版本'
    #
    #
    #
    # # 参数构建判断是否为空
    # params = [algorithm_name]
    #
    # if not all(params):
    #     return jsonify({'code': 400, 'msg': '算法名称未填写'})
    #
    # # 查找算法名称数据相同信息
    # name_repeat = db.session.query(Algorithm_library).filter(Algorithm_library.algorithm_name==algorithm_name).first()
    # if name_repeat:
    #     return jsonify({'code': 400, 'msg': '该算法名称已存在'})
    #
    #
    # # 数据添加
    # config_data = Algorithm_library(
    #     algorithm_file_name=algorithm_file_name if algorithm_file_name else None,
    #     algorithm_name=algorithm_name  if algorithm_name else None,
    #     algorithm_type=algorithm_type if algorithm_type else None,
    #     algorithm_version=algorithm_version if algorithm_version else None,
    # )
    # db.session.add(config_data)
    # db.session.commit()

    return jsonify(result)




# 算法管理配置添加接口
@model_view.route('/algorithm_add', methods=['POST'])
def algorithm_add():

    # 获取所传参数
    conf_name = request.json.get('conf_name', None)  # 名称
    Algorithm_library_id = request.json.get('Algorithm_library_id', None)  # 算法
    Mine_id = request.json.get('Mine_id', None)  # 分析矿名称id
    Equipment_id = request.json.get('Equipment_id', None)  # 分析矿监控点id
    conf_area = request.json.get('conf_area', None)  # 分析区域
    status = request.json.get('status', None)  # 算法配置运行状态
    test_type_id = request.json.get('test_type_id', None)  # 算法检测类型
    shield_status = request.json.get('shield_status', None)  # 算法遮挡类型
    tem_conf_area = request.json.get('tem_conf_area', None)  # 热成像检测消除区域
    tem_frames = request.json.get('tem_frames', None)  # 温度阈值
    confidence = request.json.get('confidence', None)  # 置信度阈值
    draw_type = request.json.get('draw_type', None)  # 绘制状态  1矩形 2线条
    interval_time = request.json.get('interval_time', 0)  # 报警间隔时间
    img_resolution = request.json.get('img_resolution', None)  # 图片分辨率
    duration_time = request.json.get('duration_time', 0)  # 持续时间
    image_draw_type = request.json.get('image_draw_type', 1)  # 图片结果矩形框   1. 绘制   2.不绘制
    Algorithm_config_ps = request.json.get('Algorithm_config_ps', None)  # 算法配置备注



    # 参数构建判断是否为空
    params = [conf_name, Algorithm_library_id, Mine_id, Equipment_id,conf_area,test_type_id]

    if not all(params):
        return jsonify({'code': 400, 'msg': '算法配置数据有未填写项'})

    # 数据添加
    config_data = Algorithm_config(
        conf_name=conf_name if conf_name else None,
        Algorithm_library_id=int(Algorithm_library_id) if Algorithm_library_id else None,
        Mine_id=int(Mine_id) if Mine_id else None,
        Equipment_id=int(Equipment_id) if Equipment_id else None,
        conf_area=str(conf_area) if conf_area else None,
        status=status if status else '1',
        Algorithm_test_type_id = test_type_id if test_type_id else None,
        shield_status = shield_status,
        tem_conf_area = str(tem_conf_area) if tem_conf_area else str([]),
        tem_frames = tem_frames if tem_frames else None,
        draw_type = draw_type,
        confidence = confidence if confidence else '0.2',
        interval_time = interval_time if interval_time else 0,
        conf_img_resolution=img_resolution,
        duration_time=duration_time if duration_time else 0,
        image_draw_type=image_draw_type if image_draw_type else 1,
        Algorithm_config_ps=Algorithm_config_ps if Algorithm_config_ps else None,
    )
    db.session.add(config_data)
    db.session.commit()


    # 历史表数据增加
    history_data = Algorithm_config_history(
        conf_name=conf_name if conf_name else None,
        Algorithm_library_id=int(Algorithm_library_id) if Algorithm_library_id else None,
        Mine_id=int(Mine_id) if Mine_id else None,
        Equipment_id=int(Equipment_id) if Equipment_id else None,
        conf_area=str(conf_area) if conf_area else None,
        status=status if status else '1',
        Algorithm_test_type_id=test_type_id if test_type_id else None,
        shield_status=shield_status,
        tem_conf_area=str(tem_conf_area) if tem_conf_area else str([]),
        tem_frames=tem_frames if tem_frames else None,
        draw_type=draw_type,
        confidence=confidence if confidence else '0.2',
        interval_time=interval_time if interval_time else 0,
        conf_img_resolution=img_resolution,
        duration_time=duration_time if duration_time else 0,
        image_draw_type=image_draw_type if image_draw_type else 1,
        Algorithm_config_ps=Algorithm_config_ps if Algorithm_config_ps else None,
        operation_type="add",
        config_id = config_data.id
    )
    db.session.add(history_data)
    db.session.commit()


    # redis队列 当算法配置添加完成时，数据写入队列，寒武纪盒子redis监听到数据重新执行
    queue_redis = TestQueue()
    queue_redis.push()

    return jsonify({'code': 200, 'msg': '算法配置数据添加完成'})



# 算法管理配置修改接口
@model_view.route('/algorithm_update', methods=['POST'])
def algorithm_update():
    # 获取所传参数
    id = request.form.get('id', None)  # id
    conf_name = request.form.get('conf_name', None)  # 名称
    Algorithm_library_id = request.form.get('Algorithm_library_id', None)  # 算法
    Mine_id = request.form.get('Mine_id', None)  # 分析矿名称id
    Equipment_id = request.form.get('Equipment_id', None)  # 分析矿监控点id
    conf_area = request.form.get('conf_area', None)  # 分析区域
    test_type_id = request.form.get('test_type_id', None)  # 算法检测类型
    shield_status = request.form.get('shield_status', None)  # 算法遮挡类型
    tem_conf_area = request.form.get('tem_conf_area', None)  # 热成像检测消除区域
    tem_frames = request.form.get('tem_frames', None)  # 温度阈值
    confidence = request.form.get('confidence', None)  # 置信度阈值
    draw_type = request.form.get('draw_type', None)  # 绘制状态  1矩形 2线条
    interval_time = request.form.get('interval_time', 0)  # 报警间隔时间
    img_resolution = request.form.get('img_resolution', None)  # 算法配置的图片分辨率
    duration_time = request.form.get('duration_time', 0)  # 持续时间
    image_draw_type = request.form.get('image_draw_type', 1)  # 图片结果矩形框   1. 绘制   2.不绘制
    Algorithm_config_ps = request.form.get('Algorithm_config_ps', None)  # 算法配置备注



    print(id,conf_name,Algorithm_library_id,Mine_id,Equipment_id,conf_area,'修改参数')
    # 参数构建判断是否为空
    params = [id,conf_name,Algorithm_library_id, Mine_id, Equipment_id,conf_area,test_type_id]

    if not all(params):
        return jsonify({'code': 400, 'msg': '算法配置数据有未填写项'})


    # 查询配置id 修改配置id信息
    conf_id = db.session.query(Algorithm_config).filter(Algorithm_config.id == id).first()
    print(conf_id)
    if conf_id:
        # 修改配置信息的代码
        conf_id.conf_name = conf_name
        conf_id.Algorithm_library_id = Algorithm_library_id
        conf_id.Mine_id = Mine_id
        conf_id.Equipment_id = Equipment_id
        conf_id.conf_area = str(conf_area)
        conf_id.Algorithm_test_type_id = test_type_id
        conf_id.shield_status = shield_status
        conf_id.tem_conf_area = str(tem_conf_area) if tem_conf_area else None
        conf_id.tem_frames = tem_frames if tem_frames else None
        conf_id.draw_type = draw_type
        conf_id.confidence = confidence
        conf_id.interval_time = interval_time if tem_frames else 0
        conf_id.conf_img_resolution = img_resolution
        conf_id.duration_time = duration_time if duration_time else 0
        conf_id.image_draw_type = image_draw_type if image_draw_type else 1
        conf_id.Algorithm_config_ps = Algorithm_config_ps if Algorithm_config_ps else None

        # 提交会话以保存更改
        db.session.commit()

        # 添加历史记录
        history_data = Algorithm_config_history(
            conf_name=conf_id.conf_name if conf_id.conf_name else None,
            Algorithm_library_id=int(conf_id.Algorithm_library_id) if conf_id.Algorithm_library_id else None,
            Mine_id=int(conf_id.Mine_id) if conf_id.Mine_id else None,
            Equipment_id=int(conf_id.Equipment_id) if conf_id.Equipment_id else None,
            conf_area=str(conf_id.conf_area) if conf_id.conf_area else None,
            status=conf_id.status if conf_id.status else '1',
            Algorithm_test_type_id=conf_id.Algorithm_test_type_id if conf_id.Algorithm_test_type_id else None,
            shield_status=conf_id.shield_status,
            tem_conf_area=str(conf_id.tem_conf_area) if conf_id.tem_conf_area else str([]),
            tem_frames=conf_id.tem_frames if conf_id.tem_frames else None,
            draw_type=conf_id.draw_type,
            confidence=conf_id.confidence if conf_id.confidence else '0.2',
            interval_time=conf_id.interval_time if conf_id.interval_time else 0,
            conf_img_resolution=conf_id.conf_img_resolution,
            duration_time=conf_id.duration_time if conf_id.duration_time else 0,
            image_draw_type=conf_id.image_draw_type if conf_id.image_draw_type else 1,
            conf_time=conf_id.conf_time,
            Algorithm_config_ps=conf_id.Algorithm_config_ps if conf_id.Algorithm_config_ps else None,
            operation_type="update",
            config_id=conf_id.id
        )
        db.session.add(history_data)
        db.session.commit()

    # redis队列 当算法配置修改完成时，数据写入队列，寒武纪盒子redis监听到数据重新执行
    queue_redis = TestQueue()
    queue_redis.push()

    return jsonify({'code': 200, 'msg': '算法配置数据修改完成'})


#算法模型运行状态接口
@model_view.route('/algorithm_status',methods=['GET'])
def algorithm_status():
    equipment_algorithm_list = db.session.query(Algorithm_config.Equipment_id, Algorithm_config.status,
                                                Equipment.equipment_ip, Equipment.online,
                                                Algorithm_config.algorithm_status, Algorithm_config.id).join(Equipment,
                                                                                                             Algorithm_config.Equipment_id == Equipment.id).all()
    equipment_algorithm_dict_list = convert_folder_to_dict_list(equipment_algorithm_list,
                                                                ['Equipment_id', 'status', 'equipment_ip', 'online',
                                                                 'algorithm_status', 'id'])
    print(equipment_algorithm_list)
    for dict_list_itme in equipment_algorithm_dict_list:
        algorithmConfig = db.session.query(Algorithm_config).filter(Algorithm_config.id == dict_list_itme['id']).first()
        if dict_list_itme['status'] == '1' and dict_list_itme['online'] == 1:
            algorithmConfig.algorithm_status = 1
            dict_list_itme['algorithm_status'] = 1
        else:
            algorithmConfig.algorithm_status = 2
            dict_list_itme['algorithm_status'] = 2
        db.session.commit()
    print(equipment_algorithm_dict_list)
    return equipment_algorithm_dict_list


# 算法配置数据返回接口--与单一详情
@model_view.route('/algorithm_data_show', methods=['GET'])
def algorithm_data_show():

    # redis 取图片
    r = Redis(Redis_ip, Redis_port, 'list')

    # 当存在conf_id 查单一详情
    conf_id = request.args.get('conf_id')
    if conf_id:
        algorithm_res = db.session.query(
            Algorithm_config.id,
            Algorithm_config.status,
            Algorithm_library.id.label('Algorithm_library_id'),
            Algorithm_library.algorithm_name,
            Mine.id.label('Mine_id'),
            Mine.mine_name,
            Equipment.id.label('Equipment_id'),
            Equipment.equipment_name,
            Equipment.equipment_type,
            Equipment.code,
            Algorithm_config.conf_name,
            Algorithm_config.conf_object,
            Algorithm_config.conf_time,
            Algorithm_config.conf_area,
            Algorithm_config.Algorithm_test_type_id.label('test_type_id'),
            Algorithm_config.shield_status,
            Algorithm_config.tem_conf_area,
            Algorithm_config.tem_frames,
            Algorithm_config.draw_type,
            Algorithm_config.confidence,
            Algorithm_config.interval_time,
            Algorithm_config.conf_img_resolution,
            Algorithm_config.duration_time,
            Algorithm_config.image_draw_type,
            Algorithm_config.update_time,
            Algorithm_config.Algorithm_config_ps

        ).join(
            Algorithm_config,
            Algorithm_library.id == Algorithm_config.Algorithm_library_id
        ).join(
            Mine,
            Algorithm_config.Mine_id == Mine.id
        ).join(
            Equipment,
            Algorithm_config.Equipment_id == Equipment.id
        ).order_by(Algorithm_config.conf_time.desc()).filter(Algorithm_config.id == conf_id).first()

        if algorithm_res:


            # # 查询对应算法数据
            # data = db.session.query(Algorithm_test_type.id, Algorithm_test_type.test_type_ename,
            #                                   Algorithm_test_type.Algorithm_library_id).filter(
            #     Algorithm_test_type.Algorithm_library_id == algorithm_res.Algorithm_library_id).all()
            # data = convert_folder_to_dict_list(data,
            #                                              ['id', 'test_type_ename', 'Algorithm_library_id', ])

            algorithm_data = {
                'id':algorithm_res.id,
                'image':'/static/'+str(os.path.basename(r.get_string('em_{}'.format(algorithm_res.Equipment_id)))) if algorithm_res.Equipment_id else '',
                'Algorithm_library_id': algorithm_res.Algorithm_library_id,
                'algorithm_name': algorithm_res.algorithm_name,
                'Mine_id': algorithm_res.Mine_id,
                'mine_name': algorithm_res.mine_name,
                'Equipment_id': algorithm_res.Equipment_id,
                'equipment_name': algorithm_res.equipment_name,
                'equipment_type': algorithm_res.equipment_type,
                'equipment_code': algorithm_res.code,
                'conf_name': algorithm_res.conf_name if algorithm_res.conf_name else '',
                'conf_object': algorithm_res.conf_object if algorithm_res.conf_object else '',
                'conf_time': (algorithm_res.conf_time).strftime("%Y-%m-%d %H:%M:%S"),
                'conf_area': algorithm_res.conf_area if algorithm_res.conf_area else '',
                'test_type_id': algorithm_res.test_type_id if algorithm_res.test_type_id else '',
                'status': configs.status[int(algorithm_res.status)-1]['value'],
                'shield_status': algorithm_res.shield_status,
                'tem_conf_area': algorithm_res.tem_conf_area,
                'tem_frames': algorithm_res.tem_frames,
                'draw_type': algorithm_res.draw_type,
                'confidence': algorithm_res.confidence,
                'interval_time': algorithm_res.interval_time,
                'img_resolution': algorithm_res.conf_img_resolution,
                'duration_time': algorithm_res.duration_time,
                'image_draw_type': algorithm_res.image_draw_type,
                'update_time': (algorithm_res.update_time).strftime("%Y-%m-%d %H:%M:%S") if algorithm_res.update_time else '',
                'Algorithm_config_ps': algorithm_res.Algorithm_config_ps if algorithm_res.Algorithm_config_ps else '',
                # 'data': data,
            }

            return jsonify({'code': 200, 'datalist': algorithm_data,'msg':'查询成功'})
        else:
            return jsonify({'code': 400, 'datalist': [],'msg':'未有该配置的详情信息'})
    else:

        # 算法名称
        algorithm_name = request.args.get('algorithm_name')
        # 开始时间
        start_time = request.args.get('start_time')
        # 结束时间
        end_time = request.args.get('end_time')

        #算法名称
        conf_name = request.args.get('conf_name')

        # 第几页
        page = request.args.get('page', default=1, type=int)
        # 每页条数
        per_page = request.args.get('per_page', default=15, type=int)


        # 假设前端传递的参数为可能有一个或多个
        filters = []

        # 如果存在算法名称，进行模糊查询
        if conf_name:
            filters.append(Algorithm_config.conf_name.ilike(f"%{conf_name}%"))

        # 如果存在算法参数，将其加入过滤条件
        if algorithm_name:
            filters.append(Algorithm_library.algorithm_name == algorithm_name)

        # 如果存在开始时间和结束时间参数，加入过滤条件
        if start_time and end_time:
            # 查询在开始时间跟结束时间之内
            filters.append(Algorithm_config.conf_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))

        # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and

        if len(filters) >= 2:
            query_filter = and_(*filters)
        else:
            query_filter = filters[0] if filters else None

        # 矿，监控点，算法，算法配置 表联查
        # 联查总数据

        if query_filter is not None:

            algorithm_res = db.session.query(
                Algorithm_config.id,
                Algorithm_config.status,
                Algorithm_library.id.label('Algorithm_library_id'),
                Algorithm_library.algorithm_name,
                Mine.id.label('Mine_id'),
                Mine.mine_name,
                Equipment.id.label('Equipment_id'),
                Equipment.equipment_name,
                Equipment.equipment_type,
                Equipment.code,
                Algorithm_config.conf_name,
                Algorithm_config.conf_object,
                Algorithm_config.conf_time,
                Algorithm_config.conf_area,
                Algorithm_config.shield_status,
                Algorithm_config.tem_conf_area,
                Algorithm_config.tem_frames,
                Algorithm_config.draw_type,
                Algorithm_config.confidence,
                Algorithm_config.interval_time,
                Algorithm_config.conf_img_resolution,
                Algorithm_config.duration_time,
                Algorithm_config.image_draw_type,
                Algorithm_config.update_time,
                Algorithm_config.Algorithm_config_ps
            ).join(
                Algorithm_config,
                Algorithm_library.id == Algorithm_config.Algorithm_library_id
            ).join(
                Mine,
                Algorithm_config.Mine_id == Mine.id
            ).join(
                Equipment,
                Algorithm_config.Equipment_id == Equipment.id
            ).order_by(Algorithm_config.conf_time.desc()).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
        else:
            algorithm_res = db.session.query(
                Algorithm_config.id,
                Algorithm_config.status,
                Algorithm_library.id.label('Algorithm_library_id'),
                Algorithm_library.algorithm_name,
                Mine.id.label('Mine_id'),
                Mine.mine_name,
                Equipment.id.label('Equipment_id'),
                Equipment.equipment_name,
                Equipment.equipment_type,
                Equipment.code,
                Algorithm_config.conf_name,
                Algorithm_config.conf_object,
                Algorithm_config.conf_time,
                Algorithm_config.conf_area,
                Algorithm_config.shield_status,
                Algorithm_config.tem_conf_area,
                Algorithm_config.tem_frames,
                Algorithm_config.draw_type,
                Algorithm_config.confidence,
                Algorithm_config.interval_time,
                Algorithm_config.conf_img_resolution,
                Algorithm_config.duration_time,
                Algorithm_config.image_draw_type,
                Algorithm_config.update_time,
                Algorithm_config.Algorithm_config_ps
            ).join(
                Algorithm_config,
                Algorithm_library.id == Algorithm_config.Algorithm_library_id
            ).join(
                Mine,
                Algorithm_config.Mine_id == Mine.id
            ).join(
                Equipment,
                Algorithm_config.Equipment_id == Equipment.id
            ).order_by(Algorithm_config.conf_time.desc()).paginate(page=page, per_page=per_page, error_out=False)



        # 连表查询获取模型应用数据列表
        algorithm_data = [{
            'id':i.id,
            'image':'/static/' +str(os.path.basename(r.get_string('em_{}'.format(i.Equipment_id)))) if i.Equipment_id else '',
            'Algorithm_library_id': i.Algorithm_library_id,
            'algorithm_name': i.algorithm_name,
            'Mine_id': i.Mine_id,
            'mine_name': i.mine_name,
            'Equipment_id': i.Equipment_id,
            'equipment_name': i.equipment_name,
            'equipment_type': i.equipment_type,
            'equipment_code': i.code,
            'conf_name': i.conf_name if i.conf_name else '',
            'conf_object': i.conf_object if i.conf_object else '',
            'conf_time': (i.conf_time).strftime("%Y-%m-%d %H:%M:%S"),
            'conf_area': i.conf_area if i.conf_area else '',
            'status': configs.status[int(i.status)-1]['value'],
            'shield_status,': i.shield_status,
            'tem_conf_area': i.tem_conf_area,
            'tem_frames': i.tem_frames,
            'draw_type': i.draw_type,
            'confidence': i.confidence,
            'interval_time': i.interval_time,
            'img_resolution': i.conf_img_resolution,
            'duration_time': i.duration_time,
            'image_draw_type': i.image_draw_type,
            'update_time': (i.update_time).strftime("%Y-%m-%d %H:%M:%S") if i.update_time else '',
            'Algorithm_config_ps': i.Algorithm_config_ps if i.Algorithm_config_ps else '',
        } for i in algorithm_res.items]


        # 构建返回的 JSON
        response_data = {
            'total_items': algorithm_res.total,
            'total_pages': algorithm_res.pages,
            'current_page': algorithm_res.page,
            'per_page': per_page,
            'data': algorithm_data,
        }


        return jsonify({'code':200,'msg':'查询成功','data_list':response_data})




# 算法配置数据删除接口
@model_view.route('/algorithm_data_delete', methods=['POST'])
def algorithm_data_delete():
    # 配置id
    id = request.json.get('id', None)
    id = [i['id'] for i in id]
    if id:

        # 添加历史记录
        for item in id:
            conf_id = db.session.query(Algorithm_config).filter(Algorithm_config.id == item).first()
            history_data = Algorithm_config_history(
                conf_name=conf_id.conf_name if conf_id.conf_name else None,
                Algorithm_library_id=int(conf_id.Algorithm_library_id) if conf_id.Algorithm_library_id else None,
                Mine_id=int(conf_id.Mine_id) if conf_id.Mine_id else None,
                Equipment_id=int(conf_id.Equipment_id) if conf_id.Equipment_id else None,
                conf_area=str(conf_id.conf_area) if conf_id.conf_area else None,
                status=conf_id.status if conf_id.status else '1',
                Algorithm_test_type_id=conf_id.Algorithm_test_type_id if conf_id.Algorithm_test_type_id else None,
                shield_status=conf_id.shield_status,
                tem_conf_area=str(conf_id.tem_conf_area) if conf_id.tem_conf_area else str([]),
                tem_frames=conf_id.tem_frames if conf_id.tem_frames else None,
                draw_type=conf_id.draw_type,
                confidence=conf_id.confidence if conf_id.confidence else '0.2',
                interval_time=conf_id.interval_time if conf_id.interval_time else 0,
                conf_img_resolution=conf_id.conf_img_resolution,
                duration_time=conf_id.duration_time if conf_id.duration_time else 0,
                image_draw_type=conf_id.image_draw_type if conf_id.image_draw_type else 1,
                conf_time=conf_id.conf_time,
                Algorithm_config_ps=conf_id.Algorithm_config_ps if conf_id.Algorithm_config_ps else None,
                operation_type="delete",
                config_id = conf_id.id

            )
            db.session.add(history_data)
            db.session.commit()

        # 删除到算法配置删除记录
        db.session.query(Algorithm_config).filter(Algorithm_config.id.in_(id)).delete()

        # 删除对应算法结果对应配置id记录
        db.session.query(Algorithm_result).filter(Algorithm_result.Algorithm_config_id.in_(id)).delete()

        db.session.commit()


        # 获取算法配置要跑进程数据的条数，按条数写入队列来进行重启
        queue_redis = TestQueue()
        queue_redis.push()
        return jsonify({'code': 200, 'msg': '删除成功'})
    else:
        return jsonify({'code': 400, 'msg': '缺少设备id参数'})



from sqlalchemy import desc, func

# 算法预警--------sqlalchemy--------分页结果展示接口
@model_view.route('/algorithm_result_sqlalchemy', methods=['GET'])
def algorithm_result_sqlalchemy():

    # id 单一取值
    id = request.args.get('id', None)

    # 矿id
    mine_id = request.args.get('mine_id', None)
    # 监控点id
    equipment_id = request.args.get('equipment_id', None)

    # 开始时间
    start_time = request.args.get('start_time')
    # 结束时间
    end_time = request.args.get('end_time')

    # 报警类型
    type_sta = request.args.get('type', None)

    # 算法id
    algorithm_id = request.args.get('algorithm_id', None)


    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=15, type=int)


    # 假设前端传递的参数为可能有一个或多个
    filters = []

    # 如果存在算法名称参数，将其加入过滤条件
    if mine_id:
        filters.append(Algorithm_config.Mine_id == mine_id)

    if equipment_id:

        # 判断 如果是父类 取父类下边数据
        parent_id = db.session.query(Equipment).filter(Equipment.id == equipment_id).first()
        # 查找父类下边是否有 子类数据
        children = db.session.query(Equipment).filter(Equipment.parent_id == parent_id.id).first()

        # 如果没有子类数据取摄像头
        if not children:
            filters.append(Equipment.id == equipment_id)

        # 如果有子类数据取录像机下边子类数据
        else:
            filters.append(Equipment.parent_id == equipment_id)

    # 如果存在开始时间和结束时间参数，加入过滤条件
    if start_time and end_time:

        # 使用 and_ 函数将两个条件组合起来
        filters.append(Algorithm_result.res_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))

    if type_sta:
        filters.append(Algorithm_result.res_type == type_sta)


    if algorithm_id:
        filters.append(Algorithm_library.id == algorithm_id)


    # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and

    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None


    if query_filter is not None:

        algorithm_info = db.session.query(
                Algorithm_result.id.label('Algorithm_result_id'),
                Algorithm_result.res_time,
                Mine.id.label('Mine_id'),
                Mine.mine_name,
                Equipment.id.label('Equipment_id'),
                Equipment.equipment_name,
                Algorithm_config.id.label('Algorithm_config_id'),
                Algorithm_config.conf_name,
                Algorithm_config.conf_img_resolution,
                Algorithm_result.res_type,
                Algorithm_result.res_image,
                Algorithm_result.res_video,
                Algorithm_result.res_frame_skip,
                Algorithm_library.algorithm_name,
            ).join(
                Algorithm_config,
                Algorithm_config.id==Algorithm_result.Algorithm_config_id
            ).join(
                Mine,
                Algorithm_config.Mine_id==Mine.id
            ).join(
                Equipment,
                Algorithm_config.Equipment_id==Equipment.id
            ).join(
                Algorithm_library,
                Algorithm_config.Algorithm_library_id == Algorithm_library.id
            ).filter(query_filter).order_by(Algorithm_result.res_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    else:
        algorithm_info = db.session.query(
                Algorithm_result.id.label('Algorithm_result_id'),
                Algorithm_result.res_time,
                Mine.id.label('Mine_id'),
                Mine.mine_name,
                Equipment.id.label('Equipment_id'),
                Equipment.equipment_name,
                Algorithm_config.id.label('Algorithm_config_id'),
                Algorithm_config.conf_name,
                Algorithm_config.conf_img_resolution,
                Algorithm_result.res_type,
                Algorithm_result.res_image,
                Algorithm_result.res_video,
                Algorithm_result.res_frame_skip,
                Algorithm_library.algorithm_name,
            ).join(
                Algorithm_config,
                Algorithm_config.id==Algorithm_result.Algorithm_config_id
            ).join(
                Mine,
                Algorithm_config.Mine_id==Mine.id
            ).join(
                Equipment,
                Algorithm_config.Equipment_id==Equipment.id
            ).join(
                Algorithm_library,
                Algorithm_config.Algorithm_library_id == Algorithm_library.id
            ).order_by(Algorithm_result.res_time.desc()).paginate(page=page, per_page=per_page, error_out=False)

    if id:
        algorithm_info = db.session.query(
            Algorithm_result.id.label('Algorithm_result_id'),
            Algorithm_result.res_time,
            Mine.id.label('Mine_id'),
            Mine.mine_name,
            Equipment.id.label('Equipment_id'),
            Equipment.equipment_name,
            Algorithm_config.id.label('Algorithm_config_id'),
            Algorithm_config.conf_name,
            Algorithm_config.conf_img_resolution,
            Algorithm_result.res_type,
            Algorithm_result.res_image,
            Algorithm_result.res_video,
            Algorithm_result.res_frame_skip,
            Algorithm_library.algorithm_name,
        ).join(
            Algorithm_config,
            Algorithm_config.id == Algorithm_result.Algorithm_config_id
        ).join(
            Mine,
            Algorithm_config.Mine_id == Mine.id
        ).join(
            Equipment,
            Algorithm_config.Equipment_id == Equipment.id
        ).join(
            Algorithm_library,
            Algorithm_config.Algorithm_library_id == Algorithm_library.id
        ).filter(Algorithm_result.id == id).order_by(Algorithm_result.res_time.desc()).paginate(page=page,
                                                                                                per_page=per_page,
                                                                                                error_out=False)

    # 连表查询获取模型应用数据列表
    algorithm_data = [{
        'Algorithm_result_id': i.Algorithm_result_id,
        'res_time': (i.res_time).strftime("%Y-%m-%d %H:%M:%S"),
        'Mine_id': i.Mine_id,
        'mine_name': i.mine_name,
        'Equipment_id': i.Equipment_id,
        'equipment_name': i.equipment_name,
        'conf_id':i.Algorithm_config_id,
        'conf_name':i.conf_name,
        'res_type': configs.type_status[int(i.res_type)-1]['value'],
        'res_image': i.res_image,
        'res_video': i.res_video,
        'res_frame_skip': i.res_frame_skip,
        'algorithm_name': i.algorithm_name,
        'img_resolution': i.conf_img_resolution,
    } for i in algorithm_info.items]


    response_data = {
        'total_items': algorithm_info.total,
        'total_pages': algorithm_info.pages,
        'current_page': algorithm_info.page,
        'per_page': per_page,
        'data':  algorithm_data,
    }

    return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})


# # 算法预警--------sql自写分页--------结果展示接口
# @model_view.route('/algorithm_result', methods=['GET'])
# def algorithm_result():
#
#
#     # id 单一取值
#     id = request.args.get('id', None)
#
#     # 矿id
#     mine_id = request.args.get('mine_id', None)
#     # 监控点id
#     equipment_id = request.args.get('equipment_id', None)
#
#     # 开始时间
#     start_time = request.args.get('start_time')
#     # 结束时间
#     end_time = request.args.get('end_time')
#
#     # 报警类型
#     type_sta = request.args.get('type', None)
#
#     # 算法id
#     algorithm_id = request.args.get('algorithm_id', None)
#
#
#     # 第几页
#     page = request.args.get('page', default=1, type=int)
#     # 每页条数
#     per_page = request.args.get('per_page', default=15, type=int)
#
#
#     # 假设前端传递的参数为可能有一个或多个
#     filters = []
#
#     # 如果存在算法名称参数，将其加入过滤条件
#     if mine_id:
#         filters.append(Algorithm_config.Mine_id == mine_id)
#
#     if equipment_id:
#
#         # 判断 如果是父类 取父类下边数据
#         parent_id = db.session.query(Equipment).filter(Equipment.id == equipment_id).first()
#         # 查找父类下边是否有 子类数据
#         children = db.session.query(Equipment).filter(Equipment.parent_id == parent_id.id).first()
#
#         # 如果没有子类数据取摄像头
#         if not children:
#             filters.append(Equipment.id == equipment_id)
#
#         # 如果有子类数据取录像机下边子类数据
#         else:
#             filters.append(Equipment.parent_id == equipment_id)
#
#     # 如果存在开始时间和结束时间参数，加入过滤条件
#     if start_time and end_time:
#
#         # 使用 and_ 函数将两个条件组合起来
#         filters.append(Algorithm_result.res_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))
#
#     if type_sta:
#         filters.append(Algorithm_result.res_type == type_sta)
#
#
#     if algorithm_id:
#         filters.append(Algorithm_library.id == algorithm_id)
#
#
#     # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and
#
#     if len(filters) >= 2:
#         query_filter = and_(*filters)
#     else:
#         query_filter = filters[0] if filters else None
#
#
#     if query_filter is not None:
#
#         algorithm_info = db.session.query(
#                 Algorithm_result.id.label('Algorithm_result_id'),
#                 Algorithm_result.res_time,
#                 Mine.id.label('Mine_id'),
#                 Mine.mine_name,
#                 Equipment.id.label('Equipment_id'),
#                 Equipment.equipment_name,
#                 Algorithm_config.id.label('Algorithm_config_id'),
#                 Algorithm_config.conf_name,
#                 Algorithm_config.conf_img_resolution,
#                 Algorithm_result.res_type,
#                 Algorithm_result.res_image,
#                 Algorithm_result.res_video,
#                 Algorithm_result.res_frame_skip,
#                 Algorithm_library.algorithm_name,
#             ).join(
#                 Algorithm_config,
#                 Algorithm_config.id==Algorithm_result.Algorithm_config_id
#             ).join(
#                 Mine,
#                 Algorithm_config.Mine_id==Mine.id
#             ).join(
#                 Equipment,
#                 Algorithm_config.Equipment_id==Equipment.id
#             ).join(
#                 Algorithm_library,
#                 Algorithm_config.Algorithm_library_id == Algorithm_library.id
#             ).filter(query_filter).order_by(Algorithm_result.res_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
#     else:
#         # 定义子查询获取分页数据
#         subquery_algorithm_result = db.session.query(
#             Algorithm_result.id,
#             Algorithm_result.Algorithm_config_id,
#             Algorithm_result.res_time,
#             Algorithm_result.res_type,
#             Algorithm_result.res_image,
#             Algorithm_result.res_video,
#             Algorithm_result.res_frame_skip
#         ).order_by(
#             desc(Algorithm_result.res_time)
#         ).limit(per_page).offset((page - 1) * per_page).subquery()
#
#         # 查询结果总数
#         algorithm_info = db.session.query(func.count(Algorithm_result.res_time).label('library_count')).first()
#         total_count = algorithm_info[0]
#
#         # 主查询获取详细信息
#         algorithm_info = db.session.query(
#             subquery_algorithm_result.c.id.label('Algorithm_result_id'),
#             subquery_algorithm_result.c.res_time,
#             Mine.id.label('Mine_id'),
#             Mine.mine_name,
#             Equipment.id.label('Equipment_id'),
#             Equipment.equipment_name,
#             Algorithm_config.id.label('Algorithm_config_id'),
#             Algorithm_config.conf_name,
#             Algorithm_config.conf_img_resolution,
#             subquery_algorithm_result.c.res_type,
#             subquery_algorithm_result.c.res_image,
#             subquery_algorithm_result.c.res_video,
#             subquery_algorithm_result.c.res_frame_skip,
#             Algorithm_library.algorithm_name,
#         ).join(
#             Algorithm_config,
#             Algorithm_config.id == subquery_algorithm_result.c.Algorithm_config_id
#         ).join(
#             Mine,
#             Algorithm_config.Mine_id == Mine.id
#         ).join(
#             Equipment,
#             Algorithm_config.Equipment_id == Equipment.id
#         ).join(
#             Algorithm_library,
#             Algorithm_config.Algorithm_library_id == Algorithm_library.id
#         ).order_by(
#             desc(subquery_algorithm_result.c.res_time)
#         ).all()
#         # 格式化数据
#         algorithm_data = [{
#             'Algorithm_result_id': i.Algorithm_result_id,
#             'res_time': i.res_time.strftime("%Y-%m-%d %H:%M:%S") if i.res_time else None,
#             'Mine_id': i.Mine_id,
#             'mine_name': i.mine_name,
#             'Equipment_id': i.Equipment_id,
#             'equipment_name': i.equipment_name,
#             'conf_id': i.Algorithm_config_id,
#             'conf_name': i.conf_name,
#             'res_type': configs.type_status[int(i.res_type) - 1]['value'] if i.res_type else None,
#             'res_image': i.res_image,
#             'res_video': i.res_video,
#             'res_frame_skip': i.res_frame_skip,
#             'algorithm_name': i.algorithm_name,
#             'img_resolution': i.conf_img_resolution,
#         } for i in algorithm_info]
#
#         # 构造响应数据
#         response_data = {
#             'total_items': total_count,
#             'total_pages': total_count // per_page + (1 if total_count % per_page > 0 else 0),
#             'current_page': page,
#             'per_page': per_page,
#             'data': algorithm_data,
#         }
#
#         return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})
#
#     if id:
#         algorithm_info = db.session.query(
#             Algorithm_result.id.label('Algorithm_result_id'),
#             Algorithm_result.res_time,
#             Mine.id.label('Mine_id'),
#             Mine.mine_name,
#             Equipment.id.label('Equipment_id'),
#             Equipment.equipment_name,
#             Algorithm_config.id.label('Algorithm_config_id'),
#             Algorithm_config.conf_name,
#             Algorithm_config.conf_img_resolution,
#             Algorithm_result.res_type,
#             Algorithm_result.res_image,
#             Algorithm_result.res_video,
#             Algorithm_result.res_frame_skip,
#             Algorithm_library.algorithm_name,
#         ).join(
#             Algorithm_config,
#             Algorithm_config.id == Algorithm_result.Algorithm_config_id
#         ).join(
#             Mine,
#             Algorithm_config.Mine_id == Mine.id
#         ).join(
#             Equipment,
#             Algorithm_config.Equipment_id == Equipment.id
#         ).join(
#             Algorithm_library,
#             Algorithm_config.Algorithm_library_id == Algorithm_library.id
#         ).filter(Algorithm_result.id == id).order_by(Algorithm_result.res_time.desc()).paginate(page=page,
#                                                                                                 per_page=per_page,
#                                                                                                 error_out=False)
#
#     # 连表查询获取模型应用数据列表
#     algorithm_data = [{
#         'Algorithm_result_id': i.Algorithm_result_id,
#         'res_time': (i.res_time).strftime("%Y-%m-%d %H:%M:%S"),
#         'Mine_id': i.Mine_id,
#         'mine_name': i.mine_name,
#         'Equipment_id': i.Equipment_id,
#         'equipment_name': i.equipment_name,
#         'conf_id':i.Algorithm_config_id,
#         'conf_name':i.conf_name,
#         'res_type': configs.type_status[int(i.res_type)-1]['value'],
#         'res_image': i.res_image,
#         'res_video': i.res_video,
#         'res_frame_skip': i.res_frame_skip,
#         'algorithm_name': i.algorithm_name,
#         'img_resolution': i.conf_img_resolution,
#     } for i in algorithm_info.items]
#
#
#     response_data = {
#         'total_items': algorithm_info.total,
#         'total_pages': algorithm_info.pages,
#         'current_page': algorithm_info.page,
#         'per_page': per_page,
#         'data':  algorithm_data,
#     }
#
#     return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})


# 算法预警--------sql自写分页--------结果展示接口
@model_view.route('/algorithm_result', methods=['GET'])
def algorithm_result():

    # 报警数据id
    id = request.args.get('id')

    # 开始时间
    start_time = request.args.get('start_time')
    # 结束时间
    end_time = request.args.get('end_time')

    # 报警类型
    type_sta = request.args.get('type', None)

    # 算法配置id
    algorithm_id= request.args.get('algorithm_id', None)

    # 矿id
    mine_id = request.args.get('mine_id', None)
    # 监控点id
    equipment_id = request.args.get('equipment_id', None)

    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=15, type=int)

    # 假设前端传递的参数为可能有一个或多个
    filters = []

    # 如果存在开始时间和结束时间参数，加入过滤条件
    if start_time and end_time:
        # 使用 and_ 函数将两个条件组合起来
        filters.append(Algorithm_result.res_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))

    # 报警状态
    if type_sta:
        filters.append(Algorithm_result.res_type == type_sta)

    # 算法配置id
    if algorithm_id:
        filters.append(Algorithm_result.Algorithm_config_id == algorithm_id)

    # 如果存在算法名称参数，将其加入过滤条件
    if mine_id:
        filters.append(Algorithm_result.Mine_id == mine_id)

    if id:
        filters.append(Algorithm_result.id == id)

    if equipment_id:

        # 判断 如果是父类 取父类下边数据
        parent_id = db.session.query(Equipment).filter(Equipment.id == equipment_id).first()
        # 查找父类下边是否有 子类数据
        children = db.session.query(Equipment).filter(Equipment.parent_id == parent_id.id).first()

        # 如果没有子类数据取摄像头
        if not children:
            filters.append(Algorithm_result.Equipment_id == equipment_id)

        # 如果有子类数据取录像机下边子类数据
        else:
            filters.append(Algorithm_result.Equipment_parent_id== equipment_id)

    # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and
    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else True  # True 表示没有过滤条件时，查询所有记录

    # 查询结果总数
    total_count_query = db.session.query(func.count(Algorithm_result.res_time))
    if query_filter is not True:
        total_count_query = total_count_query.filter(query_filter)
    total_count = total_count_query.scalar()


    # 定义子查询获取分页数据
    subquery_algorithm_result = db.session.query(
        Algorithm_result.id,
        Algorithm_result.Algorithm_config_id,
        Algorithm_result.res_time,
        Algorithm_result.res_type,
        Algorithm_result.res_image,
        Algorithm_result.res_video,
        Algorithm_result.res_frame_skip
    ).filter(query_filter if query_filter is not True else True).order_by(
        desc(Algorithm_result.res_time)
    ).limit(per_page).offset((page - 1) * per_page).subquery()

    # 主查询获取详细信息
    algorithm_info = db.session.query(
        subquery_algorithm_result.c.id.label('Algorithm_result_id'),
        subquery_algorithm_result.c.res_time,
        Mine.id.label('Mine_id'),
        Mine.mine_name,
        Equipment.id.label('Equipment_id'),
        Equipment.equipment_name,
        Algorithm_config.id.label('Algorithm_config_id'),
        Algorithm_config.conf_name,
        Algorithm_config.conf_img_resolution,
        subquery_algorithm_result.c.res_type,
        subquery_algorithm_result.c.res_image,
        subquery_algorithm_result.c.res_video,
        subquery_algorithm_result.c.res_frame_skip,
        Algorithm_library.algorithm_name,
    ).join(
        Algorithm_config,
        Algorithm_config.id == subquery_algorithm_result.c.Algorithm_config_id
    ).join(
        Mine,
        Algorithm_config.Mine_id == Mine.id
    ).join(
        Equipment,
        Algorithm_config.Equipment_id == Equipment.id
    ).join(
        Algorithm_library,
        Algorithm_config.Algorithm_library_id == Algorithm_library.id
    ).order_by(
        desc(subquery_algorithm_result.c.res_time)
    ).all()

    # 格式化数据
    algorithm_data = [{
        'Algorithm_result_id': i.Algorithm_result_id,
        'res_time': i.res_time.strftime("%Y-%m-%d %H:%M:%S") if i.res_time else None,
        'Mine_id': i.Mine_id,
        'mine_name': i.mine_name,
        'Equipment_id': i.Equipment_id,
        'equipment_name': i.equipment_name,
        'conf_id': i.Algorithm_config_id,
        'conf_name': i.conf_name,
        'res_type': configs.type_status[int(i.res_type) - 1]['value'] if i.res_type else None,
        'res_image': i.res_image,
        'res_video': i.res_video,
        'res_frame_skip': i.res_frame_skip,
        'algorithm_name': i.algorithm_name,
        'img_resolution': i.conf_img_resolution,
    } for i in algorithm_info]

    # 构造响应数据
    response_data = {
        'total_items': total_count,
        'total_pages': total_count // per_page + (1 if total_count % per_page > 0 else 0),
        'current_page': page,
        'per_page': per_page,
        'data': algorithm_data,
    }

    return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})


#  每个监控点下算法各占比例
@model_view.route('/algorithm_ratio', methods=['GET'])
def algorithm_ratio():

    # 矿id
    mine_id = request.args.get('mine_id', None)
    # 监控点id
    equipment_id = request.args.get('equipment_id', None)

    # 开始时间
    start_time = request.args.get('start_time')
    # 结束时间
    end_time = request.args.get('end_time')


    # 假设前端传递的参数为可能有一个或多个
    filters = []

    # 如果存在算法名称参数，将其加入过滤条件
    if mine_id:
        filters.append(Algorithm_config.Mine_id == mine_id)

    if equipment_id:

        # 判断 如果是父类 取父类下边数据
        parent_id = db.session.query(Equipment).filter(Equipment.id == equipment_id).first()
        # 查找父类下边是否有 子类数据
        children = db.session.query(Equipment).filter(Equipment.parent_id == parent_id.id).first()
        # 如果没有子类数据取摄像头
        if not children:
            filters.append(Equipment.id == equipment_id)

        # 如果有子类数据取录像机下边子类数据
        else:
            filters.append(Equipment.parent_id == equipment_id)

    # 如果存在开始时间和结束时间参数，加入过滤条件
    if start_time and end_time:
        # 查询在开始时间跟结束时间之内
        filters.append(Algorithm_result.res_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))

    # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and

    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None

    if query_filter is not None:

        algorithm_info = db.session.query(
                func.count(Algorithm_library.id).label('library_count'),
                Algorithm_library.algorithm_name,
        ).join(
                Algorithm_config,
                Algorithm_config.Algorithm_library_id == Algorithm_library.id,
        ).join(
                Algorithm_result,
                Algorithm_config.id == Algorithm_result.Algorithm_config_id,
        ).join(
                Mine,
                Algorithm_config.Mine_id == Mine.id,
        ).join(
                Equipment,
                Algorithm_config.Equipment_id == Equipment.id,
        ).filter(query_filter).group_by(Algorithm_config.Algorithm_library_id).all()
    else:

        algorithm_info = db.session.query(
                func.count(Algorithm_library.id).label('library_count'),
                Algorithm_library.algorithm_name,
        ).join(
                Algorithm_config,
                Algorithm_config.Algorithm_library_id == Algorithm_library.id,
        ).join(
                Algorithm_result,
                Algorithm_config.id == Algorithm_result.Algorithm_config_id,
        ).join(
                Mine,
                Algorithm_config.Mine_id == Mine.id,
        ).join(
                Equipment,
                Algorithm_config.Equipment_id == Equipment.id,
        ).group_by(Algorithm_config.Algorithm_library_id).all()


    # 连表查询获取模型应用数据列表
    algorithm_data = [{
        'name': i.algorithm_name,
        'value': i.library_count,
    } for i in algorithm_info]

    return jsonify({'code': 200, 'msg': '查询成功', 'data_list': algorithm_data})




# 实时视频展示返回
@model_view.route('/video_show', methods=['POST', 'GET'])
def video_show():

    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=3, type=int)

    equipment_info = db.session.query(Equipment.id,Equipment.equipment_name,Equipment.Mine_id,Equipment.equipment_ip,Equipment.equipment_uname,
                                      Equipment.equipment_password,Equipment.equipment_type,Equipment.parent_id,Equipment.code
                                      ).filter(

        (   (Equipment.equipment_type == '浙江双视热成像')|(Equipment.equipment_type == '摄像头')
            |
            ((Equipment.parent_id != None) & (Equipment.equipment_type == '录像机'))
            |
            ((Equipment.parent_id != None) & (Equipment.equipment_type == '特殊摄像头')
            )
        )
    # ).all()
    ).paginate(page=page, per_page=per_page, error_out=False)
    # ).paginate(page=page, per_page=per_page, error_out=False)

    # result_count = len(equipment_info)
    # print(result_count)

    equipment_data = []
    for i in equipment_info.items:
        rtsp = ''
        # 判断摄像头类型获取rtsp流
        if i.equipment_type == '摄像头':
            rtsp = 'rtsp://{}:{}@{}'.format(i.equipment_uname, i.equipment_password, i.equipment_ip)
        elif i.equipment_type == '录像机':
            rtsp = get_children_rtsp(i.parent_id, i.code, 1)
        elif i.equipment_type == '特殊摄像头':
            rtsp = get_children_rtsp(i.parent_id, i.code, 2)
        elif i.equipment_type == '浙江双视热成像':
            rtsp = 'rtsp://{}:{}@{}:554/live/chn0'.format(i.equipment_uname, i.equipment_password, i.equipment_ip)

        dict_res = {
            'equipment_id': i.id,
            'equipment_name': i.equipment_name,
            'mine_id': i.Mine_id,
            'equipment_ip': rtsp,
            'ip': i.equipment_ip,
            'uname': i.equipment_uname,
            'password': i.equipment_password,
            'data_now_result': datainfo(i.id, 2),
            'data_old_result': datainfo(i.id, 1),
            'data_res': datainfo(i.id, 2) + datainfo(i.id, 1),  # 使用预先计算的值
        }
        equipment_data.append(dict_res)



    # # 将设备信息组合到主数据中
    # for i in mine_data:
    #     mine_id = i['mine_id']
    #     i['children'] = [equip for equip in equipment_data if equip['mine_id'] == mine_id]

    # 分页所需数据
    response_data = {
        'total_items': equipment_info.total,
        'total_pages': equipment_info.pages,
        'current_page': equipment_info.page,
        'per_page': per_page,
        'data':  equipment_data,
    }

    return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})





# 算法仓数据展示编写
@model_view.route('/algorithm_data', methods=['GET'])
def algorithm_data():

    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=15, type=int)

    # 文件名称
    algorithm_file_name = request.args.get('algorithm_file_name')
    # 算法名称
    algorithm_name = request.args.get('algorithm_name')

    # 运行状态
    algorithm_status = request.args.get('algorithm_status')

    # 产商类型
    algorithm_trade_type = request.args.get('algorithm_trade_type')

    # 假设前端传递的参数为可能有一个或多个
    filters = []

    # 如果存在算法名称参数，将其加入过滤条件
    if algorithm_file_name:
        filters.append(Algorithm_library.algorithm_file_name.ilike(f"%{algorithm_file_name}%"))

    if algorithm_name:
        filters.append(Algorithm_library.algorithm_name.ilike(f"%{algorithm_name}%"))

    if algorithm_status:
        filters.append(Algorithm_library.algorithm_status==int(algorithm_status))

    if algorithm_trade_type:
        filters.append(Algorithm_library.algorithm_trade_type==int(algorithm_trade_type))

    # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and

    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None
    
    if query_filter is not None:

        # 查询全部数据
        algorithm_data = db.session.query(Algorithm_library).filter(query_filter).order_by(Algorithm_library.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)

    else:
        # 查询全部数据
        algorithm_data = db.session.query(Algorithm_library).order_by(Algorithm_library.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # 连表查询获取模型应用数据列表
    algorithm_info = [{
        'id': i.id,
        'algorithm_file_name': i.algorithm_file_name,
        'algorithm_name': i.algorithm_name,
        'algorithm_type': configs.algorithm_type[int(i.algorithm_type) - 1]['value'],
        'algorithm_version': i.algorithm_version,
        'algorithm_status': configs.status[int(i.algorithm_status) - 1]['value'],
        'algorithm_trade_type': i.algorithm_trade_type,
        'create_time': (i.create_time).strftime("%Y-%m-%d %H:%M:%S"),
        'algorithm_ps': i.algorithm_ps
    } for i in algorithm_data.items]

    # 构建返回的 JSON
    response_data = {
        'total_items': algorithm_data.total,
        'total_pages': algorithm_data.pages,
        'current_page': algorithm_data.page,
        'per_page': per_page,
        'data': algorithm_info,
    }


    return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})



#算法配置历史记录展示
@model_view.route('/algorithm_config_history',methods=['GET'])
def algorithm_config_history():
    r = Redis(Redis_ip, Redis_port, 'list')
    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=15, type=int)
    id = request.args.get('id')
    if id:
        # 查询全部数据
        algorithm_res = db.session.query(
            Algorithm_config_history.id,
            Algorithm_config_history.status,
            Algorithm_library.id.label('Algorithm_library_id'),
            Algorithm_library.algorithm_name,
            Mine.id.label('Mine_id'),
            Mine.mine_name,
            Equipment.id.label('Equipment_id'),
            Equipment.equipment_name,
            Equipment.equipment_type,
            Equipment.code,
            Algorithm_config_history.conf_name,
            Algorithm_config_history.conf_object,
            Algorithm_config_history.conf_time,
            Algorithm_config_history.conf_area,
            Algorithm_config_history.Algorithm_test_type_id.label('test_type_id'),
            Algorithm_config_history.shield_status,
            Algorithm_config_history.tem_conf_area,
            Algorithm_config_history.tem_frames,
            Algorithm_config_history.draw_type,
            Algorithm_config_history.confidence,
            Algorithm_config_history.interval_time,
            Algorithm_config_history.conf_img_resolution,
            Algorithm_config_history.duration_time,
            Algorithm_config_history.image_draw_type,
            Algorithm_config_history.update_time,
            Algorithm_config_history.Algorithm_config_ps,
            Algorithm_config_history.operation_type
        ).join(
            Algorithm_config_history,
            Algorithm_library.id == Algorithm_config_history.Algorithm_library_id
        ).join(
            Mine,
            Algorithm_config_history.Mine_id == Mine.id
        ).join(
            Equipment,
            Algorithm_config_history.Equipment_id == Equipment.id
        ).join(
            Algorithm_config,
            Algorithm_config_history.config_id == Algorithm_config.id
        ).filter(Algorithm_config_history.config_id==id).order_by(Algorithm_config_history.update_time.desc()).paginate(page=page, per_page=per_page, error_out=False)

        if algorithm_res:

            algorithm_data = [{
                'id': i.id,
                'image': '/static/' + str(
                    os.path.basename(r.get_string('em_{}'.format(i.Equipment_id)))) if i.Equipment_id else '',
                'Algorithm_library_id': i.Algorithm_library_id,
                'algorithm_name': i.algorithm_name,
                'Mine_id': i.Mine_id,
                'mine_name': i.mine_name,
                'Equipment_id': i.Equipment_id,
                'equipment_name': i.equipment_name,
                'equipment_type': i.equipment_type,
                'equipment_code': i.code,
                'conf_name': i.conf_name if i.conf_name else '',
                'conf_object': i.conf_object if i.conf_object else '',
                'conf_time': (i.conf_time).strftime("%Y-%m-%d %H:%M:%S"),
                'conf_area': i.conf_area if i.conf_area else '',
                'status': configs.status[int(i.status) - 1]['value'],
                'shield_status,': i.shield_status,
                'tem_conf_area': i.tem_conf_area,
                'tem_frames': i.tem_frames,
                'draw_type': i.draw_type,
                'confidence': i.confidence,
                'interval_time': i.interval_time,
                'img_resolution': i.conf_img_resolution,
                'duration_time': i.duration_time,
                'image_draw_type': i.image_draw_type,
                'update_time': (i.update_time).strftime("%Y-%m-%d %H:%M:%S") if i.update_time else '',
                'Algorithm_config_ps': i.Algorithm_config_ps,
                'operation_type': i.operation_type
            } for i in algorithm_res.items]

            return jsonify({'code': 200, 'datalist': algorithm_data,'msg':'查询成功'})
        else:
            return jsonify({'code': 400, 'datalist': [],'msg':'未有该配置的详情信息'})

    else:
        # 查询全部数据
        algorithm_res = db.session.query(
            Algorithm_config_history.id,
            Algorithm_config_history.status,
            Algorithm_library.id.label('Algorithm_library_id'),
            Algorithm_library.algorithm_name,
            Mine.id.label('Mine_id'),
            Mine.mine_name,
            Equipment.id.label('Equipment_id'),
            Equipment.equipment_name,
            Equipment.equipment_type,
            Equipment.code,
            Algorithm_config_history.conf_name,
            Algorithm_config_history.conf_object,
            Algorithm_config_history.conf_time,
            Algorithm_config_history.conf_area,
            Algorithm_config_history.Algorithm_test_type_id.label('test_type_id'),
            Algorithm_config_history.shield_status,
            Algorithm_config_history.tem_conf_area,
            Algorithm_config_history.tem_frames,
            Algorithm_config_history.draw_type,
            Algorithm_config_history.confidence,
            Algorithm_config_history.interval_time,
            Algorithm_config_history.conf_img_resolution,
            Algorithm_config_history.duration_time,
            Algorithm_config_history.image_draw_type,
            Algorithm_config_history.update_time,
            Algorithm_config_history.Algorithm_config_ps,
            Algorithm_config_history.operation_type
        ).join(
            Algorithm_config_history,
            Algorithm_library.id == Algorithm_config_history.Algorithm_library_id
        ).join(
            Mine,
            Algorithm_config_history.Mine_id == Mine.id
        ).join(
            Equipment,
            Algorithm_config_history.Equipment_id == Equipment.id
        ).order_by(Algorithm_config_history.update_time.desc()).paginate(page=page, per_page=per_page, error_out=False)


    # 连表查询获取模型应用数据列表
        algorithm_data = [{
            'id': i.id,
            'image': '/static/' + str(os.path.basename(r.get_string('em_{}'.format(i.Equipment_id)))) if i.Equipment_id else '',
            'Algorithm_library_id': i.Algorithm_library_id,
            'algorithm_name': i.algorithm_name,
            'Mine_id': i.Mine_id,
            'mine_name': i.mine_name,
            'Equipment_id': i.Equipment_id,
            'equipment_name': i.equipment_name,
            'equipment_type': i.equipment_type,
            'equipment_code': i.code,
            'conf_name': i.conf_name if i.conf_name else '',
            'conf_object': i.conf_object if i.conf_object else '',
            'conf_time': (i.conf_time).strftime("%Y-%m-%d %H:%M:%S"),
            'conf_area': i.conf_area if i.conf_area else '',
            'status': configs.status[int(i.status) - 1]['value'],
            'shield_status,': i.shield_status,
            'tem_conf_area': i.tem_conf_area,
            'tem_frames': i.tem_frames,
            'draw_type': i.draw_type,
            'confidence': i.confidence,
            'interval_time': i.interval_time,
            'img_resolution': i.conf_img_resolution,
            'duration_time': i.duration_time,
            'image_draw_type': i.image_draw_type,
            'update_time': (i.update_time).strftime("%Y-%m-%d %H:%M:%S") if i.update_time else '',
            'Algorithm_config_ps': i.Algorithm_config_ps,
            'operation_type': i.operation_type
        } for i in algorithm_res.items]
    # 构建返回的 JSON
        response_data = {
            'total_items': algorithm_res.total,
            'total_pages': algorithm_res.pages,
            'current_page': algorithm_res.page,
            'per_page': per_page,
            'data': algorithm_data,
        }

    return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})


# 算法仓状态修改
@model_view.route('/algorithm_data_update', methods=['POST'])
def algorithm_data_update():

    # 算法 id
    id = request.form.get('id')

    # 1 运行 2 停止
    status = request.form.get('status')

    # 查找当前算法仓运行状态id
    data = db.session.query(Algorithm_library).filter(Algorithm_library.id == id).first()
    print(data)

    # 对接受参数来进行该算法仓状态修改
    if data:
        data.algorithm_status = 1 if status =='运行' else 2
        db.session.commit()
        # redis队列 当算法配置修改完成时，数据写入队列，寒武纪盒子redis监听到数据重新执行
        queue_redis = TestQueue()
        queue_redis.push()
    else:
        return jsonify({'code': 400, 'msg': '修改数据不存在'})

    return jsonify({'code':200,'msg':'修改成功'})




# 监控点算法配置运行状态
@model_view.route('/algorithm_conf_update', methods=['POST'])
def algorithm_conf_update():

    # 算法 id
    id = request.form.get('id')

    # 1 运行 2 停止
    status = request.form.get('status')

    # 查找当前监控点运行状态id
    data = db.session.query(Algorithm_config).filter(Algorithm_config.id == id).first()

    # 对接受参数来进行该监控点状态修改
    if data:
        data.status = 1 if status =='运行' else 2
        # 提交
        db.session.commit()
        # redis队列 当算法配置修改完成时，数据写入队列，寒武纪盒子redis监听到数据重新执行
    else:
        return jsonify({'code': 400, 'msg': '修改数据不存在'})

    # 获取算法配置要跑进程数据的条数，按条数写入队列来进行重启
    queue_redis = TestQueue()
    queue_redis.push()

    return jsonify({'code':200,'msg':'修改成功'})


# 录像机设备同步接口
@model_view.route('/VCR_data_sync', methods=['POST'])
def VCR_data_sync():

    vcr_type = request.form.get('vcr_type') # 厂商类型
    vcr_way = request.form.get('vcr_way')   # 接入方式
    vcr_name = request.form.get('vcr_name') # 录像机名称
    username = request.form.get('username') # 录像机用户
    password = request.form.get('password') # 录像机密码
    ip = request.form.get('ip') # 录像机ip
    port = request.form.get('port') #录像机端口
    Mine_id = request.form.get('Mine_id') # 矿id



    vcr_type = (configs.manufacturer_type[int(vcr_type)-1])['value'] if vcr_type else 1  # 厂商类型
    vcr_way = (configs.vcr_way[int(vcr_way)-1])['value'] if  vcr_way else 1  # 接入方式

    params = [vcr_type,vcr_way,vcr_name,username,password,port,Mine_id,ip]
    print(params)

    if not all(params):
        return jsonify({'code': 400, 'msg': '录像机同步有未填写项！'})


    # 先查询当前录像机是否存在，
    vcr_data = db.session.query(Equipment).filter(Equipment.equipment_ip == ip).first()
    # 如果存在则返回，录像机设备信息已经存在
    if vcr_data:
        return jsonify({'code':400,'msg':'录像机设备信息已经存在,同步失败！'})

    # 调用方法获取录像机同步数据  数据格式为 [{},{}]
    vcr_data_info = VCR_data_info(username,password,ip,port)
    print(username,password,ip,port,type(username),type(password),type(ip),type(port))
    # 当返回值为列表的时候说明参数错误，请求超时
    if vcr_data_info == []:
        return jsonify({'code':400,'msg':'录像机设备信息不存在,请输入正确参数！'})

    # 返回值有值说明正确进行同步操作,

    # 写入录像机同步表
    VCR_data_data = VCR_data(
        vcr_type = vcr_type if vcr_type in ['海康', '大华', '索尼', '宇视', '天地伟业', '三星'] else None,
        vcr_way = vcr_way if vcr_way  in ['私有SDK','Onvif','GB28181'] else None,
        vcr_name = vcr_name,
        vcr_ip = ip,
        vcr_username = username,
        vcr_password = password,
        vcr_port = port,
        Mine_id = Mine_id,
        # vcr_status = db.Column(db.String(50), comment='录像机同步状态 1 同步完成 2 同步未完成' )
    )
    db.session.add(VCR_data_data)
    db.session.commit()

    # 判断私有sdk接入
    if vcr_type == '海康' and  vcr_way == '私有SDK':
        print('海康接入')
        # ----------同步的时候录像机父类设备写入----------
        # 添加录像机父设备
        equipment_data = Equipment(
            equipment_type='录像机',
            manufacturer_type='海康',
            equipment_name=vcr_name,
            equipment_ip=ip,
            equipment_uname=username,
            equipment_password=password,
            Mine_id=int(Mine_id) if Mine_id else None,
            online=1,
            VCR_data_id=VCR_data_data.id,
        )
        db.session.add(equipment_data)
        db.session.commit()
        # 获取对应子集数据的  默认通道 code 数据
        children_list = children_list_get_code(vcr_data_info)

        for i in children_list:
            # 添加录像机子设备
            # 父类设备为 parent_id

            child_equipment_data = Equipment(
                equipment_type=equipment_data.equipment_type if equipment_data.equipment_type else None,
                manufacturer_type=equipment_data.manufacturer_type if equipment_data.manufacturer_type else None,
                equipment_name=i['name'] if i.get('name') else None,
                equipment_ip=i['ip_address'] if i.get('ip_address') is not None else None,
                equipment_uname=i.get('username') if i.get('username') else None,
                equipment_password=equipment_data.equipment_password if equipment_data.equipment_password else None,
                equipment_aisles=i.get('equipment_aisles') if i.get('equipment_aisles') else None,
                equipment_codetype=equipment_data.equipment_codetype if equipment_data.equipment_codetype else None,
                Mine_id=int(equipment_data.Mine_id) if equipment_data.Mine_id else None,
                parent_id=int(equipment_data.id) if equipment_data.id else None,
                code=i.get('code') if i.get('code') else None,
                VCR_data_id = VCR_data_data.id,
                online = 1 if i.get('online') == 'true' else 2,
            )
            db.session.add(child_equipment_data)

    VCR_data_data.vcr_status=1
    db.session.commit()

    return jsonify({'code':200,'msg':'录像机设备信息同步成功！'})


# 手动刷新录像机同步
@model_view.route('/manual_sync',methods=['POST'])
def manual_sync():
    # 查找录像机信息
    vcr_dict_list = convert_folder_to_dict_list(db.session.query(VCR_data).all(),
                                                ['id', 'vcr_ip', 'vcr_username', 'vcr_password', 'vcr_port', 'Mine_id'])
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

            if external_data_list == []:
                print('当前录像机数据不存在或账密错误！')
            else:
                # 获取外部设备信息列表,用于查询数据表存在矿上不存在删除操作
                external_data_ip_list = [i.get('ip_address') for i in external_data_list]

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

                # print(external_data_list,'获取的外部信息')
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
                            code=str(id) + '01',
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
        print('录像机设备手动同步更新成功!')

    return jsonify({'code':200,'msg':'手动更新成功'})


# 录像机设备修改及详情接口
@model_view.route('/VCR_data_update', methods=['GET'])
def VCR_data_update():

    # 接受类型 当为1的时候为详情  2的时候为修改
    type_st =  request.args.get('type_st')

    # 录像机id
    id  = request.args.get('id')

    # 当为1的时候为详情
    if int(type_st) == 1:
        # 查找录像机id对应数据
        vcr_res  = db.session.query(VCR_data).filter(VCR_data.id == id).first()
        # 当查询到录像机对应id
        if vcr_res:
            # 序列化数据
            dict_res = convert_to_dict(vcr_res,['id','vcr_type','vcr_way','vcr_name','vcr_ip','vcr_username','vcr_password','vcr_port','Mine_id'])
            return jsonify({'code': 200,'msg':'查找成功！', 'data': dict_res})
        # 未查找到数据返回
        else:
            return jsonify({'code': 400,'msg':'未查找到数据！！','data': {}})

    # 当为2的时候为修改
    if int(type_st) == 2:

        vcr_type = request.args.get('vcr_type')  # 厂商类型
        vcr_way = request.args.get('vcr_way')  # 接入方式
        vcr_name = request.args.get('vcr_name')  # 录像机名称
        username = request.args.get('username')  # 录像机用户
        password = request.args.get('password')  # 录像机密码
        ip = request.args.get('ip')  # 录像机ip
        port = request.args.get('port')  # 录像机端口
        Mine_id = request.args.get('Mine_id')  # 矿id

        vcr_type = (configs.manufacturer_type[int(vcr_type) - 1])['value'] if vcr_type else 1  # 厂商类型
        vcr_way = (configs.vcr_way[int(vcr_way) - 1])['value'] if vcr_way else 1  # 接入方式


        # 查找录像机id对应数据
        vcr_res = db.session.query(VCR_data).filter(VCR_data.id == id).first()
        if vcr_res:
            # 查找id进行修改
            update_query = (
                update(VCR_data)
                    .where(VCR_data.id == id)
                    .values(
                    vcr_type=vcr_type if vcr_type in ['海康', '大华', '索尼', '宇视', '天地伟业', '三星'] else None,
                    vcr_way=vcr_way if vcr_way in ['私有SDK', 'Onvif', 'GB28181'] else None,
                    vcr_name=vcr_name,
                    vcr_ip=ip,
                    vcr_username=username,
                    vcr_password=password,
                    vcr_port=port,
                    Mine_id=Mine_id,
                )
            )

            update_query_parent = (
                update(Equipment)
                    .where(Equipment.VCR_data_id == id,Equipment.parent_id == None)
                    .values(
                    manufacturer_type= vcr_type if vcr_type in ['海康', '大华', '索尼', '宇视', '天地伟业', '三星'] else None,
                    equipment_name=vcr_name,
                    Mine_id=Mine_id,
                )
            )

            update_query_children = (
                update(Equipment)
                    .where(Equipment.VCR_data_id == id,Equipment.parent_id != None)
                    .values(
                    manufacturer_type=vcr_type if vcr_type in ['海康', '大华', '索尼', '宇视', '天地伟业', '三星'] else None,
                    Mine_id=Mine_id,
                )
            )


            # 执行更新
            db.session.execute(update_query)
            db.session.execute(update_query_parent)
            db.session.execute(update_query_children)
            db.session.commit()

            return jsonify({'code':200,'msg':'更新完成'})
        else:
            return jsonify({'code':400,'msg':'更新数据不存在'})

    return jsonify({'code': 400,'msg':'类型不存在'})


# 录像机设备展示接口 (1. 全部， 2.录像机信息及录像机下方子设备信息)
@model_view.route('/VCR_data_show', methods=['GET'])
def VCR_data_show():
    # 1全部  2 查询录像机信息对应id录像机及子设备信息
    type_st = request.args.get('type_st',None)
    id = request.args.get('id',None)

    params = [type_st]

    # 当必传参数没填，返回错误
    if not all(params):
        return jsonify({'code': 400, 'msg': '参数状态未有！'})

    if int(type_st) == 1:
        # 查询录像机全部信息
        res = convert_folder_to_dict_list(db.session.query(VCR_data).all(),['id','vcr_type','vcr_way','vcr_name','vcr_ip','vcr_username',
                                               'vcr_password','vcr_port','Mine_id'])
        return jsonify({'code':200,'msg':"查询成功",'data':res})
    else:
        # 查询录像机及子设备信息
        res = convert_to_dict(db.session.query(VCR_data).filter(VCR_data.id == id).first(), ['id', 'vcr_type', 'vcr_way', 'vcr_name', 'vcr_ip', 'vcr_username',
                                                'vcr_password', 'vcr_port', 'Mine_id'])
        # 序列化查找子设备信息
        res_children = convert_folder_to_dict_list(db.session.query(Equipment).filter(Equipment.VCR_data_id==id,Equipment.parent_id !=None).all(),['id','equipment_type','manufacturer_type',
                                                                 'equipment_name','equipment_ip','equipment_uname',
                                                                 'equipment_password','create_time','online'])
        # 将子设备信息赋值给父设备参数返回
        res['children'] = res_children

        return jsonify({'code': 200, 'msg': "查询成功", 'data': res})



# 录像机设备删除接口  （删除相关下方子设备-算法配置-算法结果）
@model_view.route('/VCR_data_delete', methods=['POST'])
def VCR_data_delete():
    # 录像机id
    id = request.form.get('id', None)

    # 查找设备ids
    em_ids = db.session.query(Equipment.id).filter(Equipment.VCR_data_id==id).all()
    em_ids = [ i[0] for i in em_ids]

    # 当设备ids存在时
    if em_ids:
        # 根据设备ids查找算法配置相关数据
        algorithm_config_res = db.session.query(Algorithm_config.id).filter(Algorithm_config.Equipment_id.in_(em_ids)).all()
        algorithm_config_res = [ i[0] for i in algorithm_config_res]

        # 当查找到算法配置ids时  进行算法配置删除操作
        if algorithm_config_res:

            # 删除算法配置id
            db.session.query(Algorithm_config).filter(Algorithm_config.id.in_(algorithm_config_res)).delete()

            # 根据算法配置id删除算法结果id
            db.session.query(Algorithm_result).filter(Algorithm_result.Algorithm_config_id.in_(algorithm_config_res)).delete()


    # 删除录像机数据
    db.session.query(VCR_data).filter(VCR_data.id==id).delete()

    # 删除设备数据
    db.session.query(Equipment).filter(Equipment.id.in_(em_ids)).delete()

    db.session.commit()

    return jsonify({'code':200,'msg':'删除成功'})


# 算法仓数据删除接口
@model_view.route('/algorithm_library_delete', methods=['POST'])
def algorithm_library_delete():

    # 获取算法id
    ids = request.json.get('id',None)
    print(ids)

    # 参数构建判断是否为空
    params = [ids]

    # 如果参数未获取到
    if not all(params):
        return jsonify({'code': 400, 'msg': '缺少删除设备id参数'})

    # 当存在ids
    if ids:
        # 删除算法id
        db.session.query(Algorithm_library).filter(Algorithm_library.id.in_(ids)).delete()

    # 查找算法id
    # res = db.session.query(Algorithm_library.id).filter(Algorithm_library.id == id).first()

    # # 根据算法id查找是否有配置id，如果存在配置id进行删除， 算法结果删除
    # conf_id = db.session.query(Algorithm_config.id).filter(Algorithm_config.Algorithm_library_id==res[0]).all()
    # conf_ids = [ i[0] for i in conf_id]

    # # 删除算法配置id
    # db.session.query(Algorithm_config).filter(Algorithm_config.id.in_(conf_ids)).delete()
    #
    # # 根据算法配置id删除算法结果id
    # db.session.query(Algorithm_result).filter(Algorithm_result.Algorithm_config_id.in_(conf_ids)).delete()

    # 提交
    db.session.commit()

    return jsonify({'code':200,'msg':'删除成功'})





# 模型类别 select 筛选返回
@model_view.route('/model_type', methods=['GET','POST'])
@jwt_required() # token身份验证
def model_type():

    res = request.args.get('model_type')
    print(res,'11111')
    return jsonify({'code': 200, 'msg': '查询成功', 'data': []})
