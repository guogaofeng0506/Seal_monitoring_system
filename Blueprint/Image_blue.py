from flask import Response, jsonify, Flask, request, Blueprint
from configs import *
import os
import shutil
from modules.Tables import *


# 递归查找 parent_id 直到为空  向上找
def get_folder_names_recursive(folder_id, folder_names=[]):
    # 查询数据库中指定ID的文件夹信息
    folder = db.session.query(Folder).filter_by(id=folder_id).first()
    if folder is not None:
        folder_names.append(folder.folder_name)  # 将文件夹名字插入到列表
        if folder.folder_parent_id is not None:
            # 如果有父文件夹，继续递归查找
            get_folder_names_recursive(folder.folder_parent_id, folder_names)


# 递归查找 parent_id 直到没有 向下找
def find_folders_with_parent_id(parent_id):
    # 初始化一个空列表用于存储文件夹数据
    folders = []

    # 查询具有特定 folder_parent_id 的数据
    folders_with_parent_id = db.session.query(Folder).filter(Folder.folder_parent_id == parent_id).all()

    for folder in folders_with_parent_id:
        # 将数据添加到列表
        folders.append(folder)

        # 递归查找子文件夹的数据
        child_folders = find_folders_with_parent_id(folder.id)
        folders.extend(child_folders)

    return folders

# 从parent_id为none主节点开始找
def build_tree(data, parent_id=None):
    tree = []
    for item in data:
        if item['folder_parent_id'] == parent_id:
            children = build_tree(data, item['id'])
            if children:
                item['children'] = children
            tree.append(item)
    return tree


# 创建蓝图，对应的register目录
imageblue = Blueprint('imageblue', __name__)


@imageblue.route('/select_type', methods=['GET', 'POST', 'DELETE', 'PUT', 'CATCH'])
def select_type():
    # 获取type类型
    type = request.args.get("type", None)
    # 当tyep 为 1 的时候运行敞车程序
    if int(type) == 1:
        # image_list = DeleteRepeat('static/one/open_car/98')
        image_list = []
        return jsonify({'code': 200, 'list': image_list, 'count': len(image_list)})
    # 当tyep 为 2 的时候运行集装箱程序
    elif int(type) == 2:
        # image_list = main('static/container')
        image_list = []
        return jsonify({'code': 200, 'list': image_list, 'count': len(image_list)})



# # 数据表数据返回接口
# @imageblue.route('/folder_info', methods=['POST','GET'])
# def folder_info():
#     # 查询文件表所有数据
#     folder_res = db.session.query(Folder).all()
#     if folder_res:
#         # 转换为套字典的列表
#         folder_dict_list = convert_folder_to_dict_list(folder_res,['create_time','folder_list','folder_parent_id','folder_name','id'])
#         # 调用方法来寻找节点返回数据
#         folder_dict_list = build_tree(folder_dict_list)
#         print(folder_dict_list)
#
#         return  jsonify({'code': 200, 'data':folder_dict_list})
#     return jsonify({'code': 400, 'msg':'文件表数据为空'})


