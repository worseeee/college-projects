#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
使用Python通过MQTT协议连接OneNET云平台并定期上报传感器数据
'''

import json
import time
import random
import base64
import hmac
import hashlib
import datetime
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv311
from urllib.parse import quote

# OneNET平台配置参数
# 请替换为您的设备信息
PRODUCT_ID = "3j3CNnOX2C"  # 产品ID
DEVICE_NAME = "mqtt_device_1"  # 设备名称
ACCESS_KEY = 'REPLACE_WITH_YOUR_VALUE'  # 访问密钥

# MQTT连接参数
HOST = "mqtts.heclouds.com"  # OneNET MQTT服务器地址
PORT = 1883  # MQTT端口
KEEP_ALIVE = 60  # 心跳时间间隔(秒)
UPLOAD_INTERVAL = 10  # 数据上报间隔(秒)

# 生成认证信息
def get_token():
    """
    获取OneNET平台Token
    :param exp_time: token过期时间，默认为30天
    :return: token字符串
    """
    version = '2018-10-31'
    res = f"products/{PRODUCT_ID}/devices/{DEVICE_NAME}"
    # 用户自定义token过期时间
    et = str(int(time.time()) + 360000) #注意！注意！注意！此处生成的时间戳只能生效100小时，将            
                                        #大括号里的全部替换为未来时间戳即可
    #et = '1778121036'
    # 签名方法，支持md5、sha1、sha256
    method = 'md5'
    # 对access_key进行decode
    key = base64.b64decode(ACCESS_KEY)
    # 计算sign
    org = et + '\n' + method + '\n' + res + '\n' + version
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    # value 部分进行url编码，method/res/version值较为简单无需编码
    sign = quote(sign, safe='')
    res = quote(res, safe='')
    # token参数拼接
    token = 'REPLACE_WITH_YOUR_VALUE' % (version, res, et, method, sign)
    return token

# 主要程序功能
def main():
    # 生成客户端ID和用户名
    client_id = DEVICE_NAME
    username = PRODUCT_ID
    
    # 获取Token
    token = get_token()
    #token = f"REPLACE_WITH_ONENET_TOKEN"
    
    # 创建MQTT客户端
    client = mqtt.Client(client_id=client_id,protocol=MQTTv311,clean_session=True)
    client.username_pw_set(username, token)
      # 断开连接回调
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print(f"意外断开连接，代码: {rc}")
        else:
            print("已断开连接")
    
    # 发布消息回调
    def on_publish(client, userdata, mid):
        print(f"消息已发送，ID: {mid}")
    
    # 订阅回调
    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"订阅成功，ID: {mid}, QoS: {granted_qos}")

    # MQTT连接回调函数
    def on_connect(client, userdata, flags, rc):
        """
        连接回调函数
        :param client: MQTT客户端
        :param userdata: 用户数据
        :param flags: 连接标志
        :param rc: 连接结果
        """
        result_codes = {
            0: "连接成功",
            1: "协议版本错误",
            2: "无效的客户端ID",
            3: "服务器无法使用",
            4: "用户名或密码错误",
            5: "连接未授权"
        }
        print(f"MQTT连接状态: {result_codes.get(rc, f'未知错误 ({rc})')}")
        if rc == 0:
            # 订阅命令下发主题 - 添加通配符+确保能接收所有命令
            cmd_topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply"
            client.subscribe(cmd_topic)
            print(f"订阅主题成功: {cmd_topic}")
            
            # 订阅服务调用主题 - 添加通配符+确保能接收所有服务调用
            service_topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/"
            client.subscribe(service_topic)
            print(f"订阅主题成功: {service_topic}")
            
            # 订阅属性上报回复主题
            post_reply_topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set"
            client.subscribe(post_reply_topic)
            print(f"订阅主题成功: {post_reply_topic}")

    # 消息接收回调函数
    def on_message(client, userdata, msg):
        """
        消息接收回调函数
        :param client: MQTT客户端
        :param userdata: 用户数据
        :param msg: 消息对象
        """
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        print(f"★★★ 接收到消息 ★★★")
        print(f"主题: {topic}")
        print(f"内容: {payload}")
        
        try:
            # 解析JSON数据
            data = json.loads(payload)
            
            # 处理属性设置命令
            if "property/set" in topic:
                handle_property_set(client, data)
            
            # 处理服务调用
            elif "service" in topic:
                handle_service_call(client, data, topic)
            
            # 处理属性上报回复
            elif "post/reply" in topic:
                if "code" in data and data["code"] == 200:
                    print("√ 属性上报成功")
                else:
                    print(f"× 属性上报失败: {data}")
        
        except json.JSONDecodeError:
            print("消息格式错误，无法解析JSON数据")
        except Exception as e:
            print(f"处理消息时发生错误: {e}")

    # 处理属性设置
    def handle_property_set(client, data):
        """
        处理平台下发的属性设置命令
        :param client: MQTT客户端
        :param data: 属性数据
        """
        if "id" in data and "params" in data:
            msg_id = data["id"]
            params = data["params"]
            
            print(f"接收到属性设置: {params}")
            
            # 回复平台，确认属性已设置
            reply_topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set_reply"
            reply_data = {
                "id": msg_id,
                "code": 200,
                "msg": "success"
            }
            
            client.publish(reply_topic, json.dumps(reply_data))
            print(f"已回复属性设置确认")

    # 处理服务调用
    def handle_service_call(client, data, topic):
        """
        处理平台下发的服务调用
        :param client: MQTT客户端
        :param data: 服务数据
        :param topic: 服务主题
        """
        # 从主题中提取服务ID
        topic_parts = topic.split('/')
        service_id = topic_parts[-1] if len(topic_parts) > 0 else "unknown"
        
        if "id" in data and "params" in data:
            msg_id = data["id"]
            params = data["params"]
            
            print(f"接收到服务调用 {service_id}: {params}")
            
            # 回复平台，确认服务已调用
            reply_topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/{service_id}_reply"
            reply_data = {
                "id": msg_id,
                "code": 200,
                "msg": "success",
                "data": {}
            }
            
            client.publish(reply_topic, json.dumps(reply_data))
            print(f"已回复服务调用确认")
    
    # 设置回调函数
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    
    # 设置调试日志级别
    client.enable_logger()
    
    try:
        # 连接MQTT服务器
        print(f"正在连接 MQTT 服务器 {HOST}:{PORT}...")
        client.connect(HOST, PORT, KEEP_ALIVE)
        
        # 启动网络循环
        client.loop_start()
        print("开始数据上报循环...")
        connection_retry = 0
        while True:
            try:
                # 检查客户端是否连接
                if not client.is_connected():
                    print("MQTT客户端连接已断开，尝试重新连接...")
                    client.reconnect()
                    time.sleep(6)
                    continue
                
                # 生成模拟数据
                temp = random.randint(20, 30) # 模拟温度数据: 20-30°C
                humi = random.randint(0, 100)  # 模拟湿度数据: 0-100%
                
                # 构建上报数据
                msg_id = str(int(time.time()))
                upload_data = {
                    "id": msg_id,  # 消息ID使用当前时间戳
                    "version": "1.0",
                    "params": {
                        "temperature": {"value": temp},
                        "humidity": {"value": humi}
                    }
                }
                
                # 上报主题
                topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post"
                
                # 发布消息 - 使用QoS=1确保消息送达
                result = client.publish(topic, json.dumps(upload_data), qos=1)
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    print(f"发布消息失败，错误码: {result.rc}")
                else:
                    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 已上报数据: 温度={temp}°C, 电量={power}%, 消息ID: {msg_id}")
                
                # 处理MQTT消息循环
                client.loop(timeout=0.1)
                
                # 等待下一次上报
                time.sleep(UPLOAD_INTERVAL)
                connection_retry = 0
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                connection_retry += 1
                print(f"循环中发生错误: {e}")
                if connection_retry > 5:
                    print("多次尝试失败，等待60秒后重试...")
                    time.sleep(60)
                    connection_retry = 0
                else:
                    print(f"等待5秒后重试... (尝试 {connection_retry}/5)")
                    time.sleep(5)
    
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 停止网络循环
        client.loop_stop()
        # 断开连接
        client.disconnect()
        print("已断开连接")

if __name__ == "__main__":
    main()