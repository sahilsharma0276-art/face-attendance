import cv2

video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Camera not opened")
    exit()

while True:
    ret, frame = video.read()

    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
      