# 摄像头视频捕获
# import cv2

# cap = cv2.VideoCapture(0)
# cap.set(3,640)
# cap.set(4,480)

# while True:
#     success, img = cap.read() 
#     cv2.imshow("Video", img)
#     if cv2.waitKey(1) & 0XFF ==ord('q'):
#         break

# 加入FPS计算
# import cv2
# import time

# cap = cv2.VideoCapture(0)
# cap.set(3,640)
# cap.set(4,480)

# while True:
#     start_time = time.time()
#     success, img = cap.read() 
#     if (time.time() - start_time) > 0:
#         fpsInfo = "FPS: " + str(1.0 / (time.time() - start_time))  # FPS = 1 / time to process loop
#         font = cv2.FONT_HERSHEY_DUPLEX
#         cv2.putText(img, fpsInfo, (10, 20), font, 0.4, (255, 255, 255), 1)
#     cv2.imshow("Video", img)
#     if cv2.waitKey(1) & 0XFF ==ord('q'):
#         break

# 录制视频
# import cv2
# import time

# cap = cv2.VideoCapture(0)
# cap.set(3,640)
# cap.set(4,480)

# vid_cod = cv2.VideoWriter_fourcc(*'XVID')
# vid_output = cv2.VideoWriter("cam_video.mp4", vid_cod, 20.0, (640,480))

# while True:
#     start_time = time.time()
#     success, img = cap.read() 

#     if (time.time() - start_time) > 0:
#         fpsInfo = "FPS: " + str(1.0 / (time.time() - start_time))  # FPS = 1 / time to process loop
#         font = cv2.FONT_HERSHEY_DUPLEX
#         cv2.putText(img, fpsInfo, (10, 20), font, 0.4, (255, 255, 255), 1)

#         cv2.imshow("Video", img)
#         vid_output.write(img)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         vid_output.release()
#         break

# # close the already opened camera, and the video file
# vid_output.release()
# cv2.destroyAllWindows()

# 摄像头捕获并保存图片
import cv2

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

while True:
    success, img = cap.read() 
    cv2.imshow("Video", img)
    key = cv2.waitKey(1)
    if key == ord('z'):
        cv2.imwrite('usbcapture.jpg', img)
    if key == ord('q'):
        break
# close the already opened camera
cap.release()
cv2.destroyAllWindows()