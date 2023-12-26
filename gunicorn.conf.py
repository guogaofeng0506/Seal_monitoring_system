# import multiprocessing
#
# bind = "0.0.0.0:5000"   #绑定的ip与端口
# workers = 3                #进程数

import multiprocessing

bind = "0.0.0.0:5000"  # 绑定的ip与端口
workers = multiprocessing.cpu_count() * 2 + 1  # 进程数，建议设置为 (2 * CPU核数) + 1
