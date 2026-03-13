<<<<<<< HEAD
import cv2
import os

# 1) Name input
name = input("Enter name (no spaces): ").strip().replace(" ", "_")

if not name:
    print("Name required. Exiting.")
    exit()

# 2) Dataset folder create (if not exists)
dataset_dir = "dataset"
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)

# 3) Open Camera
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera not working. Close other apps using camera.")
    exit()

count = 0
print("Camera opened. Press 's' to save image, 'q' to quit.")

while True:
    ret, frame = cam.read()

    if not ret:
        print("Failed to read from camera.")
        break

    cv2.imshow("Register Face - Press s to save, q to quit", frame)

    key = cv2.waitKey(1) & 0xFF

    # Save image
    if key == ord('s'):
        filename = f"{name}_{count}.jpg"
        filepath = os.path.join(dataset_dir, filename)
        cv2.imwrite(filepath, frame)
        print("Saved:", filename)
        count += 1

    # Quit
    elif key == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

print("Done. Saved", count, "images.")
=======
import cv2
import os

# 1) Name input
name = input("Enter name (no spaces): ").strip().replace(" ", "_")

if not name:
    print("Name required. Exiting.")
    exit()

# 2) Dataset folder create (if not exists)
dataset_dir = "dataset"
if not os.path.exists(dataset_dir):
    os.makedirs(dataset_dir)

# 3) Open Camera
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera not working. Close other apps using camera.")
    exit()

count = 0
print("Camera opened. Press 's' to save image, 'q' to quit.")

while True:
    ret, frame = cam.read()

    if not ret:
        print("Failed to read from camera.")
        break

    cv2.imshow("Register Face - Press s to save, q to quit", frame)

    key = cv2.waitKey(1) & 0xFF

    # Save image
    if key == ord('s'):
        filename = f"{name}_{count}.jpg"
        filepath = os.path.join(dataset_dir, filename)
        cv2.imwrite(filepath, frame)
        print("Saved:", filename)
        count += 1

    # Quit
    elif key == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

print("Done. Saved", count, "images.")
>>>>>>> fe3712a1746a474a3e7df8b939355920585d9381
