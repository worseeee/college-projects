import cv2
import mediapipe as mp
  
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

while True:

    ret,img=cap.read()

    if ret:
        img = cv2.flip(img,1)
        imgrgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        result = hands.process(imgrgb)
            
        #判断左右手的Index号
        if result.multi_handedness:
            for hand_label in result.multi_handedness:
                print(hand_label)
            
        #获取每个手掌21个点的信息
        if result.multi_hand_landmarks:
            for hand_no, hand_landmarks in enumerate(result.multi_hand_landmarks):
                print("HAND Index:",hand_no)
                print("-----------------------")
            
                for i in range(0,len(mpHands.HandLandmark)):
                    print(i,mpHands.HandLandmark(i).name)
                    print(hand_landmarks.landmark[mpHands.HandLandmark(i).value])
            
        #绘制手掌21个点          
        if result.multi_hand_landmarks:
            for handLms in  result.multi_hand_landmarks:
                mpDraw.draw_landmarks(img,handLms)
            
        cv2.imshow('img',img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()