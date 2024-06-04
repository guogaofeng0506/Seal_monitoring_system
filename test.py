# # import os
# # import stat
# # import time
# # import traceback
# #
# # import paramiko as pm
# #
# #
# #
# # # ------获取远端linux主机上指定目录下的子目录------
# # def get_remote_dirs(sftp, remote_folder):
# #     # 保存所有文件的列表
# #     remote_file_list = []
# #     # 获取当前指定目录下的所有目录及文件，包含属性值
# #     result = sftp.listdir_attr(remote_folder)
# #
# #     if result:
# #         for file in result:
# #             # remote_folder目录中每一个文件或目录的完整路径
# #             file_path = remote_folder + '/' + file.filename
# #
# #             # 如果是目录，则在列表中添加该目录
# #             if stat.S_ISDIR(file.st_mode):
# #                 remote_file_list.append(file_path)
# #
# #         remote_file_list.sort()  # 列表内元素顺序排队
# #
# #     return remote_file_list
# #
# #
# # # ------获取远端linux主机上指定目录及其子目录下的所有文件------
# # def get_remote_files(sftp, remote_path):
# #     # 保存所有文件的列表
# #     remote_file_list = []
# #     # 获取当前指定目录下的所有目录及文件，包含属性值
# #     result = sftp.listdir_attr(remote_path)
# #
# #     if result:
# #         for file in result:
# #             # remote_folder目录中每一个文件或目录的完整路径
# #             file_path = remote_path + '/' + file.filename
# #
# #             # 如果是目录，则递归处理该目录，这里用到了stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
# #             if stat.S_ISDIR(file.st_mode):
# #                 remote_file_list.extend(get_remote_files(sftp, file_path))
# #
# #             else:
# #                 remote_file_list.append(file_path)
# #
# #         remote_file_list.sort()  # 列表内元素顺序排队
# #
# #     return remote_file_list
# #
# #
# # # 获取下级文件/文件夹路径
# # def get_second_path(first_path):
# #     second_mame_list = os.listdir(first_path)  # 二级文件夹名称列表
# #     second_count = len(second_mame_list)  # 二级文件夹数
# #     second_path_list = []
# #     for i in range(second_count):
# #         second_name = second_mame_list[i]  # 二级文件夹名称
# #         # if second_name >= '000000175.jpg' and second_name <= '000000995.jpg':
# #         second_path = os.path.join(first_path, second_name)  # 二级文件夹路径
# #         second_path_list.append(second_path)
# #     second_path_list.sort()
# #     return second_path_list  # 返回二级文件路径列表
# #
# #
# # def timed(sftp, remote_path, local_dir):
# #
# #     while True:
# #
# #         # 获取远端linux主机上指定目录及其子目录下的所有文件
# #         remote_folder = remote_path.replace('/' + remote_path.split('/')[-1], '')
# #         remote_folder_list = get_remote_dirs(sftp, remote_folder)
# #
# #         if remote_path in remote_folder_list:
# #             remote_file_list = get_remote_files(sftp, remote_path)
# #
# #             if remote_file_list:
# #                 # 依次get每一个文件
# #                 for remote_file in remote_file_list:
# #
# #                     split_str = remote_path.split('/')[-1]
# #                     file_path = remote_file.split(split_str)[-1]
# #                     local_file = local_dir +'/' + split_str + file_path
# #
# #                     local_folder = local_file.replace(local_file.split('/')[-1], '')
# #                     if not os.path.exists(local_folder):
# #                         os.makedirs(local_folder)
# #
# #                     if not os.path.exists(local_file):
# #                         sftp.get(remote_file, local_file)  # 下载
# #                         print('%s has got as %s' % (remote_file, local_file))
# #                         try:
# #                             sftp.remove(remote_file)  # 删除
# #                             print('%s has removed' % remote_file)
# #                         except:
# #                             traceback.print_exc()
# #                             print('-' * 100)
# #                             continue
# #             # else:
# #             #     time.sleep(1)
# #
# #
# # def main():
# #
# #     # 获取transport传输实例, 远端服务器 ip + 端口号
# #     remote_ip = '192.168.14.103'
# #     tran = pm.Transport((remote_ip, 22))
# #     # 连接远端服务器，用户名，密码
# #     tran.connect(username='root', password='xspeed')
# #     # 获取sftp实例
# #     sftp = pm.SFTPClient.from_transport(tran)
# #
# #     remote_path = '/var/model_algorithm_package/output/'  # 远端待下载目录
# #     local_dir = '.'  # 本地下载文件所在目录
# #
# #     print('remote_ip:', remote_ip)
# #     print('remote_path:', remote_path)
# #     print('local_dir:', local_dir)
# #
# #     # # 若路径字符串最后有'/'，则删除
# #     # if remote_path[-1] == '/':
# #     #     remote_path = remote_path[0:-1]
# #     # # 若路径字符串最后有'/'，则删除
# #     # if local_dir[-1] == '/':
# #     #     local_dir = local_dir[0:-1]
# #
# #     timed(sftp, remote_path, local_dir)  # 下载后保存为视频
# #
# #
# # if __name__ == '__main__':
# #     main()
# # -*- coding: gbk -*-
# import datetime
#
import cv2
import numpy as np
import os
import random
import pymysql
import copy
import ctypes
import time
import paramiko

from ctypes import *
from dbutils.pooled_db import PooledDB
# 数据库连接池
pool = PooledDB(pymysql, maxconnections=10, host='192.168.14.93', user='root', password='abc123',
                database='seal_system',
                charset='utf8')

conn = pool.connection()
cursor = conn.cursor()

# # 查询数据 cursor.lastrowid = id
# sql = " SELECT `res_temperature` from t_algorithm_result WHERE  id = '%s' " % (12609)
# cursor.execute(sql)
# tem_data = cursor.fetchone()[0]
# print(tem_data)
# if tem_data == []:
#     print(123)

sql = (
    "SELECT c.id AS Mine_id, c.mine_name, d.id AS Equipment_id, "
    "d.equipment_name, d.equipment_type, d.equipment_ip, d.equipment_uname, d.equipment_password, d.code, d.parent_id, "
    "a.id AS Conf_id, a.Algorithm_library_id, a.conf_area, e.id AS test_type_id, e.test_type_ename, "
    "b.algorithm_status, b.algorithm_path, b.algorithm_name,b.algorithm_type_list,b.algorithm_trade_type,"
    "d.flower_frames,a.status,a.conf_name,"
    "a.shield_status,a.tem_conf_area,a.tem_frames,a.draw_type,a.confidence "
    "FROM `t_algorithm_config` AS a "
    "JOIN `t_algorithm_library` AS b ON a.Algorithm_library_id = b.id "
    "JOIN `t_mine` AS c ON a.Mine_id = c.id "
    "JOIN `t_equipment` AS d ON a.Equipment_id = d.id "
    "JOIN `t_algorithm_test_type` AS e ON a.Algorithm_test_type_id = e.id "
    "WHERE b.algorithm_status = 1 and a.status = 1 and b.algorithm_trade_type = 2;"
)

cursor.execute(sql)

# 获取查询结果集的列名
columns = [i[0] for i in cursor.description]

results = cursor.fetchall()
print(results)
#
# # 构建字典列表
# result_dict_list = [dict(zip(columns, i)) for i in results]
# import redis
# r = redis.Redis(host='localhost',port=6379,db=1)
#
# print(result_dict_list,)
# for i in result_dict_list:
#     print(eval(i['algorithm_type_list']))

# names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', \
#          'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', \
#          'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', \
#          'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', \
#          'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', \
#          'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', \
#          'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', \
#          'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', \
#          'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', \
#          'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
#          'toothbrush']
#
# print(names)

# yyyyyyyyhhhhhhhhhh