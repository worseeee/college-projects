# 读取图片
# import cv2

# img = cv2.imread("picture.png")
# cv2.imshow("Output",img)
# cv2.waitKey(0)

# 读取视频
# import cv2

# cap = cv2.VideoCapture("video.mp4")
# while True:
#     success, img = cap.read() 
#     cv2.imshow("Video", img)
#     if cv2.waitKey(30) & 0XFF ==ord('q'):
#         break

# 读取摄像头视频流
import cv2

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

while True:
    success, img = cap.read() 
    cv2.imshow("Video", img)
    if cv2.waitKey(1) & 0XFF ==ord('q'):
        break