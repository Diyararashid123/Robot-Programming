import RPi.GPIO as GPIO
from time import sleep
from lib.interface import Interface
from camera2 import motor_control_event
# GPIO pin setup
move_belt = 17
directions = 22
CLAW_pin = 23
PLC_pin = 18




GPIO.setmode(GPIO.BCM)
GPIO.setup(PLC_pin, GPIO.OUT)
GPIO.setup(CLAW_pin, GPIO.OUT)
GPIO.setup(move_belt, GPIO.OUT)
GPIO.setup(directions, GPIO.OUT)

#Good luck !!!!!!!!!!!!!!!!!!!!!
# For reseting the claw use the PLC_pin instead of move_belt and tehn Claw_pin insted of directions and that will make the robots claw system resets and now u can run the main program again

# Here we are activating the move belt and the directiong of it
def set_roll_band_high():
    GPIO.output(move_belt, GPIO.HIGH)

def set_roll_band_low():
    GPIO.output(move_belt, GPIO.LOW)

def move_left():
    GPIO.output(directions, GPIO.LOW)

def move_right():
    GPIO.output(directions, GPIO.HIGH)


def main():


   
    
    try:
        while True:
            set_roll_band_high()
            move_left()
            sleep(1)
            move_right()
            set_roll_band_low()
            
            
            
           
            
       

            
            
         
            
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
   
    main()
