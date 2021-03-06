import numpy as np
import matplotlib as plt
import serial
import sys
import time

plt.style.use('_mpl-gallery-nogrid')

# This connects to serial
ser = serial.Serial(
    #You might change the PORT corresponding to the assigned by Operative System
    '/dev/cu.usbmodem104742601',  # raspberry: '/dev/ttyUSB1'
    baudrate=115200,
    timeout=0.1)


# Default parameters
ROWS = 48  # Rows of the sensor
COLS = 48  # Columns of the sensor

# Variable declaration
Values = np.zeros((ROWS, COLS))


def RequestPressureMap():
    data = "R"
    ser.write(data.encode())


def activePointsReceiveMap():
    global Values
    matrix = np.zeros((ROWS, COLS), dtype=int)

    xbyte = ser.read().decode('utf-8')

    HighByte = ser.read()
    LowByte = ser.read()
    high = int.from_bytes(HighByte, 'big')
    low = int.from_bytes(LowByte, 'big')
    nPoints = ((high << 8) | low)

    xbyte = ser.read().decode('utf-8')
    xbyte = ser.read().decode('utf-8')
    x = 0
    y = 0
    n = 0
    while(n < nPoints):
        x = ser.read()
        y = ser.read()
        x = int.from_bytes(x, 'big')
        y = int.from_bytes(y, 'big')
        HighByte = ser.read()
        LowByte = ser.read()
        high = int.from_bytes(HighByte, 'big')
        low = int.from_bytes(LowByte, 'big')
        val = ((high << 8) | low)
        matrix[y][x] = val
        n += 1
    Values = matrix
 
def activePointsGetMap():
    xbyte = ''
    if ser.in_waiting > 0:
        try:
            xbyte = ser.read().decode('utf-8')
        except Exception:
            print("Exception")
        if(xbyte == 'N'):
            activePointsReceiveMap()
        else:
            ser.flush()

class Null:
    def write(self, text):
        pass

    def flush(self):
        pass

def getMatrix():
    RequestPressureMap()
    activePointsGetMap()

def printMatrix():
    for i in range(COLS):
        tmp = ""
        for j in range(ROWS):
            tmp = tmp +   hex(int(Values[i][j]))[-1]
        print(tmp)
    print("\n")

def generatePlot(Z):
    fig, ax = plt.subplots()

    ax.contourf(Z, levels=np.linspace(Z.min(), Z.max(), 7))

    plt.show()
   
#Main


while True:
    getMatrix() # This function requests and parses a pressure map in the variable Values    
    printMatrix()
    generatePlot(Values)
    # time.sleep(1)


