from array import array
from time import sleep_ms
from pyb import Pin

def tim_cb(tim):
    global data, idx
    
    data[idx] = adc.read()
    idx=idx+1
    if idx == (len(data) - 1):
        PC1.low()                         #input signal off
        print(f"{idx}, {data[idx]}")             
        tim7.callback(None)               #callback off
        

data = array('H', 500*[0])                #defining arrays/timers/pins, length of array was 
tim7 = Timer(7, freq=700)                 #from time constant times 5 divided by how long in between each sample
PC1 = Pin(Pin.board.PC1, mode=Pin.OUT_PP)
adc = pyb.ADC(Pin.board.PC0)

tim7.callback(tim_cb)                      #callback on
sleep_ms(1) 
PC1.high()                                 #input signal on            

