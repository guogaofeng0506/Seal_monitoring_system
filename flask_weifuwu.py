from flask import Flask, jsonify
import paramiko
import time
import threading

app = Flask(__name__)
running = False
ssh_client = None  # 用于存储 SSH 客户端对象


# 寒武纪运行
def connect_and_start_script():
    global running, ssh_client

    # 检查是否有任务正在执行，如果有，就结束它
    if running and ssh_client:
        print('结束')
        ssh_client.close()
        running = False

    # 云服务器信息
    hostname = '192.168.14.103'
    username = 'root'
    password = 'xspeed'
    directory_path = '/var/model_algorithm_package/hksdk/'
    start_script_path = '/var/model_algorithm_package/hksdk/model_ai.py'

    try:
        # 创建 SSH 客户端
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到云服务器
        ssh_client.connect(hostname=hostname, username=username, password=password)

        # 执行启动脚本并获取交互式 shell
        shell = ssh_client.invoke_shell()
        shell.send(f'python3 {start_script_path}\n')

        # 读取输出
        output = ''
        while True:
            if shell.recv_ready():
                data = shell.recv(1024)
                if data:
                    output_line = data.decode('utf-8', errors='ignore')
                    output += output_line.strip() + '\n'
                    print(output_line)
                else:
                    break  # 当没有数据时退出循环
            else:
                time.sleep(0.1)  # 等待一小段时间继续检查输出

        return output

    except Exception as e:
        return str(e)




# 寒武纪算法模型接口
@app.route('/start_script', methods=['GET'])
def start_script():
    global running
    running = True
    # output = connect_and_start_script()
    # 任务放入进程后台执行
    threading.Thread(target=connect_and_start_script).start()  # 将启动脚本放入后台线程中执行
    running = False
    return jsonify({'code': 200,'msg':'寒武纪算法模型后台线程运行中！'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
