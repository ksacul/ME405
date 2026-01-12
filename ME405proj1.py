from array import array
from time import sleep_ms
from pyb import Timer, Pin

tim7 = Timer(7, freq=700)           
adc = pyb.ADC(Pin.board.PC0)     
PC1 = Pin(Pin.board.PC1, mode=Pin.OUT_PP)
idx = 0
data = array('H', 500*[0])                #defining array,idx
done = 0
PC1.low() 
sleep_ms(1000)



def tim_cb(tim):
    global data, idx, done
    if idx < 499:
        data[idx] = adc.read()
        idx +=  1
    else:
        tim7.callback(None)               #callback off
        PC1.low()                         #input signal off
        done = 1
        
tim7.callback(tim_cb)                      #callback on
sleep_ms(1) 
PC1.high()                                 #input signal on            

sleep_ms(4000)
for idx,out in enumerate(data):
    print(f"{idx}, {out}") 
