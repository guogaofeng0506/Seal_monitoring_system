from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
import os
import dbutils.steady_db
from configs import *
from modules.Tables import *
from sqlalchemy import and_,func,update
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from Video_Quality_Diagnosis.VQD import *
from sqlalchemy.exc import SQLAlchemyError


# 创建蓝图
scheduler_task = Blueprint('scheduler_task', __name__)

# 质量诊断数据写入
def perform_diagnostic_task(data):
    try:
        # 开始事务
        with db.session.begin_nested():

            # 查找并批量移动现有数据到诊断历史表
            existing_data = db.session.query(Diagnosis_data).all()

            if existing_data:
                # 创建要插入到历史表中的数据列表
                history_entries = [
                    Diagnosis_data_old(
                        equipment_id=entry.equipment_id,
                        equipment_ip=entry.equipment_ip,
                        equipment_name=entry.equipment_name,
                        vcr_ip=entry.vcr_ip,
                        diagnosis_type=entry.diagnosis_type,
                        db101=entry.db101, db102=entry.db102, db103=entry.db103,
                        db104=entry.db104, db105=entry.db105, db106=entry.db106,
                        db107=entry.db107, db108=entry.db108, db109=entry.db109,
                        db110=entry.db110, db111=entry.db111, db112=entry.db112,
                        db113=entry.db113, db114=entry.db114, db115=entry.db115,
                        create_time=entry.create_time
                    )
                    for entry in existing_data
                ]

                # 批量保存到历史表
                db.session.bulk_save_objects(history_entries)

            # 清空现有的诊断数据表
            db.session.query(Diagnosis_data).delete()

            # 准备批量插入的新诊断数据
            new_entries = [
                Diagnosis_data(
                    equipment_id=i[0], equipment_ip=i[1], equipment_name=i[2], vcr_ip=i[3],
                    diagnosis_type=i[4], db101=i[5], db102=i[6], db103=i[7],
                    db104=i[8], db105=i[9], db106=i[10], db107=i[11],
                    db108=i[12], db109=i[13], db110=i[14], db111=i[15],
                    db112=i[16], db113=i[17], db114=i[18], db115=i[19],
                    create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                for i in data
            ]
            # 批量插入新的诊断数据
            db.session.bulk_save_objects(new_entries)

        # 提交事务
        db.session.commit()
        print('诊断数据上传完成！')

    except SQLAlchemyError as e:
        # 回滚事务
        db.session.rollback()
        print(f'发生错误: {str(e)}')

# 质量诊断数据写入
# def perform_diagnostic_task(data):
    #
    # # 查找诊断数据表，将诊断数据表数据写入诊断历史表
    # db.session.query(Diagnosis_data).all()
    # # 清空诊断数据表
    #
    # # 数据插入诊断数据表
    # for i in data:
    #     res = Diagnosis_data(
    #         equipment_id=i[0],equipment_ip=i[1],equipment_name=i[2],vcr_ip=i[3],
    #         diagnosis_type=i[4],db101=i[5],db102=i[6],db103=i[7],
    #         db104=i[8],db105=i[9],db106=i[10],db107=i[11],
    #         db108=i[12],db109=i[13],db110=i[14],db111=i[15],
    #         db112=i[16],db113=i[17],db114=i[18],db115=i[19],
    #         create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     )
    #     db.session.add(res)
    #     db.session.commit()
    # print('诊断数据上传完成！')



# 质量诊断运行（定时任务设置）
def run_task(task_id,task_name,task_interval_seconds,time_type,rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status):
    print('----------------------------------------------------------------------------------------')
    details = [
        f"当前任务id为: {task_id}",
        f"当前任务名称为: {task_name}",
        f"当前时间为: {task_interval_seconds}",
        f"时间类型: {time_type}",
        f"rtsp: {rtsp_list}",
        f"类型: {diagnosis_type_list}",
        f"备注: {scheduled_concent}",
        f"状态: {scheduled_status}"
    ]
    print("\n".join(details))
    try:
        print(f"运行任务: {task_name} 于 {datetime.now()}")
        # 手动创建应用上下文
        res = VQD.run(eval(rtsp_list), eval(diagnosis_type_list))
        print(res, '诊断数据')
        # 在函数内部导入 app
        from main import app
        # 调用任务的处理函数
        with app.app_context():
            perform_diagnostic_task(res)
        print('----------------------------------------------------------------------------------------')
    except Exception as e:
        print(f"运行任务时发生异常: {e}")

# # 注册定时任务启动的 before_first_request (before_app_first_request)钩子
# @scheduler_task.before_app_first_request
# def setup_scheduler_tasks():
#     try:
#         # 查询数据库获取所有定时任务配置
#         tasks = db.session.query(ScheduledTask).all()
#         tasks_data = convert_folder_to_dict_list(tasks,['id','name','interval_seconds'])
#         for task in tasks_data:
#             job_id = f"task_{task['id']}"
#             name = f"task_{task['name']}"
#             interval_seconds = int(task['interval_seconds'])
#
#             # 添加定时任务到 APScheduler
#             scheduler = current_app.apscheduler
#             scheduler.add_job(
#                 id=job_id,
#                 func=run_task,
#                 args=[job_id, name, interval_seconds],
#                 trigger='interval',
#                 seconds=interval_seconds,
#             )
#
#             print(f"已添加定时任务: {name}，触发间隔: {interval_seconds} 秒")
#
#     except Exception as e:
#         print(f"初始化定时任务时发生异常: {e}")


# 定时任务添加
@scheduler_task.route('/add_task', methods=['POST'])
def add_task():

    name = request.form.get('name') # 任务名称
    interval_seconds = request.form.get('interval_seconds') # 任务执行的时间间隔
    time_type = request.form.get('time_type') # 时间类型
    rtsp_list = request.form.get('rtsp_list') # rtsp流列表内容
    diagnosis_type_list = request.form.get('diagnosis_type_list') # 诊断类型列表id
    scheduled_concent = request.form.get('scheduled_concent') # 备注
    scheduled_status = request.form.get('scheduled_status') # 状态 1 启用 0禁用


    # 当没有获取到 name（任务名称） 或者 interval_seconds（任务名称）
    if not name or not interval_seconds:
        return jsonify({'code':400,'msg':'缺少必要的参数'})

    new_task = ScheduledTask(name=name, interval_seconds=interval_seconds,time_type=time_type,
                             rtsp_list = rtsp_list,
                             diagnosis_type_list = diagnosis_type_list,
                             scheduled_concent = scheduled_concent,
                             scheduled_status = scheduled_status,
                             create_time=datetime.now())
    db.session.add(new_task)
    db.session.commit()

    scheduler = current_app.apscheduler
    job_id = f"task_{new_task.id}"

    # 当任务类型为启用的时候运行
    if int(scheduled_status) == 1:

        if time_type == 'seconds':
            scheduler.add_job(id=job_id, func=run_task, args=[new_task.id, new_task.name,
                                                              new_task.interval_seconds,
                                                              new_task.time_type,
                                                              new_task.rtsp_list,
                                                              new_task.diagnosis_type_list,
                                                              new_task.scheduled_concent,
                                                              new_task.scheduled_status,
                                                              ],
                              trigger='interval', seconds=int(interval_seconds))

        elif time_type == 'minutes':
            scheduler.add_job(id=job_id, func=run_task, args=[new_task.id, new_task.name,
                                                              new_task.interval_seconds,
                                                              new_task.time_type,
                                                              new_task.rtsp_list,
                                                              new_task.diagnosis_type_list,
                                                              new_task.scheduled_concent,
                                                              new_task.scheduled_status,
                                                              ],
                              trigger='interval', minutes=int(interval_seconds))

        elif time_type == 'hours':
            scheduler.add_job(id=job_id, func=run_task, args=[new_task.id, new_task.name,
                                                              new_task.interval_seconds,
                                                              new_task.time_type,
                                                              new_task.rtsp_list,
                                                              new_task.diagnosis_type_list,
                                                              new_task.scheduled_concent,
                                                              new_task.scheduled_status,
                                                              ],
                              trigger='interval', hours=int(interval_seconds))

        elif time_type == 'days':
            scheduler.add_job(id=job_id, func=run_task, args=[new_task.id, new_task.name,
                                                              new_task.interval_seconds,
                                                              new_task.time_type,
                                                              new_task.rtsp_list,
                                                              new_task.diagnosis_type_list,
                                                              new_task.scheduled_concent,
                                                              new_task.scheduled_status,
                                                              ],
                              trigger='interval', days=int(interval_seconds))

        elif time_type == 'weeks':
            scheduler.add_job(id=job_id, func=run_task, args=[new_task.id, new_task.name,
                                                              new_task.interval_seconds,
                                                              new_task.time_type,
                                                              new_task.rtsp_list,
                                                              new_task.diagnosis_type_list,
                                                              new_task.scheduled_concent,
                                                              new_task.scheduled_status,
                                                              ],
                              trigger='interval', weeks=int(interval_seconds))
        else:
            return jsonify({"msg": "类型错误", "code": 400})

    return jsonify({"msg": "任务已添加", "task_id": new_task.id})


# 定时任务时间修改
@scheduler_task.route('/update_task', methods=['POST'])
def update_task():
    id = request.form.get('id') # 任务id
    name = request.form.get('name')  # 任务名称
    interval_seconds = int(request.form.get('interval_seconds')) # 任务执行的时间间隔
    time_type = request.form.get('time_type') # 时间类型
    rtsp_list = request.form.get('rtsp_list') # rtsp流列表内容
    diagnosis_type_list = request.form.get('diagnosis_type_list') # 诊断类型列表id
    scheduled_concent = request.form.get('scheduled_concent') # 备注
    scheduled_status = request.form.get('scheduled_status') # 状态 启用 禁用

    task = db.session.query(ScheduledTask).filter(ScheduledTask.id==id).first()
    task_data = convert_to_dict(task,['id','name','interval_seconds','time_type','rtsp_list',

                                      'diagnosis_type_list','scheduled_concent','scheduled_status'])
    if not task_data:
        return jsonify({"msg": "任务不存在",'code':404})

    # 检查 scheduled_status 是否为 '启用' 或 '禁用'
    if scheduled_status != '启用' and scheduled_status != '禁用':
        return jsonify({"msg": "参数错误", 'code': 404})


    scheduler = current_app.apscheduler
    job_id = f"task_{task.id}"

    task.interval_seconds = interval_seconds
    task.time_type = time_type
    task.rtsp_list = rtsp_list
    task.diagnosis_type_list = diagnosis_type_list
    task.scheduled_concent = scheduled_concent
    task.scheduled_status = 1 if scheduled_status == '启用' else 0
    db.session.commit()

    # 检查任务是否存在
    existing_job = scheduler.get_job(job_id)


    # 当任务不存在 and 查找到库里数据为禁用 and 当前传输为启用时候，add
    if not existing_job and int(task_data['scheduled_status']) == 0  and scheduled_status == '启用':

        if time_type == 'seconds':
            scheduler.add_job(id=job_id, func=run_task, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                              trigger='interval', seconds=int(interval_seconds))

        elif time_type == 'minutes':
            scheduler.add_job(id=job_id, func=run_task, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                              trigger='interval', minutes=int(interval_seconds))

        elif time_type == 'hours':
            scheduler.add_job(id=job_id, func=run_task, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                              trigger='interval', hours=int(interval_seconds))

        elif time_type == 'days':
            scheduler.add_job(id=job_id, func=run_task, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                              trigger='interval', days=int(interval_seconds))

        elif time_type == 'weeks':

            scheduler.add_job(id=job_id, func=run_task,args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],
                              trigger='interval', weeks=int(interval_seconds))
    # 当任务存在 and 查找到库里数据为禁用 and 当前传输为启用时候 恢复 + 修改
    elif  existing_job and int(task_data['scheduled_status']) == 0  and scheduled_status == '启用':

            # 恢复任务
            scheduler.resume_job(job_id)

            if time_type == 'seconds':
                scheduler.modify_job(job_id, trigger='interval',
                                     seconds=interval_seconds, args=[task_data['id'], name, interval_seconds, time_type,
                                                                     rtsp_list, diagnosis_type_list, scheduled_concent,
                                                                     scheduled_status], )

            elif time_type == 'minutes':
                scheduler.modify_job(job_id, trigger='interval',
                                     minutes=interval_seconds, args=[task_data['id'], name, interval_seconds, time_type,
                                                                     rtsp_list, diagnosis_type_list, scheduled_concent,
                                                                     scheduled_status], )


            elif time_type == 'hours':
                scheduler.modify_job(job_id, trigger='interval',
                                     hours=interval_seconds, args=[task_data['id'], name, interval_seconds, time_type,
                                                                   rtsp_list, diagnosis_type_list, scheduled_concent,
                                                                   scheduled_status], )


            elif time_type == 'days':
                scheduler.modify_job(job_id, trigger='interval',
                                     days=interval_seconds, args=[task_data['id'], name, interval_seconds, time_type,
                                                                  rtsp_list, diagnosis_type_list, scheduled_concent,
                                                                  scheduled_status], )


            elif time_type == 'weeks':
                scheduler.modify_job(job_id, trigger='interval',
                                     weeks=interval_seconds, args=[task_data['id'], name, interval_seconds, time_type,
                                                                   rtsp_list, diagnosis_type_list, scheduled_concent,
                                                                   scheduled_status], )

            print(f"任务 {job_id} 已恢复")

    # 当查找到库里数据为启用,并且当前传输为禁用时候，update
    elif int(task_data['scheduled_status']) == 1  and scheduled_status == '禁用':

        # 暂停当前任务
        scheduler.pause_job(job_id)
        print('停止当前任务---:',job_id)

    else:

        if not existing_job:
            return jsonify({"msg": "任务已更新", 'code': 200})

        # 不启用停止，进行修改操作
        if time_type == 'seconds':
            scheduler.modify_job(job_id, trigger='interval',
                                 seconds=interval_seconds, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],)

        elif time_type == 'minutes':
            scheduler.modify_job(job_id, trigger='interval',
                                 minutes=interval_seconds, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],)


        elif time_type == 'hours':
            scheduler.modify_job(job_id, trigger='interval',
                                 hours=interval_seconds, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],)


        elif time_type == 'days':
            scheduler.modify_job(job_id, trigger='interval',
                                 days=interval_seconds, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],)


        elif time_type == 'weeks':
            scheduler.modify_job(job_id, trigger='interval',
                                 weeks=interval_seconds, args=[task_data['id'], name, interval_seconds,time_type,
                                                                 rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status],)
        print('修改完成')

    return jsonify({"msg": "任务已更新",'code':200})


# 定时任务删除
@scheduler_task.route('/delete_task', methods=['POST'])
def delete_task():
    id = request.form.get('id',None) # 任务id

    if id:
        try:
            result = eval(id)  # 解析
            if isinstance(result, list):  # 检查是否是一个列表
                for i in eval(id):
                    task = db.session.query(ScheduledTask).filter(ScheduledTask.id == i).first()
                    task_data = convert_to_dict(task, ['id', 'name', 'interval_seconds'])
                    if not task_data:
                        return jsonify({"msg": "任务不存在", 'code': 404})

                    scheduler = current_app.apscheduler
                    job_id = f"task_{task.id}"

                    # 检查任务是否存在
                    existing_job = scheduler.get_job(job_id)
                    if existing_job:
                        scheduler.remove_job(job_id)

                    db.session.delete(task)
                    db.session.commit()
            else:
                return jsonify({"msg": "id不为所传参数校验标准", 'code': 400})
        except Exception as e:
            return jsonify({"msg": "id不为所传参数校验标准", 'code': 400})
    else:
        return jsonify({"msg": "id不为所传参数校验标准", 'code': 400})

    return jsonify({"msg": "任务已删除",'code':200})


# 定时任务展示接口
@scheduler_task.route('/show_task', methods=['GET'])
def show_task():
    # 搜索内容
    name = request.args.get('name')

    # 类型
    time_type = request.args.get('time_type')
    # 状态
    scheduled_status = request.args.get('scheduled_status')

    # 第几页
    page = request.args.get('page', default=1, type=int)
    # 每页条数
    per_page = request.args.get('per_page', default=15, type=int)

    # 假设前端传递的参数为可能有一个或多个
    filters = []

    # 搜索名称
    if name:
        filters.append(ScheduledTask.name.ilike(f"%{name}%"))

    # 如果存在类型参数，将其加入过滤条件
    if time_type:
        filters.append(ScheduledTask.time_type == time_type)

    # 如果存在状态参数，加入过滤条件
    if scheduled_status:
        filters.append(ScheduledTask.scheduled_status == int(scheduled_status))

    # 如果有两个条件，使用 and 连接；如果只有一个条件，不使用 and
    if len(filters) >= 2:
        query_filter = and_(*filters)
    else:
        query_filter = filters[0] if filters else None

    if query_filter is not None:
        res = db.session.query(ScheduledTask).filter(query_filter).paginate(page=page, per_page=per_page,
                                                                          error_out=False)
        # for i in res.items:
        #     print(i)
        #     print(i.scheduled_status,'11111')

    else:
        res = db.session.query(ScheduledTask).paginate(page=page, per_page=per_page,error_out=False)

    res_data = [{
        'id': i.id,
        'name': i.name,
        'interval_seconds': i.interval_seconds,
        'next_run_time': i.next_run_time,
        'create_time': (i.create_time).strftime("%Y-%m-%d %H:%M:%S"),
        'time_type': i.time_type,
        'rtsp_list': i.rtsp_list,
        'diagnosis_type_list': i.diagnosis_type_list,
        'scheduled_concent': i.scheduled_concent,
        'scheduled_status': vcr_status[int(i.scheduled_status) - 1]['value'],

    } for i in res.items]

    response_data = {
        'total_items': res.total,
        'total_pages': res.pages,
        'current_page': res.page,
        'per_page': per_page,
        'data': res_data,
    }

    return jsonify({'code':200,'msg':'查询成功','data':response_data})


# 定时任务状态详情接口
@scheduler_task.route('/task_detail', methods=['GET'])
def task_detail():
    # 任务id
    id = request.args.get('id')

    # 查找当前算法仓运行状态id
    data = db.session.query(ScheduledTask).filter(ScheduledTask.id == id).first()

    if data:
        res_data = {
            'id': data.id,
            'name': data.name,
            'interval_seconds': data.interval_seconds,
            'next_run_time': data.next_run_time,
            'create_time': (data.create_time).strftime("%Y-%m-%d %H:%M:%S"),
            'time_type': data.time_type,
            'rtsp_list': data.rtsp_list,
            'diagnosis_type_list': data.diagnosis_type_list,
            'scheduled_concent': data.scheduled_concent,
            'scheduled_status': vcr_status[int(data.scheduled_status) - 1]['value'],
        }
        return jsonify({'code': 200, 'msg': '查询成功', 'data': res_data})
    else:
        return jsonify({'code': 400, 'msg': '该数据不存在'})



