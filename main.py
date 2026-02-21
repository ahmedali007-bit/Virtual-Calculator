import cv2
from cvzone.HandTrackingModule import HandDetector

# Button class for defining buttons with circular borders
class Button:
    def __init__(self, pos, radius, value):
        self.pos = pos
        self.radius = radius
        self.value = value

    def draw(self, img):
        # Button shadow for a 3D effect
        cv2.circle(img, self.pos, self.radius + 5, (50, 50, 50), cv2.FILLED)

        # Button body
        color1 = (0, 0, 0) if self.value != "=" else (255, 165, 0)
        cv2.circle(img, self.pos, self.radius, color1, cv2.FILLED)

        # Text on button
        color = (255, 255, 255) if self.value not in ['+', '-', '*', '/','AC','DEL','%'] else (0, 255, 0)
        cv2.putText(img, self.value,
                    (self.pos[0] - 20, self.pos[1] + 10),
                    cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

    def checkClick(self, x, y):
        # Check if the given coordinates are inside the circular button
        dist = ((x - self.pos[0])**2 + (y - self.pos[1])**2)**0.5
        return dist < self.radius

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)  # Height
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Create buttons
buttonListValues = [
    ['AC', 'DEL', '%', '='],
    ['7', '8', '9', '*'],
    ['4', '5', '6', '-'],
    ['1', '2', '3', '+'],
    ['00', '0', '.', '/']
]
buttonList = []
radius = 40  # Circular button radius

for row, values in enumerate(buttonListValues):
    for col, value in enumerate(values):
        xpos = 850 + col * 100
        ypos = 200 + row * 100
        buttonList.append(Button((xpos, ypos), radius, value))

# Variables
myEquation = ''
delayCounter = 0

# Loop for live interaction
while True:
    # Capture frame
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Detect hand
    hands, img = detector.findHands(img, flipType=False)

    # Draw calculator display
    cv2.rectangle(img, (800, 70), (1200, 150), (0, 0, 0), cv2.FILLED)  # Display background
    cv2.rectangle(img, (800, 70), (1200, 150), (0, 0, 0), 3)  # White border
    cv2.putText(img, myEquation, (820, 120), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    # Draw buttons
    for button in buttonList:
        button.draw(img)

    # Process hand detection
    if hands:
        lmList = hands[0]['lmList']  # Landmark list of detected hand
        x, y = lmList[8][:2]  # Tip of the index finger
        length, _, img = detector.findDistance(lmList[8][:2], lmList[12][:2], img)  # Distance between index and middle finger

        if length < 50:
            for button in buttonList:
                if button.checkClick(x, y) and delayCounter == 0:
                    value = button.value
                    if value == '=':
                        try:
                            myEquation = str(eval(myEquation))
                        except:
                            myEquation = 'Error'
                    elif value == 'AC':
                        myEquation = ''
                    elif value == 'DEL':
                        myEquation = myEquation[:-1]
                    else:
                        myEquation += value
                    delayCounter = 1

    # Delay counter to avoid multiple clicks
    if delayCounter > 0:
        delayCounter += 1
        if delayCounter > 10:
            delayCounter = 0

    # Show the output
    cv2.imshow("Mini Calculator", img)
    key = cv2.waitKey(1)
    if key == ord('q'):  # Quit when 'q' is pressed
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
