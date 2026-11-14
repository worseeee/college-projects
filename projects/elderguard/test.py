import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

print("========== DHT11 硬件诊断 ==========")
print("测试配置：")
print("  - 引脚: GPIO25 (BCM编号) / Pin 22 (BOARD编号)")
print("  - 传感器: DHT11")
print("======================================\n")

# 初始化
dht_device = None

try:
    print("[1/5] 初始化 DHT11 (use_pulseio=False)...")
    dht_device = adafruit_dht.DHT11(board.D25, use_pulseio=False)
    print("✓ 初始化成功\n")
    
    print("[2/5] 等待传感器稳定 (5秒)...")
    time.sleep(5)
    print("✓ 等待完成\n")
    
    print("[3/5] 开始连续读取测试 (10次)...")
    success_count = 0
    
    for i in range(1, 11):
        try:
            print(f"  尝试 {i}/10...", end=" ")
            
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            
            if temperature is not None and humidity is not None:
                print(f"✓ 温度: {temperature:.1f}°C, 湿度: {humidity:.1f}%")
                success_count += 1
            else:
                print("✗ 返回 None")
            
        except RuntimeError as e:
            print(f"✗ 超时: {e}")
        except Exception as e:
            print(f"✗ 异常: {e}")
        
        # 每次读取间隔3秒
        if i < 10:
            time.sleep(3)
    
    print(f"\n成功率: {success_count}/10 ({success_count*10}%)")
    
    if success_count == 0:
        print("\n❌ 完全无法读取，可能的原因：")
        print("   1. DHT11 损坏")
        print("   2. 接线错误")
        print("   3. 供电不足")
        print("   4. 引脚配置错误")
    elif success_count < 5:
        print("\n⚠ 读取不稳定，建议：")
        print("   1. 检查接线是否松动")
        print("   2. 更换数据线")
        print("   3. 增加上拉电阻 (4.7K-10K)")
    else:
        print("\n✓ DHT11 工作正常")
    
    print("\n[4/5] GPIO 状态检查...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.IN)
    
    for i in range(5):
        state = GPIO.input(25)
        print(f"  GPIO25 电平: {state} ({'高' if state else '低'})")
        time.sleep(0.5)
    
    print("\n[5/5] 电压检查建议：")
    print("  用万用表测量：")
    print("    DHT11 VCC 引脚 → 应为 3.3V")
    print("    DHT11 GND 引脚 → 应为 0V")
    print("    DHT11 DATA 引脚空闲时 → 应为 3.3V (上拉)")

except Exception as e:
    print(f"✗ 初始化失败: {e}")

finally:
    if dht_device:
        dht_device.exit()
    GPIO.cleanup()
    print("\n========== 诊断完成 ==========")
