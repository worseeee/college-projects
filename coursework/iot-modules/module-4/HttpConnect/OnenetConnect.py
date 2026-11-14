import requests
import json
 
# 直连设备属性上报
def report_device_property():
    # 设备信息
    product_id = "J7936UtYPR"
    device_name = "http_device_1"
 
    # 构造topic和protocol参数
    topic = f"$sys/J7936UtYPR/http_device_1/thing/property/post"
    protocol = "http"
 
    # 构造完整的URL
    url = f"https://open.iot.10086.cn/fuse/http/device/thing/property/post?topic={topic}&protocol={protocol}"
 
    # 请求头部信息
    headers = {
        "Content-Type": "application/json",
        "token": 'REPLACE_WITH_YOUR_VALUE'
    }
 
    # 设备属性信息
    body = {
        "id": "123",
        "version": "1.0",
        "params": {
            "temperature": {"value": 30}
        }
    }
 
    # 发送POST请求
    response = requests.post(url, headers=headers, json=body)
    print("Response:", response.json())

# 直连设备属性获取
def request_device_property():
    # 设备信息
    product_id = "J7936UtYPR"
    device_name = "http_device_1"
 
    # 构造完整的URL
    url = f"https://iot-api.heclouds.com/thingmodel/query-device-property?product_id={product_id}&device_name={device_name}"
 
    # 请求头部信息
    headers = {
        "Content-Type": "application/json",
        "authorization": 'REPLACE_WITH_YOUR_VALUE'
    }
 
    # 发送POST请求
    response = requests.get(url, headers=headers)
    print("Response:", response.json())    
 
 # 直连设备物模型获取
def request_device_model():
    # 设备信息
    product_id = "J7936UtYPR"
 
    # 构造完整的URL
    url = f"https://iot-api.heclouds.com/thingmodel/query-thing-model?product_id={product_id}"
 
    # 请求头部信息
    headers = {
        "Content-Type": "application/json",
        "authorization": 'REPLACE_WITH_YOUR_VALUE'
    }
 
 
    # 发送POST请求
    response = requests.get(url, headers=headers)
    print("Response:", response.json())    

# 测试直连设备属性上报
report_device_property()
request_device_property()
request_device_model()