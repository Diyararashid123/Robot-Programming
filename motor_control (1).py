import RPi.GPIO as GPIO
from time import sleep
from lib.interface import Interface


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


# Initialize and configure the Interface
bot = Interface('/dev/ttyS0')

# Global variable for the position
current_position = 0
x_coord = 0
y_coord = 0

def set_coordinates(x, y):
    global x_coord, y_coord
    x_coord = x
    y_coord = y
# Function to activate the PLC
def set_plc_high():
    GPIO.output(PLC_pin, GPIO.HIGH)

def set_plc_low():
    GPIO.output(PLC_pin, GPIO.LOW)

# Function to activate the claw
def set_claw_high():
    GPIO.output(CLAW_pin, GPIO.HIGH)

def set_claw_low():
    GPIO.output(CLAW_pin, GPIO.LOW)

# Function to control the direction
def move_left():
    GPIO.output(directions, GPIO.LOW)

def move_right():
    GPIO.output(directions, GPIO.HIGH)

# Wait for execution of a command
def wait_for_execution():
    global bot
    index = bot.get_current_queue_index()
    while index == bot.get_current_queue_index():
        sleep(0.1)

# Function to pick an object
def pick_object(x, y):
    global bot
 
    bot.set_point_to_point_command(2, x, y, 25, 0)  # Move to x, y, z, r (2 is mode)

    wait_for_execution()
    set_claw_high()
    sleep(1)
   
    



# Here we are activating the move belt and the directiong of it
def set_roll_band_high():
    GPIO.output(move_belt, GPIO.HIGH)

def set_roll_band_low():
    GPIO.output(move_belt, GPIO.LOW)

def move_left():
    GPIO.output(directions, GPIO.LOW)

def move_right():
    GPIO.output(directions, GPIO.HIGH)

    
def move_belt_for_duration(direction, duration, stop_duration):
    if direction == "right":
        move_right()
    elif direction == "left":
        move_left()
    else:
        return

    set_roll_band_high()
    sleep(duration)
    set_roll_band_low()
    sleep(stop_duration)


order_complete = False

def set_order_complete(value):
    global order_complete
    order_complete = value
     


def is_order_complete():
    print(f"Order status{order_complete}")
    return order_complete
   

x_position = 5

# Function to place an object
def place_object(index):
    global bot, current_position, x_position, order_complete
   
    if is_order_complete():  
        x_position += 25
        set_order_complete(False)
        print(f"X position: {x_position}")
        current_position = 0
   
        
          

    bot.set_arc_command([154, 154, 110, 45], [5, 230, 125, 90])  
    sleep(1)
  
    wait_for_execution()
    bot.set_point_to_point_command(2, x_position, 160 + 25 * current_position, -25, 90) 
    sleep(2) 
  

    wait_for_execution()
    set_claw_low()
    bot.set_point_to_point_command(2, 5, 220, 140, 90)  


    wait_for_execution()
    sleep(1)


    bot.set_arc_command([154, 154, 110, 45], [200, 0, 80, 0])
    set_claw_low()
    
    wait_for_execution()
    
    current_position += 1.1

def main(motor_control_event):
    bot = Interface('/dev/ttyS0')
    move_count_right = 0  
    move_count_left = 5
    move_right_next = True  

    try:
        while True:
           
            if move_right_next and move_count_right < 12:
                move_belt_for_duration("right", 0.5, 3)
                move_count_right += 1
             
                if move_count_right == 10:
                    move_right_next = False
                    move_count_left = 0  

            elif not move_right_next and move_count_left < 10:
                move_belt_for_duration("left", 0.5, 3)
                move_count_left += 1
              
                if move_count_left == 10:
                    move_right_next = True
                    move_count_right = 0
            
            if motor_control_event.is_set():
           
                set_roll_band_low()
                motor_control_event.wait()
                set_roll_band_low()
                set_plc_high()
                pick_object((390-y_coord)*1, -(x_coord-140)*0.7) 
                place_object(current_position)
                sleep(1)
                set_plc_low()
                motor_control_event.clear() 
           
            
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    from threading import Event
    main(Event())
