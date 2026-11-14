# opencv图像处理
# import cv2
# import numpy as np

# img = cv2.imread("picture.png")
# kernel = np.ones((5,5), np.uint8)

# imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# imgBlur = cv2.GaussianBlur(imgGray, (11,11), 0)
# imgCanny = cv2.Canny(img, 120, 120)
# imgDilate = cv2.dilate(imgCanny, kernel, iterations=1)
# imgErode = cv2.erode(imgDilate, kernel, iterations=1)

# cv2.imshow("Original Image", img)
# cv2.imshow("Gray Image", imgGray)
# cv2.imshow("Blurred Image", imgBlur)
# cv2.imshow("Edge Detection", imgCanny)
# cv2.imshow("Image Dilation", imgDilate)
# cv2.imshow("Image Erosion", imgErode)

# cv2.waitKey(0)


# opencv图像操作
# import cv2
# import numpy as np
# img = cv2.imread("picture.png")
# print(img.shape)
# imgResize = cv2.resize(img, (300,300))
# imgCrop = imgResize[0:100,100:200]
# cv2.imshow("Output", img)
# cv2.imshow("Resized  Output", imgResize)
# cv2.imshow("Cropped  Output", imgCrop)
# cv2.waitKey(0)

# 形状和文本
# import cv2
# import numpy as np

# img = np.zeros((512,512,3),np.uint8)

# cv2.line(img,(0,256),(512,256),(200,232,132),3)
# cv2.rectangle(img, (0,0),(250,350),(213,123,23),2)
# cv2.circle(img,(400,50),30,(14,29,195),5)
# cv2.circle(img,(400,150),30,(14,29,195),-5)
# cv2.putText(img, "Bookworm", (0,400), cv2.FONT_HERSHEY_COMPLEX,3,(0,213,51),1)

# cv2.imshow("Output", img)
# cv2.waitKey(0)

# opencv图像扭曲和透视
# import cv2
# import numpy as np
# img = cv2.imread("box.png")
# width, height = 500, 300
# points1 = np.float32([[109,155],[714,51],[75,560],[800,424]])
# points2 = np.float32([[0,0],[width,0],[0,height],[width,height]])
# matrix = cv2.getPerspectiveTransform(points1,points2)
# imgOutput = cv2.warpPerspective(img, matrix, (width, height))
# cv2.imshow("Original", img)
# cv2.imshow("Output", imgOutput)
# cv2.waitKey(0)

# opencv颜色检测
# import cv2
# import numpy as np
# def empty(a):
#     pass
# path = "box.png"
# cv2.namedWindow("Track Bars")
# cv2.resizeWindow("Track Bars",(640,240))
# cv2.createTrackbar("Hue Min", "Track Bars", 34, 179, empty)
# cv2.createTrackbar("Hue Max", "Track Bars", 55, 179, empty)
# cv2.createTrackbar("Sat Min", "Track Bars", 160, 255, empty)
# cv2.createTrackbar("Sat Max", "Track Bars", 255, 255, empty)
# cv2.createTrackbar("Value Min", "Track Bars", 34, 255, empty)
# cv2.createTrackbar("Value Max", "Track Bars", 255, 255, empty)
# while True:
#     img = cv2.imread(path)
#     imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
#     hmin = cv2.getTrackbarPos("Hue Min","Track Bars")
#     hmax = cv2.getTrackbarPos("Hue Max", "Track Bars")
#     smin = cv2.getTrackbarPos("Sat Min", "Track Bars")
#     smax = cv2.getTrackbarPos("Sat Max", "Track Bars")
#     vmin = cv2.getTrackbarPos("Value Min", "Track Bars")
#     vmax = cv2.getTrackbarPos("Value Max", "Track Bars")
#     lower = np.array([hmin,smin,vmin])
#     upper = np.array([hmax,smax,vmax])
#     mask = cv2.inRange(imgHSV,lower,upper)
#     imgResult = cv2.bitwise_and(img,img,mask=mask)
#     cv2.imshow("Original Image", img)
#     cv2.imshow("HSV Image", imgHSV)
#     cv2.imshow("Mask", mask)
#     cv2.imshow("Final Output", imgResult)
#     cv2.waitKey(1)

# opencv轮廓检测
# import cv2
# import numpy as np
# path = "shapes.png"
# img = cv2.imread(path)
# imgContour = img.copy()
# imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# imgBlur = cv2.GaussianBlur(imgGray, (7,7), 1)
# imgCanny = cv2.Canny(imgBlur,100,100)
# contours, hierarchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
# for cnt in contours:
#     area = cv2.contourArea(cnt)
#     print("area: " + str(area))
#     if area>500:
#         cv2.drawContours(imgContour, cnt, -1, (0, 255, 0), 3)
#         para = cv2.arcLength(cnt,True)
#         print("perimeter: " + str(para))
#         approx = cv2.approxPolyDP(cnt,0.02*para,True)
#         print("approximate points: " + str(len(approx)))
# cv2.imshow("Contour Detection",imgContour)
# cv2.waitKey(0)

# opencv人脸检测
import cv2
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
img = cv2.imread("people.jpg")
imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
faces = faceCascade.detectMultiScale(imgGray,1.1,39)
for (x,y,w,h) in faces:
    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    cv2.putText(img, "face",(x,y-5),cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,255,0),1)
    cv2.imshow("Face Detection",img)
cv2.waitKey(0)

# opencv摄像头视频流人脸检测
# import cv2
# import numpy as np
# cap = cv2.VideoCapture(0)
# cap.set(3,640)
# cap.set(4,480)
# faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
# while True:
#     success, img = cap.read()
#     imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#     faces = faceCascade.detectMultiScale(imgGray,1.1,39)
#     for (x,y,w,h) in faces:
#         cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
#         cv2.putText(img, "face",(x,y-10),cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,255,0),1)
#     cv2.imshow("Output",img)
#     if cv2.waitKey(1) & 0xFF==ord('q'):
#         break