import bluetooth,ble_simple_peripheral,time  # type: ignore # noqa: E401
import sys
import motion


from machine import Pin, Timer
from neopixel import NeoPixel  # type: ignore

pin = Pin(12, Pin.OUT)
np = NeoPixel(pin, 8)

colors = [
    (255,   0,   0),  # 红色
    (255, 165,   0),  # 橙色
    (255, 255,   0),  # 黄色
    (  0, 255,   0),  # 绿色
    (  0, 255, 255),  # 青色
    (  0,   0, 255),  # 蓝色
    (128,   0, 128),  # 紫色
    (255, 255, 255),  # 白色
    # (0, 0, 0)
]

# RGB流动彩虹模式
def rgb_flow(tim2):

    global colors

    for i in range(8):
        np[i] = colors[i]

    np.write()

    colors.append(colors.pop(0))
    

tim2 = Timer(2)
tim2.init(period=500, mode=Timer.PERIODIC, callback=rgb_flow)

#构建BLE对象
ble = bluetooth.BLE()

#构建从机对象,广播名称为WalnutPi，名称最多支持8个字符。
ble_client = ble_simple_peripheral.BLESimplePeripheral(ble,name='WPi-Car')

car_sw = 0
rotate_sw = 0

# 接收到主机发来的蓝牙数据处理函数
def on_rx(text):
    global car_sw, rotate_sw

    go_speed = 800
    turn_speed = 500
    
    try:        
        print("RX:",text) #打印接收到的数据,数据格式为字节数组。
        
        #回传数据给主机。
        ble_client.send("I got: ") 
        ble_client.send(text)
        
        hex_data = ['{:02x}'.format(byte) for byte in text]
        
        print(hex_data)
        
        if len(hex_data) > 6:
            
            if (hex_data[6] == '00' or hex_data[7] == '00') and rotate_sw == 0 and car_sw == 0:
                motion.stop()

            """ if hex_data[6] != '00':
                car_sw = 1 """

            if hex_data[6] == '01':  # up
                motion.go_forward(go_speed)
                
            if hex_data[6] == '02':  # down
                motion.go_backward(go_speed)
                
            if hex_data[6] == '04':  # left
                motion.go_left(go_speed)
                
            if hex_data[6] == '08':  # right
                motion.go_right(go_speed)
                
            if hex_data[5] == '04':  # y
                motion.move(700, 200, -400)
                
            if hex_data[5] == '20':  # x
                motion.move(700, -200, 400)

            if hex_data[5] == '08':  # b
                motion.move(500, -600, -100)
                
            if hex_data[5] == '10':  # a
                motion.move(500, 600,  100)
                
            if hex_data[5] == '02':  # select
                
                if rotate_sw == 0:
                    rotate_sw = 1 
                    motion.turn_right(go_speed)

                elif rotate_sw == 1:
                    rotate_sw = 2
                    motion.turn_left(go_speed)
                    
                else:
                    rotate_sw = 0
                    motion.stop()
                    
                print(f"开关小陀螺: {rotate_sw}")
                
            if hex_data[5] == '01':  # start

                print("停止接收主机数据")
                
                if car_sw == 0 :
                    car_sw = 1 
                else:
                    car_sw = 0
                    motion.stop()
                
                print(f"开关电机控制: {car_sw}")
                """ ble_client.on_write(None)
                sys.exit() """


    except (OSError, RuntimeError) as e:
    
        print(f"错误原因：{e}")
        # ble_client.on_write(None)
        sys.exit()

#从机接收回调函数，收到数据会进入on_rx函数。
ble_client.on_write(on_rx)

# while True:
#     
#     time.sleep(0.5)