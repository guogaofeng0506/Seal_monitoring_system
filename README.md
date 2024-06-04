## Flask 开发模板
## 数据库初始化  (请执行下列命名，进行数据初始化)
```
# $env:FLASK_APP = "main.py"  # windwos 设置环境变量指定启动文件
# export FLASK_APP=main.py    # linux   设置环境变量指定启动文件

# 执行init命令，初始化一个迁移文件夹：
# flask db init

# 把当前的模型添加到迁移文件中：
# flask db migrate

# 迁移文件中对应的数据库操作，真正的映射到数据库中,执行完毕生成migrations文件夹，数据库表生成完成
# flask db upgrade

# 预置数据方法cli
# flask cli insert_predefined_data

```

### 目录说明

```
├── file										上传下载文件放置目录
│   ├── download								下载文件放置目录
│   └── upload									上传文件放置目录
├── main.py										项目启动文件
├── project										项目入口
│   ├── app.py									项目基本设置
│   ├── blueprint_mg							项目蓝图管理目录
│   │   ├── blueprint_mg.py						蓝图注册模块
│   ├── config									项目配置文件目录
│   │   ├── db_config.py						项目数据库连接配置文件
│   │   └── sys_config.py						项目系统配置文件
│   ├── interceptor								拦截器配置目录
│   │   ├── before_req.py						请求拦截器
│   │   ├── global_exception_handler.py			全局异常处理
│   ├── models									模型
│   │   ├── com_models.py						公共模型
│   │   ├── proj_base_model.py					基本模型
│   │   └── user								用户模块相关模型
│   │       └── user_models.py					用户模型
│   ├── modules									项目模块管理
│   │   ├── file_upload_download				文件模块（示例）
│   │   │   ├── file_download.py				文件下载模块（示例）
│   │   │   ├── file_upload.py					文件上传模块（示例）
│   │   ├── __init__.py
│   │   ├── resp_return_way						response 返回方式模块（示例）
│   │   │   └── resp_return_way.py				response 返回方式模块（示例）
│   │   └── user								user 模块开发（示例）
│   │       └── user.py							user 具体模块开发（示例）
│   └── utils									工具目录
│       ├── comm_ret.py							统一 response 封装
│       ├── handle_req_param.py					检查及处理 request 请求参数
│       ├── jwt_auth.py							JWT 编码 及 解码
│       ├── operate_mongodb.py					MongoDB 数据库操作（实例）
│       ├── operate_redis.py					Redis 数据库操作（实例）
│       └── resp_code.py						response 状态码  （其他状态码可自行根据开发需要添加添加）
├── requirements.txt							项目依赖
└── uwsgi.ini									uwsgi 启动配置文件
```

```
说明：示例部分可随项目的开发进行调整
```

----------

### uwsgi 配置说明(注意：实际部署中最好把注释去掉)
```
http = 0.0.0.0:5000
plugin = python3        ; 使用插件-编程语言
chdir = /opt/flask/flask_template    ; 指定项目目录
processes = 4           ; 开启进程数量
threads = 2
enable-threads = true   ; 允许用内嵌的语言启动线程;这将允许你在app程序中产生一个子线程
max-requests = 8192     ; 设置每个进程请求数上限
master = true           ; 允许主线程存在
wsgi-file = ./main.py
callable = app
; home = ./.venv      ; 虚拟环境目录
```

```
启动命令: uwsgi --ini uwsgin.ini
重启命令: uwsgi --reload uwsgi.pid
关闭命令: uwsgi --stop uwsgi.pid
实时状态: uwsgi --connect-and-read uwsgi/uwsgi.status
```

----------

### Python 环境部署方案说明

1. 生成 requirements.txt 文件
```
pip freeze > requirements.txt
```
2. 下载 requirements.txt 文件中的依赖库
```
pip download -r requirements.txt -d ./ --platform=linux --python-version=3.6.5 --no-deps
说明：
    -r               : 指定 requirements.txt 文件
    -d               : 指定 Python 依赖库下载存放的位置
    --platform       : 指定下载哪个平台的 Python 依赖库
    --python-version : 指定下载哪个 Python 版本的依赖
```
3. 将 2 步骤下载的依赖库及 requirements.txt 文件打包上传到需要部署的环境
4. 安装 2 步骤中下载的依赖库
```
pip install --no-index -f ./ -r requirements.txt
说明：
    --no-index  : Ignore package index
    -f          : 已下载依赖库存放位置
    -r          : 指定 requirements.txt 文件
```

### Nginx 配置
```
server {                                                                                        
    listen       80;
    server_name  localhost;
    charset utf-8;

    location /api {
        uwsgi_pass 127.0.0.1:5000;
        include uwsgi_params;
    }
}

```
