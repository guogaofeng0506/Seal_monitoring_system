import requests

# GET请求示例
res = requests.get('http://192.168.14.93:5000/imageblue/aaa', params={'id': 1})
# POST请求示例
res2 = requests.post('http://112.124.2.201:5000/imageblue/select_type/', params={'type1': '1'})

# 打印结果
# print(res.text)
print(res2.text)
