import cv2
import mediapipe as mp
import time

time.sleep(2.0)

# for get keyboard controls
from Quartz.CoreGraphics import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap

def press_key(key_code):
    # Create and post key press event
    key_down = CGEventCreateKeyboardEvent(None, key_code, True)
    CGEventPost(kCGHIDEventTap, key_down)

def release_key(key_code):
    # Create and post key release event  
    key_up = CGEventCreateKeyboardEvent(None, key_code, False)
    CGEventPost(kCGHIDEventTap, key_up)

def press_and_release_key(key_code, duration=0.1):
    """Press and release a key with a specified duration"""
    press_key(key_code)
    time.sleep(duration)
    release_key(key_code)

# draw detection features like hand marks
mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

# for camera
video = cv2.VideoCapture(0)

tipIds = [4, 8, 12, 16, 20]  # Finger tip ids for thumb, index, middle, ring, and pinky fingers

# Track current key state
current_key_pressed = None
last_gesture = None

# Initialize MediaPipe Hands
with mp_hand.Hands(min_tracking_confidence=0.5, max_num_hands=1,
                   min_detection_confidence=0.5) as hands:

    while True:
        # Capture frame-by-frame
        ret, frame = video.read()
        
        if not ret:
            break
            
        # converting bgr to rgb
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # for optimize the performance
        image.flags.writeable = False
        # Process the image and find hands
        results = hands.process(image)
        # for optimize the performance
        # we draw the hands in the image now
        image.flags.writeable = True
        # converting rgb to bgr
        frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        lmList = []

        # Draw hand landmarks on the frame
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # accessing from the first landmark from the hand 
                myHands = results.multi_hand_landmarks[0]
                # loop for landmarks
                for id, lm in enumerate(myHands.landmark):
                    # get the height, width and channel of the video frame 
                    h, w, c = frame.shape
                    # convert the landmark coordinates to pixel values
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # append the landmark id and coordinates to the list
                    lmList.append([id, cx, cy])

                # Draw the hand connections
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hand.HAND_CONNECTIONS)

            fingers = []
            if len(lmList) != 0:
                # we are taking id from lmlist lm list stores the relevant x and y coordinates 1 means x coordinate 2 means y coordinate 
                if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)  

                # for the fingers without thumb 
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                        
            # Count the number of fingers that are open 
            totalFingers = fingers.count(1)
            
            # Determine current gesture
            current_gesture = None
            if totalFingers == 0:
                current_gesture = "brake"
            elif totalFingers == 5:
                current_gesture = "gas"
           
            
            # Only change key state if gesture changed
            if current_gesture != last_gesture:
                # Release any currently pressed key
                if current_key_pressed is not None:
                    release_key(current_key_pressed)
                    current_key_pressed = None
                    print(f"Released key")
                
                # Press new key based on gesture
                if current_gesture == "brake":
                    press_key(123)  # Left arrow key
                    current_key_pressed = 123
                    print("Brake - Key pressed and held")
                elif current_gesture == "gas":
                    press_key(124)  # Right arrow key  
                    current_key_pressed = 124
                    print("Gas - Key pressed and held")
                
                
                last_gesture = current_gesture
            
            # Display current gesture on screen
            if current_gesture == "brake":
                cv2.rectangle(frame, (20, 300), (270, 425), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, "BRAKE", (45, 375), cv2.FONT_HERSHEY_SIMPLEX,
                           2, (255, 255, 255), 5)
            elif current_gesture == "gas":
                cv2.rectangle(frame, (20, 300), (270, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, " GAS", (45, 375), cv2.FONT_HERSHEY_SIMPLEX,
                           2, (255, 255, 255), 5)
           
        
        # Display the resulting frame
        cv2.imshow('Camera Feed', frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release any pressed keys before exit
if current_key_pressed is not None:
    release_key(current_key_pressed)
    print("Released key on exit")

# Release the camera and close all OpenCV windows
video.release()
cv2.destroyAllWindows()