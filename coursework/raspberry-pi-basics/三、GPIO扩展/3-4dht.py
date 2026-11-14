import RPi.GPIO as GPIO
import time

def delayMicrosecond(t):   
    start,end=0,0           
    start=time.time()      
    t=(t-3)/1000000     
    while end-start<t:  
        end=time.time()     

tmp0=[]      # Used to store the read data
data0 = 22   # DHT11 Board
a,b=0,0

def DHT11_0():
    GPIO.setup(data0, GPIO.OUT)  # GPIO OUTPUT   
    GPIO.output(data0,GPIO.HIGH) 
    
    delayMicrosecond(10*1000)   # delay 10ms
    GPIO.output(data0,GPIO.LOW)  
    
    delayMicrosecond(25*1000)   # delay 25ms    
    GPIO.output(data0,GPIO.HIGH) 
    
    GPIO.setup(data0, GPIO.IN) # GPIO INPUT
    
  
    a=time.time()           # Recording cycle start time
    while GPIO.input(data0): 
        b=time.time()       # time the record ended 
        if (b-a)>0.1:       #Determine whether the cycle time exceeds 0.1 seconds to avoid the program from entering an infinite loop and getting stuck 
            break           
        
    a=time.time()
    while GPIO.input(data0)==0:  
        b=time.time()
        if (b-a)>0.1:
            break
                
    a=time.time()
    while GPIO.input(data0): 
        b=time.time()
        if (b-a)>=0.1:
            break   
            
    for i in range(40):         
        a=time.time()
        while GPIO.input(data0)==0:  
            b=time.time()
            if (b-a)>0.1:
                break
                       
        delayMicrosecond(28)    # delay 28 microseconds
            
        if GPIO.input(data0):    # After more than 28 microseconds, it is judged whether it is still at a high level
            tmp0.append(1)       # Record the received bit as 1
                
            a=time.time()
            while GPIO.input(data0): # Loop until the input is low
                b=time.time()
                if (b-a)>0.1:
                    break
        else:
            tmp0.append(0)       # Record the received bit as 0
 
            
while True:
    GPIO.setmode(GPIO.BOARD)      
    GPIO.setwarnings(False)
    del tmp0[0:]                 #delete list
    time.sleep(1)               # Delay 1 second
    
    DHT11_0()
      
    humidity0_bit=tmp0[0:8]       # Delimited list, bits 0 to 7 are humidity integer data
    humidity0_point_bit=tmp0[8:16]# Humidity Decimals
    temperature0_bit=tmp0[16:24]  # Integer temperature
    temperature0_point_bit=tmp0[24:32]    # temperature decimal
    check0_bit=tmp0[32:40]        # check data
       
    humidity0_int=0
    humidity0_point=0
    temperature0_int=0
    temperature0_point=0
      
    check0=0
 
    for i in range(8):          # convert binary to decimal
        humidity0_int+=humidity0_bit[i]*2**(7-i)
        
        humidity0_point+=humidity0_point_bit[i]*2**(7-i)
        
        temperature0_int+=temperature0_bit[i]*2**(7-i)
                
        temperature0_point+=temperature0_point_bit[i]*2**(7-i)
        
        check0+=check0_bit[i]*2**(7-i)
  
    humidity0=humidity0_int+humidity0_point/10
    temperature0=temperature0_int+temperature0_point/10
  
    check0_tmp0=humidity0_int+humidity0_point+temperature0_int+temperature0_point
  
    if check0==check0_tmp0 and temperature0!=0 and temperature0!=0 :  # Determine if the data is normal
        print("Temperature0 is ", temperature0,"C\nHumidity0 is ",humidity0,"%")# Print the temperature and humidity data
        
        #ser.write(temperature0_int)
        temperature00 = str(temperature0)
        humidity00 = str(humidity0)
        #th00 = temperature00 + ";" + humidity00
        #ser.write(th00.encode())
        #ser.write(temperature00.encode())
        
        th = temperature00 + ";" + humidity00 + ";" 
        
    else:
        print("error")
  
    time.sleep(2)
    GPIO.cleanup()
