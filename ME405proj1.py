from array import array                     #import required modules
from time import sleep_ms
from pyb import Timer, Pin

tim7 = Timer(7, freq=700)                   #defining timer
adc = pyb.ADC(Pin.board.PC0)                #defining adc to read output of circuit
PC1 = Pin(Pin.board.PC1, mode=Pin.OUT_PP)   #defining pin for input of circuit
idx = 0                                     #defining index for array
data = array('H', 500*[0])                  #defining empty array to be populated
PC1.low()                                   #make sure input to circuit is low prior to callback
sleep_ms(1000)

def tim_cb(tim):                            #function to be executed by timer channel
    global data, idx
    if idx < 499:                           #if loop to populate list until full
        data[idx] = adc.read()
        idx +=  1
    else:                                   #else after index exceeds 499
        tim7.callback(None)                 #callback off
        PC1.low()                           #input signal off
        
tim7.callback(tim_cb)                       #callback on
sleep_ms(1) 
PC1.high()                                  #input signal on            

sleep_ms(4000)
for idx,out in enumerate(data):             #iterate through array to print (index,output value)
    print(f"{idx}, {out}") 
