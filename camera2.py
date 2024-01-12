import cv2
import pytesseract
import re
from threading import Event
from time import sleep
import time
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
import motor_control
from motor_control import set_order_complete



def detect_text(frame):
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(frame, config=custom_config)
    filtered_text = ''.join(re.findall(r'\b[A-Z]\b', text.upper()))
    return filtered_text

def write_to_log(data, event_type):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{current_time} - {event_type}: {data}\n"
    with open('event_log.txt', 'a') as file:
        file.write(log_entry)

def letter():
    with open('received_letters.txt', 'r') as file:
        data = file.read().replace("\n", "").replace(" ", "")
        letter_array = list(data)
        return letter_array
# find objects in frame and read text on them
def find_objects(frame):
	# table of letters and text to return
	letters_with_pos = []
	roi_x, roi_y, roi_w, roi_h = 80, 70, 250, 135
	
	# region of interest
	roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
	gray_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
	
	binary_frame = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
	
	# hitta konturer
	contours, _ = cv2.findContours(binary_frame,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	for contour in contours:
		x,y,w,h = cv2.boundingRect(contour)
		x += roi_x
		y += roi_y
		
		
		if w * h > 1200 and w*h<2500 and w < 50 and h < 50 and w > 30 and h > 30:
			
			#cv2.rectangle(roi, (x,y), (x+w, y+h), (0, 255, 0), 2)
			
			letter_roi = frame[y:y+h, x:x+w]
			letter_roi = cv2.bitwise_not(letter_roi)
			cv2.rectangle(roi, (x,y), (x+w, y+h), (0, 255, 0), 2)
			
			# find letter at 
			found_letter = detect_text(letter_roi)
			
			#print(f'Text: {found_letter}')
			#print(f'at: {x}, {y}')
			
			tmp = [found_letter, x, y]
			letters_with_pos.append(tmp)
			
			
	cv2.rectangle(frame,(roi_x,roi_y),(roi_w,roi_h), (0, 255, 0), 2)
	
	
	return letters_with_pos
	
global motor_control_event
motor_control_event = Event()


        
def clear_letters():
    with open('received_letters.txt', 'w') as file:
        file.write("")

def main(motor_control_event):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 200)

    frame_counter = 0  # Initialize frame counter
    ocr_frequency = 30  # Process every 30th frame for OCR

    while True:
        target_letters = letter()
        if not target_letters:
            print("Waiting for letters...")
            sleep(1)
            continue
        
        current_letter_index = 0
        is_processing = False

        while current_letter_index < len(target_letters):
            if not is_processing:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame.")
                    break
                
                frame_counter += 1

                # Only process frames based on the OCR frequency
                if frame_counter % ocr_frequency == 0:
                    print(f"Searching for letter: {target_letters[current_letter_index]}")
                    objects = find_objects(frame)
                    for obj in objects:
                        if obj[0].upper() == target_letters[current_letter_index]:
                            print(f"Match found for letter: {obj[0]} at {obj[1]}, {obj[2]}")
                            motor_control.set_coordinates(obj[1], obj[2])
                            motor_control_event.set()
                            write_to_log(obj[0], "Letter Recognized")
                            is_processing = True
                            current_letter_index += 1
                            break

                cv2.imshow("Camera Feed", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            else:
                if not motor_control_event.is_set():
                    is_processing = False
                    # Resetting camera after each letter
              

        clear_letters()
        write_to_log("Order Completed", "Processing")
        print("The order is completed. Waiting for new orders.")
        sleep(10)
        set_order_complete(True)

    cap.release()
    cv2.destroyAllWindows()
    print("Exiting program...")

if __name__ == "__main__":
    main(Event())
