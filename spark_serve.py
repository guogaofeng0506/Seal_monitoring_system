import os ,sys ,re
import time

import pymongo
import findspark
findspark.init()
from pyspark.sql import SparkSession



# def start_spark(appname='Default APP'):
#     name = appname
#     spark = SparkSession.builder.appName(name).getOrCreate()
#     print("Spark 框架启动成功 ！！！ ")
#     return  spark


#添加两个cpu和1g的内存
def start_spark(appname='Default APP',core=2,mem='1g'):
    name = appname
    dmem = mem
    cpu = "local[" +str(core) +"]"
    spark = SparkSession.builder.master(cpu).appName(name).config("spark.driver.memory",dmem).getOrCreate()
    print('加载csv 模块')
    os.environ['PYSPARK_SUBMIT_ARGS'] = 'pyspark --packages com.databricks:spark-csv_2.10:1.4.0'
    print ("Spark 框架启动成功 ！！！ ")
    return  spark



spark = start_spark('APP')

time.sleep(1000)