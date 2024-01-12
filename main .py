# main.py
import threading
import RPi.GPIO as GPIO
import time
import camera2
import motor_control
import cv2
from time import sleep
from lib.interface import Interface

bot = Interface('/dev/ttyS0')

def wait_for_execution():
    global bot
    index = bot.get_current_queue_index()
    while index == bot.get_current_queue_index():
        sleep(0.1)
        
        
def homming():
    bot.set_homing_command(0)
    wait_for_execution()
    sleep(1)

def read_connection_status():
    with open('Connection_status.txt', 'r') as file:
        status = file.read().strip()  
    return status.lower() == 'true' 

def camera_thread(event, stop_event):
    while not stop_event.is_set(): 
        camera2.main(event)
        break
        
def motor_control_thread(event, stop_event):
    while not stop_event.is_set():  
        motor_control.main(event)
        break
        

if __name__ == "__main__":
    homming()


    motor_control_event = camera2.motor_control_event
    stop_event = threading.Event() 

    thread1 = threading.Thread(target=camera_thread, args=(motor_control_event, stop_event))
    thread2 = threading.Thread(target=motor_control_thread, args=(motor_control_event, stop_event))

    thread1.start()
    thread2.start()

    try:
        while True:
            if not read_connection_status(): 
                print("Connection lost. Stopping program.")
    
                stop_event.set()
                GPIO.cleanup()
                cam.release()
                
                
                break
            time.sleep(1)
    finally:
        thread1.join()
        thread2.join()
        print("Program stopped.")
        GPIO.cleanup()
   
