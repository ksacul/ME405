from array import array
from time import sleep_ms
from pyb import Pin
def tim_cb(tim):
    global data, idx
    tim7 = Timer(7, freq=700)
    PC1 = Pin(Pin.board.PC1, mode=Pin.OUT_PP)
    
    PC1.high() #input signal on

    tim7.callback(tim_cb) #callback on
    data = array('H', 1000*[0])
    data[idx] = 47

    sleep_ms(705) #time constant is .141s 
    PC1.low() #input signal off
    tim7.callback(None) #callback off
    print(f"{idx}, {data[idx]}")