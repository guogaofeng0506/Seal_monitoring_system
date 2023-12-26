
from flask import jsonify, request, Blueprint

import configs
from configs import *
from modules.Tables import *
from sqlalchemy import and_,func


import os

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# 创建蓝图，对应的register目录
model_view = Blueprint('model_view', __name__)


# 递归查找 parent_id 直到没有 向下找
def find_parent_id(parent_id):
    # 使用生成器
    def recursive_query(parent_id):
        with_parent_id = db.session.query(
            Equipment.id, Equipment.equipment_type,
            Equipment.manufacturer_type, Equipment.equipment_name,
            Equipment.equipment_ip, Equipment.equipment_uname,
            Equipment.equipment_password, Equipment.equipment_aisles,
            Equipment.equipment_codetype, Equipment.user_status,
            Equipment.create_time, Equipment.parent_id
        ).filter(Equipment.parent_id == parent_id).all()

        for folder in with_parent_id:
            yield folder
            yield from recursive_query(folder.id)

    return list(recursive_query(parent_id))


# 转换函数
def row_to_dict(row, keys):
    return {key: value for key, value in zip(keys, row)}

# 子数据
def children_data(equipment_list,vcr_ids):
    for i, equipment in enumerate(equipment_list):
        # 定义子集列表，如果有数据则填入
        # children = []
        id = equipment['id']
        # 在 vcr_ids 中查找匹配的 id
        if id in vcr_ids:
            # 使用 find_parent_id 获取与当前录像机关联的设备
            results = find_parent_id(id)

            # 检查是否有结果
            if results:
                # 获取字段名列表
                keys = results[0]._mapping.keys()
                # 使用 find_parent_id 获取与当前录像机关联的设备
                children = [row_to_dict(result, keys) for result in results]

                # 将 children 赋值给当前记录的 'children' 字段
                equipment_list[i]['children'] = children
            else:
                equipment_list[i]['children'] = []
    return equipment_list

# 获取监控点下方详情  默认为当天
def datainfo(equipment_id,now):
    # 1为所有 2为当天
    if now == 1:
        filters = [Equipment.id == equipment_id]
    else:
        filters = [Equipment.id == equipment_id, db.func.date(Algorithm_result.res_time) == datetime.now().date()]

    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None


    res = db.session.query(Algorithm_library.algorithm_name,Algorithm_config.conf_name,Algorithm_result.res_time,Algorithm_result.res_type
                           ).join(Algorithm_config, Algorithm_config.Algorithm_library_id == Algorithm_library.id
                           ).join(Algorithm_result,Algorithm_config.id == Algorithm_result.Algorithm_config_id
                           ).join(Mine, Mine.id == Algorithm_config.Mine_id
                           ).join(Equipment,Equipment.id == Algorithm_config.Equipment_id).filter(query_filter).all()
    data = [{'algorithm_name': i.algorithm_name, 'conf_name':i.conf_name,'res_time':(i.res_time).strftime("%Y-%m-%d %H:%M:%S"),'res_type':configs.type_status[int(i.res_type)-1]['value'],} for i in res]
    return data


# 获取视频为录像机子集的返回格式  参数为  父级id  子集通道code
def get_children_rtsp(id,code):

    parent_data = db.session.query(Equipment).filter(Equipment.id == id).first()

    if parent_data:

        user = parent_data.equipment_uname
        password = parent_data.equipment_password
        ip = parent_data.equipment_ip

        result = 'rtsp://{}:{}@{}:554/Streaming/Unicast/Channels/{}'.format(user,password,ip,code)
    else:
        result = None
    return result


# 设备添加接口
@model_view.route('/equipment_create', methods=['POST'])
def equipment_create():

    equipment_type = request.json.get('equipment_type', None)  # '设备类型' ('摄像头','录像机')
    manufacturer_type = request.json.get('manufacturer_type', None)  # ('海康', '大华','索尼','宇视','天地伟业','三星') 厂商类型
    equipment_name = request.json.get('equipment_name', None)  # '设备名称'
    equipment_ip = request.json.get('equipment_ip', None)  # 'IP地址'
    equipment_uname = request.json.get('equipment_uname', None)  # '用户名'
    equipment_password = request.json.get('equipment_password', None)  # '密码'
    equipment_aisles = request.json.get('equipment_aisles', None)  # '通道'
    equipment_codetype = request.json.get('equipment_codetype', None)  # ('H265','H264') '码流类型'
    Mine_id = request.json.get('Mine_id', None)  # '矿名称id'

    # 当为录像机的时候传子设备数据
    children_list = request.json.get('children_list', None)

    equipment_type = (configs.equipment_type[int(equipment_type)-1])['value'] if equipment_type else 1
    manufacturer_type = (configs.manufacturer_type[int(manufacturer_type)-1])['value'] if manufacturer_type else 1
    equipment_codetype = (configs.equipment_codetype[int(equipment_codetype)-1])['value'] if  equipment_codetype else 1


    # 查询user_id是否存在
    equipment_result = db.session.query(Equipment).filter(Equipment.equipment_ip == equipment_ip).first()
    if equipment_result:
        return jsonify({'code': 400, 'msg': '设备已经存在'})


    # 判断当添加数据类型为 '录像机'  子列表数据添加

    if equipment_type == '录像机':
        # 添加录像机父设备
        equipment_data = Equipment(
            equipment_type=equipment_type if equipment_type in ['摄像头', '录像机'] else None,
            manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业','三星'] else None,
            equipment_name=equipment_name if equipment_name else None,
            equipment_ip=equipment_ip if equipment_ip is not None else None,
            equipment_uname=equipment_uname if equipment_uname else None,
            equipment_password=equipment_password if equipment_password else None,
            equipment_aisles=equipment_aisles if equipment_aisles else None,
            equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
            Mine_id=int(Mine_id) if Mine_id else None,
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
                    equipment_uname=i.get('equipment_uname') if i.get('equipment_uname') else None,
                    equipment_password=i.get('equipment_password') if i.get('equipment_password') else None,
                    equipment_aisles=i.get('equipment_aisles') if i.get('equipment_aisles') else None,
                    equipment_codetype=equipment_data.equipment_codetype if equipment_data.equipment_codetype else None,
                    Mine_id=int(equipment_data.Mine_id) if equipment_data.Mine_id else None,
                    parent_id=int(equipment_data.id) if equipment_data.id else None,
                    code=i.get('code') if i.get('code') else None,
                )
                db.session.add(child_equipment_data)
                db.session.commit()

    else:
        equipment_data = Equipment(
            equipment_type=equipment_type if equipment_type in ['摄像头', '录像机'] else None,
            manufacturer_type=manufacturer_type if manufacturer_type in ['海康', '大华', '索尼', '宇视', '天地伟业',
                                                                         '三星'] else None,
            equipment_name=equipment_name if equipment_name else None,
            equipment_ip=equipment_ip if equipment_ip is not None else None,
            equipment_uname=equipment_uname if equipment_uname else None,
            equipment_password=equipment_password if equipment_password else None,
            equipment_aisles=equipment_aisles if equipment_aisles else None,
            equipment_codetype=equipment_codetype if equipment_codetype in ['H265', 'H264'] else None,
            Mine_id=int(Mine_id) if Mine_id else None,
        )
        db.session.add(equipment_data)
        db.session.commit()

    return jsonify({'code': 200, 'msg': '设备添加成功', })


# # 设备数据展示接口
# @model_view.route('/equipment_show', methods=['GET'])
# def equipment_show():
#     # '设备名称'
#     equipment_name = request.args.get('equipment_name', None)
#     # '设备类型' ('摄像头','录像机')
#     equipment_type = request.args.get('equipment_type', None)
#
#     # 第几页
#     page = request.args.get('page', default=1, type=int)
#     # 每页条数
#     per_page = request.args.get('per_page', default=15, type=int)
#
#     # 假设前端传递的参数为 equipment_name 和 equipment_type，可能有一个或两个
#     filters = []
#
#     if equipment_name:
#         filters.append(Equipment.equipment_name == equipment_name)
#
#     if equipment_type:
#         filters.append(Equipment.equipment_type == equipment_type)
#
#     # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and
#
#     if len(filters) >= 2:
#         query_filter = and_(*filters)
#     else:
#         query_filter = filters[0] if filters else None
#
#     if query_filter is not None:
#         equipment_info = db.session.query(
#             Equipment.id, Equipment.equipment_type,
#             Equipment.manufacturer_type, Equipment.equipment_name,
#             Equipment.equipment_ip, Equipment.equipment_uname,
#             Equipment.equipment_password, Equipment.equipment_aisles,
#             Equipment.equipment_codetype, Equipment.user_status,
#             Equipment.create_time,
#         ).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
#     else:
#         equipment_info = db.session.query(
#             Equipment.id, Equipment.equipment_type,
#             Equipment.manufacturer_type, Equipment.equipment_name,
#             Equipment.equipment_ip, Equipment.equipment_uname,
#             Equipment.equipment_password, Equipment.equipment_aisles,
#             Equipment.equipment_codetype, Equipment.user_status,
#             Equipment.create_time,
#         ).paginate(page=page, per_page=per_page, error_out=False)
#
#     # 连表查询获取模型应用数据列表
#     equipment_list = [{
#         'id': i.id, 'equipment_type': i.equipment_type,
#         'manufacturer_type': i.manufacturer_type,
#         'equipment_name': i.equipment_name,
#         'equipment_ip': i.equipment_ip,
#         'equipment_uname': i.equipment_uname,
#         'equipment_password': i.equipment_password,
#         'equipment_aisles': i.equipment_aisles,
#         'equipment_codetype': i.equipment_codetype,
#         'user_status': i.user_status,
#         'create_time': i.create_time,
#     } for i in equipment_info.items]
#
#     # 构建返回的 JSON
#     response_data = {
#         'total_items': equipment_info.total,
#         'total_pages': equipment_info.pages,
#         'current_page': equipment_info.page,
#         'per_page': per_page,
#         'data': equipment_list,
#     }
#
#     return jsonify({'code': 200, 'msg': '查询成功', 'data_list': response_data})


# 设备数据展示接口 （新） 录像机父子
@model_view.route('/equipment_show', methods=['GET'])
def equipment_show():

    # '设备id'
    equipment_name = request.args.get('equipment_name', None)
    # '设备类型' ('摄像头','录像机')
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
                Equipment.create_time,Equipment.parent_id
            ).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
        else:
                equipment_info = db.session.query(
                Equipment.id, Equipment.equipment_type,
                Equipment.manufacturer_type, Equipment.equipment_name,
                Equipment.equipment_ip, Equipment.equipment_uname,
                Equipment.equipment_password, Equipment.equipment_aisles,
                Equipment.equipment_codetype, Equipment.user_status,
                Equipment.create_time,Equipment.parent_id
            ).paginate(page=page, per_page=per_page, error_out=False)


        # 连表查询获取模型应用数据列表
        equipment_list = [{
            'id': i.id, 'equipment_type': i.equipment_type,
            'manufacturer_type': i.manufacturer_type,
            'equipment_name': i.equipment_name,
            'equipment_ip': i.equipment_ip,
            'equipment_uname': i.equipment_uname,
            'equipment_password': i.equipment_password,
            'equipment_aisles': i.equipment_aisles,
            'equipment_codetype': i.equipment_codetype,
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
                Equipment.create_time,Equipment.parent_id
            ).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
        else:
                equipment_info = db.session.query(
                Equipment.id, Equipment.equipment_type,
                Equipment.manufacturer_type, Equipment.equipment_name,
                Equipment.equipment_ip, Equipment.equipment_uname,
                Equipment.equipment_password, Equipment.equipment_aisles,
                Equipment.equipment_codetype, Equipment.user_status,
                Equipment.create_time,Equipment.parent_id
            ).paginate(page=page, per_page=per_page, error_out=False)


        # 连表查询获取模型应用数据列表
        equipment_list = [{
            'id': i.id, 'equipment_type': i.equipment_type,
            'manufacturer_type': i.manufacturer_type,
            'equipment_name': i.equipment_name,
            'equipment_ip': i.equipment_ip,
            'equipment_uname': i.equipment_uname,
            'equipment_password': i.equipment_password,
            'equipment_aisles': i.equipment_aisles,
            'equipment_codetype': i.equipment_codetype,
            'user_status': i.user_status,
            'parent_id': i.parent_id,
            'create_time': i.create_time,
        } for i in equipment_info.items]


        # 使用列表推导式筛选设备类型为“录像机”的记录
        equipment_VCR = [record for record in equipment_info.items if record.equipment_type == '录像机']
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




# # 设备删除接口
# @model_view.route('/equipment_delete', methods=['POST'])
# def equipment_delete():
#
#     # '设备id'
#     equipment_id = request.json.get('equipment_id', None)
#     print(equipment_id,'1111')
#
#     # 查找 id 对应数据，如果该id的parent_id为none 查找她下方是否有子类 如果有子类删除  没有删除该值
#
#     # 如果parent_id有值那么只删除该值
#     if equipment_id:
#         equipment = db.session.query(Equipment).filter_by(id=equipment_id).first()
#
#         if equipment:
#             # 检查是否有子类
#             has_children = db.session.query(Equipment).filter_by(parent_id=equipment.id).first()
#
#             if has_children:
#                 # 如果有子类，删除所有子类以及父类
#                 db.session.query(Equipment).filter_by(parent_id=equipment.id).delete()
#                 db.session.query(Equipment).filter_by(id=equipment.id).delete()
#                 db.session.commit()
#                 result = {'code': 200, 'msg': '删除成功'}
#
#             else:
#                 # 如果没有子类，删除当前记录
#                 db.session.delete(equipment)
#                 db.session.commit()
#                 result = {'code': 200, 'msg': '删除成功'}
#         else:
#             result = {'code': 404, 'msg': '未找到对应的设备记录'}
#     else:
#         result = {'code': 400, 'msg': '缺少设备id参数'}
#
#     return jsonify(result)



# 筛选返回接口
@model_view.route('/type_select', methods=['GET'])
def type_select():
    # 矿类型id
    mine_id = request.args.get('mine_id', None)

    # 当选择矿类型id，展示  （矿,矿下监控点,算法）筛选数据
    if mine_id:
        mine_data = db.session.query(Mine.id, Mine.mine_name, ).all()
        mine_list = [{'id': i.id, 'mine_name': i.mine_name, } for i in mine_data]

        equipment_data = db.session.query(Equipment.id, Equipment.equipment_name,Equipment.equipment_type ).filter(
            Equipment.Mine_id == int(mine_id),Equipment.parent_id == None).all()

        equipment_list = [{'id': i.id, 'equipment_name': i.equipment_name,'equipment_type':i.equipment_type } for i in equipment_data]


        # 使用列表推导式筛选设备类型为“录像机”的记录 取录像机的 ID
        vcr_ids = [i['id'] for i in equipment_list if i['equipment_type'] == '录像机']
        # 调用方法数据构造
        equipment_list = children_data(equipment_list, vcr_ids)

        algorithm_data = db.session.query(Algorithm_library.id, Algorithm_library.algorithm_name,Algorithm_library.algorithm_file_name ).all()
        algorithm_list = [{'id': i.id, 'algorithm_name': i.algorithm_name,'algorithm_file_name':i.algorithm_file_name } for i in algorithm_data]


        return jsonify({'code': 200, 'msg': '筛选数据',
                        'mine_list': mine_list,
                        'mine_list_name': '矿数据返回列表',
                        'equipment_list': equipment_list,
                        'equipment_list_name': '监控点数据返回列表',
                        'algorithm_list': algorithm_list,
                        'algorithm_list_name': '算法数据返回列表',
                        'type_list': configs.type_status,
                        'type_list_name': '预警数据返回列表',
                        'equipment_type': configs.equipment_type,
                        'equipment_type_name': '设备类型数据返回列表',
                        'manufacturer_type': configs.manufacturer_type,
                        'manufacturer_type_name': '厂商类型数据返回列表',
                        'equipment_codetype': configs.equipment_codetype,
                        'equipment_codetype_name': '码流类型数据返回列表',
                        })
    # 当不选择的时候展示全部数据
    else:
        mine_data = db.session.query(Mine.id, Mine.mine_name, ).all()
        mine_list = [{'id': i.id, 'mine_name': i.mine_name, } for i in mine_data]

        equipment_data = db.session.query(Equipment.id, Equipment.equipment_name,Equipment.equipment_type).filter(Equipment.parent_id==None).all()
        equipment_list = [{'id': i.id, 'equipment_name': i.equipment_name,'equipment_type':i.equipment_type } for i in equipment_data]

        # 使用列表推导式筛选设备类型为“录像机”的记录 取录像机的 ID
        vcr_ids = [i['id'] for i in equipment_list if i['equipment_type'] == '录像机']
        # 调用方法数据构造
        equipment_list = children_data(equipment_list, vcr_ids)

        algorithm_data = db.session.query(Algorithm_library.id, Algorithm_library.algorithm_name,Algorithm_library.algorithm_file_name ).all()
        algorithm_list = [{'id': i.id, 'algorithm_name': i.algorithm_name,'algorithm_file_name':i.algorithm_file_name } for i in algorithm_data]

        return jsonify({'code': 200, 'msg': '筛选数据',

                        'mine_list': mine_list,
                        'mine_list_name': '矿数据返回列表',
                        'equipment_list': equipment_list,
                        'equipment_list_name': '监控点数据返回列表',
                        'algorithm_list': algorithm_list,
                        'algorithm_list_name': '算法数据返回列表',
                        'type_list': configs.type_status,
                        'type_list_name': '预警数据返回列表',
                        'equipment_type': configs.equipment_type,
                        'equipment_type_name': '设备类型数据返回列表',
                        'manufacturer_type': configs.manufacturer_type,
                        'manufacturer_type_name': '厂商类型数据返回列表',
                        'equipment_codetype': configs.equipment_codetype,
                        'equipment_codetype_name': '码流类型数据返回列表',
                        })


# 选取监控点图片返回接口
@model_view.route('/image_show', methods=['GET'])
def image_show():

    equipment_id = request.args.get('equipment_id',None)
    type = request.args.get('type') if  request.args.get('type') else 0

    equipment_data = db.session.query(Equipment.id,Equipment.equipment_uname,Equipment.equipment_password,Equipment.equipment_ip,Equipment.equipment_type,
                                      Equipment.parent_id,Equipment.code
                                      ).filter(Equipment.id==equipment_id).first()


    if equipment_data:
        result = get_img_from_camera_net('rtsp://{}:{}@{}'.format(
            equipment_data.equipment_uname,equipment_data.equipment_password,equipment_data.equipment_ip
            ) if equipment_data.equipment_type == '摄像头' else get_children_rtsp(equipment_data.parent_id,equipment_data.code),
            equipment_data.id,
            int(type),
        )
        return jsonify(result)
    else:
        return jsonify({'code':400,'msg':'请传递参数'})







# 算法上传接口
@model_view.route('/algorithm_upload', methods=['POST'])
def algorithm_upload():

    # 接收压缩文件
    uploaded_file = request.files.get('files')

    if uploaded_file:
        # file_name为上传文件名字
        file_name = uploaded_file.filename
        # file_path为 路径/文件名字 （结合）
        file_path = os.path.join(FILE_SAVE_PATH, file_name)
        # 文件保存
        uploaded_file.save(file_path.replace('\\', '/'))

        print(str(file_name))
        # 查找算法名称数据相同信息
        name_repeat = db.session.query(Algorithm_library).filter(Algorithm_library.algorithm_file_name==str(file_name)).first()
        print(name_repeat,'111')
        if name_repeat:
            return jsonify({'code': 400, 'msg': '该算法名称已存在'})

        config_data = Algorithm_library(
            algorithm_file_name=file_name if file_name else None,
            # algorithm_name=algorithm_name  if algorithm_name else None,
            # algorithm_type=algorithm_type if algorithm_type else None,
            # algorithm_version=algorithm_version if algorithm_version else None,
        )
        db.session.add(config_data)
        db.session.commit()





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
    conf_name = request.form.get('conf_name', None)  # 名称
    Algorithm_library_id = request.form.get('Algorithm_library_id', None)  # 算法
    Mine_id = request.form.get('Mine_id', None)  # 分析矿名称id
    Equipment_id = request.form.get('Equipment_id', None)  # 分析矿监控点id
    conf_object = request.form.get('conf_object', None)  # 分析对象
    conf_area = request.form.get('conf_area', None)  # 分析区域


    # 参数构建判断是否为空
    params = [conf_name, Algorithm_library_id, Mine_id, Equipment_id,
              conf_object, conf_area]

    if not all(params):
        return jsonify({'code': 400, 'msg': '算法配置数据有未填写项'})

    # 查找算法配置名称数据相同信息
    conf_name_repeat = db.session.query(Algorithm_config).filter(Algorithm_config.Algorithm_library_id==Algorithm_library_id,Algorithm_config.Equipment_id==Equipment_id).first()
    print(conf_name_repeat,'111')
    if conf_name_repeat:
        return jsonify({'code': 400, 'msg': '该监控点算法已存在'})

    # 数据添加
    config_data = Algorithm_config(
        conf_name=conf_name if conf_name else None,
        Algorithm_library_id=int(Algorithm_library_id) if Algorithm_library_id else None,
        Mine_id=int(Mine_id) if Mine_id else None,
        Equipment_id=int(Equipment_id) if Equipment_id else None,
        conf_object=conf_object if conf_object else None,
        # conf_time=conf_time,
        conf_area=conf_area if conf_area else None,
    )
    db.session.add(config_data)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '算法配置数据添加完成'})


# 算法配置数据返回接口
@model_view.route('/algorithm_data_show', methods=['GET'])
def algorithm_data_show():


    # 算法名称
    algorithm_name = request.args.get('algorithm_name')
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

    # 如果存在算法名称参数，将其加入过滤条件
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
            Algorithm_library.id.label('Algorithm_library_id'),
            Algorithm_library.algorithm_name,
            Mine.id.label('Mine_id'),
            Mine.mine_name,
            Equipment.id.label('Equipment_id'),
            Equipment.equipment_name,
            Algorithm_config.conf_object,
            Algorithm_config.conf_time,
            Algorithm_config.conf_area,
        ).join(
            Algorithm_config,
            Algorithm_library.id == Algorithm_config.Algorithm_library_id
        ).join(
            Mine,
            Algorithm_config.Mine_id == Mine.id
        ).join(
            Equipment,
            Algorithm_config.Equipment_id == Equipment.id
        ).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
    else:
        algorithm_res = db.session.query(
            Algorithm_library.id.label('Algorithm_library_id'),
            Algorithm_library.algorithm_name,
            Mine.id.label('Mine_id'),
            Mine.mine_name,
            Equipment.id.label('Equipment_id'),
            Equipment.equipment_name,
            Algorithm_config.conf_object,
            Algorithm_config.conf_time,
            Algorithm_config.conf_area,
        ).join(
            Algorithm_config,
            Algorithm_library.id == Algorithm_config.Algorithm_library_id
        ).join(
            Mine,
            Algorithm_config.Mine_id == Mine.id
        ).join(
            Equipment,
            Algorithm_config.Equipment_id == Equipment.id
        ).paginate(page=page, per_page=per_page, error_out=False)


    # 连表查询获取模型应用数据列表
    algorithm_data = [{
        'Algorithm_library_id': i.Algorithm_library_id,
        'algorithm_name': i.algorithm_name,
        'Mine_id': i.Mine_id,
        'mine_name': i.mine_name,
        'Equipment_id': i.Equipment_id,
        'equipment_name': i.equipment_name,
        'conf_object': i.conf_object,
        'conf_time': i.conf_time,
        'conf_area': i.conf_area,
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




# 算法预警结果展示接口
@model_view.route('/algorithm_result', methods=['GET'])
def algorithm_result():

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
        filters.append(Algorithm_config.conf_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))

    if type_sta:
        filters.append(Algorithm_result.res_type == type_sta)


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
                Algorithm_result.res_type,
                Algorithm_result.res_image,
                Algorithm_result.res_video,
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
            ).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)
    else:
        algorithm_info = db.session.query(
                Algorithm_result.id.label('Algorithm_result_id'),
                Algorithm_result.res_time,
                Mine.id.label('Mine_id'),
                Mine.mine_name,
                Equipment.id.label('Equipment_id'),
                Equipment.equipment_name,
                Algorithm_result.res_type,
                Algorithm_result.res_image,
                Algorithm_result.res_video,
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
            ).paginate(page=page, per_page=per_page, error_out=False)


    # 连表查询获取模型应用数据列表
    algorithm_data = [{
        'Algorithm_result_id': i.Algorithm_result_id,
        'res_time': (i.res_time).strftime("%Y-%m-%d %H:%M:%S"),
        'Mine_id': i.Mine_id,
        'mine_name': i.mine_name,
        'Equipment_id': i.Equipment_id,
        'equipment_name': i.equipment_name,
        'res_type': configs.type_status[int(i.res_type)-1]['value'],
        'res_image': i.res_image,
        'res_video': i.res_video,
        'algorithm_name': i.algorithm_name,
    } for i in algorithm_info.items]

    # response_data = {
    #     'total_items': algorithm_info.total,
    #     'total_pages': algorithm_info.pages,
    #     'current_page': algorithm_info.page,
    #     'per_page': per_page,
    #     'data':  algorithm_data,
    # }


    return jsonify({'code': 200, 'msg': '查询成功', 'data_list': algorithm_data})




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
        filters.append(Algorithm_config.conf_time.between(time_to_gmt_format(start_time), time_to_gmt_format(end_time)))

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
    per_page = request.args.get('per_page', default=15, type=int)

    # 实时视频 rtsp格式返回
    mine_info = db.session.query(Mine.id,Mine.mine_name).all()
    mine_data = [{'mine_id':i.id, 'mine_name':i.mine_name} for i in mine_info]

    equipment_info = db.session.query(Equipment.id,Equipment.equipment_name,Equipment.Mine_id,Equipment.equipment_ip,Equipment.equipment_uname,
                                      Equipment.equipment_password,Equipment.equipment_type,Equipment.parent_id,Equipment.code
                                      ).filter(
        (
            (Equipment.equipment_type == '摄像头')
            |
            (
                (Equipment.parent_id != None)
                & (Equipment.equipment_type == '录像机')
            )
        )
    # ).all()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # result_count = len(equipment_info)
    # print(result_count)

    equipment_data = [{
        'equipment_id':i.id, 'equipment_name':i.equipment_name,
        'mine_id':i.Mine_id,
        # 判断 当为摄像头时返回格式跟录像机返回格式
        'equipment_ip':'rtsp://{}:{}@{}'.format(i.equipment_uname,i.equipment_password,i.equipment_ip) if i.equipment_type == '摄像头' else get_children_rtsp(i.parent_id,i.code),
        'data_now_result':datainfo(i.id,2),
        'data_old_result':datainfo(i.id,1)
    } for i in equipment_info.items]

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
    # return jsonify({'code': 200, 'msg': '查询成功', 'data_list': mine_data})


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

    # 假设前端传递的参数为可能有一个或多个
    filters = []

    # 如果存在算法名称参数，将其加入过滤条件
    if algorithm_file_name:
        filters.append(Algorithm_library.algorithm_file_name.ilike(f"%{algorithm_file_name}%"))

    if algorithm_name:
        filters.append(Algorithm_library.algorithm_name.ilike(f"%{algorithm_name}%"))

    # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and

    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None

    if query_filter is not None:

        # 查询全部数据
        algorithm_data = db.session.query(Algorithm_library).filter(query_filter).paginate(page=page, per_page=per_page, error_out=False)

    else:
        # 查询全部数据
        algorithm_data = db.session.query(Algorithm_library).paginate(page=page, per_page=per_page, error_out=False)

    # 连表查询获取模型应用数据列表
    algorithm_info = [{
        'id': i.id,
        'algorithm_file_name': i.algorithm_file_name,
        'algorithm_name': i.algorithm_name,
        'algorithm_type': i.algorithm_type,
        'algorithm_version': i.algorithm_version,
        'algorithm_status': configs.status[int(i.algorithm_status) - 1]['value'],
        'create_time': (i.create_time).strftime("%Y-%m-%d %H:%M:%S"),
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



# # 模型类别 select 筛选返回
# @model_view.route('/model_type_select', methods=['POST', 'GET'])
# # @jwt_required() # token身份验证
# def model_type_select():
#     model_type = db.session.query(Model_Type).all()
#     model_type_list = convert_folder_to_dict_list(model_type, ['id', 'model_type_name', 'create_time'])
#     return jsonify({'code': 200, 'msg': '查询成功', 'data': model_type_list})


# 模型类别 select 筛选返回
@model_view.route('/model_type', methods=['PUT'])
# @jwt_required() # token身份验证
def model_type():

    res = request.args.get('model_type')
    print(res,'11111')

    return jsonify({'code': 200, 'msg': '查询成功', 'data': []})