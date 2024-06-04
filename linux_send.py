import paramiko
import time


# 寒武纪运行
def connect_and_start_script():
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

        # 执行 ls 命令查找目录中的文件
        stdin, stdout, stderr = ssh_client.exec_command(f'ls {directory_path}')
        directory_content = stdout.readlines()  # 读取所有行

        # 输出目录内容
        print(f"目录 {directory_path} 内容:")
        for line in directory_content:
            print(line.strip())

        # 执行启动脚本并获取交互式 shell
        shell = ssh_client.invoke_shell()
        shell.send(f'python3 {start_script_path}\n')

        # # 读取输出
        # start_script_output = ''
        # while True:
        #     if shell.recv_ready():
        #         start_script_output += shell.recv(1024).decode('latin-1')  # 使用 latin-1 编码
        #         print(start_script_output.strip())  # 实时输出
        #     else:
        #         time.sleep(0.1)  # 等待一小段时间继续检查输出

        # 读取输出
        while True:
            if shell.recv_ready():
                data = shell.recv(1024)
                if data:
                    output_line = data.decode('utf-8', errors='ignore')
                    print(output_line.strip())  # 实时输出
                else:
                    break  # 当没有数据时退出循环
            else:
                time.sleep(0.1)  # 等待一小段时间继续检查输出

    except Exception as e:
        print(f"错误: {str(e)}")

    finally:
        # 关闭连接
        if ssh_client:
            ssh_client.close()

if __name__ == "__main__":
    connect_and_start_script()
