import os
import dbutils.steady_db
from flask import jsonify, request, Blueprint
from configs import *
from modules.Tables import *
from sqlalchemy import and_,func,update
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# 创建数据操作蓝图1，对应的register目录
model_views = Blueprint('model_views', __name__)


# 接口
@model_views.route('/diagnosis_all', methods=['GET'])
def diagnosis_all():

    return jsonify({'code': 200, 'message':'123'})