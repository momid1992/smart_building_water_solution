from __future__ import division
#import socket
import RPi.GPIO as GPIO
import time, math, sys
import Adafruit_MCP3008

GPIO.setmode(GPIO.BCM)

# Software SPI configuration:
CLK = 11
MISO = 9
MOSI = 10
CS = 8
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
inpt = 27
GPIO.setup(inpt, GPIO.IN)
#host = '192.168.0.109'
#port = 5900
pervious_temp = 0
diff_temp  = 0
pervious_liter = 0
minto = 1
sec = 1
power_energy = 0.0
#s = socket.socket()

#s.connect((host, port))
#print('Connected with: ', host)

####************************************************************************************#####
####                    First Function                                                  #####
####************************************************************************************#####
def printing(flow,liters,minute,temperature, power_energy,new_message, decimalPlaces=2):
    times = 0.1
    new_messages = str(new_message)

    flows = round(flow, decimalPlaces)
    # print('L/min in float value ', flows)
    flow = str(flows)

    new_messagew = raw_input(new_messages+": " + flow)
    print('L/min in float value ', new_messagew)
 #   s.send(str.encode((new_messagew)))
    time.sleep(times)

    literss = round(liters, decimalPlaces)
    # print('Total  liters: ', literss)
    liters = str(literss)
    new_messagew = raw_input(new_messages+ ": "+ liters)
    print('Total  liters: ', new_messagew)
 #   s.send(str.encode(new_messagew))
    time.sleep(times)

    minute = int(minute)
    # print('Minute(s): ', minute)
    minutes = str(minute)
    new_messagew = raw_input(new_messages+ ": "+minutes)
    print('Minute(s): ', new_messagew)
 #   s.send(str.encode(new_messagew))
    time.sleep(times)

    temperature = round(temperature,0)
    temperatures = str(temperature)
    new_messagew = raw_input(new_messages+ ": "+temperatures)
 #   s.send(str.encode(new_messagew))
    time.sleep(times)
    print('Temperature: ', new_messagew)

    power_energy = round(power_energy,decimalPlaces)
    # print('KWs is used: ', power_energy)
    power_energys = str(power_energy)
    new_messagew = raw_input(new_messages+ ": "+ power_energys)
 #   s.send(str.encode(new_messagew))
    print('KWs is used: ', new_messagew)
    time.sleep(times)
    print("")

    time.sleep(times)


    return flow, liters, minute,temperature


####***************************************************************************************####
####                            2nd Function                                               ####
####***************************************************************************************####
def calcus(bytesValues, messages, decimalPlacese=2):
    rate_cnt = 0
    tot_cnt = 0

    gpio_lasts = 0
    # 0-5 pulses per revoluation

    constant = 1
    liter2 = 0

    pulses = 0
    time_zero = time.time()
    while True:

        try:
            message = messages
            print('Messages here ', message)
            time_start = time.time()

            #pulses = 0
            while pulses <= 5:
                gpio_curr = GPIO.input(inpt)
                if gpio_curr != 0 and gpio_curr != gpio_lasts:
                    pulses += 1

                gpio_lasts = gpio_curr

            tot_cnt += 1
            rate_cnt += 1
            time_end = time.time()
            try:

                voltage = ((bytesValues * 3.3)/1023)
                voltageout = 3.3 - voltage
                resisT = float(10000) * float(voltage) / float(voltageout)
                resisT = round(resisT, decimalPlacese)
                A = float(1) / float(298.15)  # in 25 degree celsuis
                B = float(1) / float(3950)  # is the beta value
                lo = math.log(float(resisT) / float(50000))
                kalvin = A + B * lo
                kalvin = 1 / kalvin
                kalvin = round(kalvin, decimalPlacese)
                celsius = kalvin - 273.15
            except:
                print("There is error in temperature sensor or code: ")
                return voltage


            liter = float(tot_cnt * constant)
            diff_time = round((time_end - time_start), 2)
            flow_rate = round((liter - liter2) / diff_time)

            liter2 = liter

            minute = (time_end - time_zero) / 60
            pulses = 0
            seconds = minute*60
            global sec
            global minto  ## Variable for difference temperature and liters
            global current_temp  # verable for current temperature
            current_temp = celsius  # whatever temperature will be here assign to current temperature
            # current_temp = round(current_temp,2)
            if seconds >= sec and current_temp >= 30:
                global pervious_temp
                global diff_temp
                global pervious_liter
                global power_energy
                if current_temp < pervious_temp:
                    diff_temp = -current_temp + pervious_temp
                    print('Power is decreasing 6: ', diff_temp)
                if pervious_temp <= current_temp:
                    diff_temp = current_temp - pervious_temp
                diff_liter = liter - pervious_liter
                pervious_liter = liter
                pervious_temp = current_temp
                sec += 1
                power_energy = (diff_liter * 4 * diff_temp) / 3412
                print('Power is used liter(s)/second: ', power_energy)
            print('Somewhere has problem i think')


            printing(flow_rate, liter, minute, celsius, power_energy, message)
        except KeyboardInterrupt:
            GPIO.cleanup()
            reply = 'crash'

        return voltageout, lo
names = raw_input("Name")

while True:
    values = [0] * 1
    for i in range(2):

        values = mcp.read_adc(0)
    bytess = float(values)
    calcus(bytess, names)

