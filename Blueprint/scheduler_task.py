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

# 创建蓝图
scheduler_task = Blueprint('scheduler_task', __name__)



# 质量诊断运行（定时任务设置）
def run_task(task_id,task_name,task_interval_seconds,time_type,rtsp_list,diagnosis_type_list,scheduled_concent,scheduled_status):
    print('当前任务id为:',task_id,'当前任务名称为:',task_name,'当前时间为:',task_interval_seconds,'时间类型:',time_type,
          'rtsp:',rtsp_list,'类型:',diagnosis_type_list,'备注：',scheduled_concent,'状态: ',scheduled_status)
    try:
        print(f"运行任务: {task_name} 于 {datetime.now()}")
        # data1 = [{'id': '1', 'name': '监控点1', 'rtsp': 'rtsp://admin:Pc@12138@192.168.7.77'},
        #          {'id': '2', 'name': '监控点2', 'rtsp': 'rtsp://admin:Pc@12138@192.168.7.31'}]
        # data2 = [{'id': '1', 'name': '场景变化', 'prewarn_threshold': 30, 'warn_threshold': 70},
        #          {'id': '2', 'name': '视频冻结', 'prewarn_threshold': 30, 'warn_threshold': 70}]
        # res = VQD.run(eval(rtsp_list), eval(diagnosis_type_list))
        # print(res)
        print('----------------------------------------------------------------------------------------')
        # 调用任务的处理函数
        # perform_diagnostic_task(task)
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
    id = request.form.get('id') # 任务id

    task = db.session.query(ScheduledTask).filter(ScheduledTask.id==id).first()
    task_data = convert_to_dict(task,['id','name','interval_seconds'])
    if not task_data:
        return jsonify({"msg": "任务不存在",'code':404})

    scheduler = current_app.apscheduler
    job_id = f"task_{task.id}"

    scheduler.remove_job(job_id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({"msg": "任务已删除",'code':200})


# 定时任务展示接口
@scheduler_task.route('/show_task', methods=['GET'])
def show_task():
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
        'create_time': i.create_time,
        'time_type': i.time_type,
        'rtsp_list': i.rtsp_list,
        'diagnosis_type_list': i.diagnosis_type_list,
        'scheduled_concent': i.scheduled_concent,
        'scheduled_status': status[int(i.scheduled_status) - 1]['value'],

    } for i in res.items]

    response_data = {
        'total_items': res.total,
        'total_pages': res.pages,
        'current_page': res.page,
        'per_page': per_page,
        'data': res_data,
    }

    return jsonify({'code':200,'msg':'查询成功','data':response_data})


# 定时任务状态修改接口
@scheduler_task.route('/task_detail', methods=['GET'])
def task_detail():
    # 任务id
    id = request.form.get('id')

    # 查找当前算法仓运行状态id
    data = db.session.query(ScheduledTask).filter(ScheduledTask.id == id).first()

    res_data = {
        'id': data.id,
        'name': data.name,
        'interval_seconds': data.interval_seconds,
        'next_run_time': data.next_run_time,
        'create_time': data.create_time,
        'time_type': data.time_type,
        'rtsp_list': data.rtsp_list,
        'diagnosis_type_list': data.diagnosis_type_list,
        'scheduled_concent': data.scheduled_concent,
        'scheduled_status': status[int(data.scheduled_status) - 1]['value'],

    }


    return jsonify({'code':200,'msg':'修改成功','data':res_data})


