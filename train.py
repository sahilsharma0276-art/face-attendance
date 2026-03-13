<<<<<<< HEAD
import cv2
import os
import numpy as np
from PIL import Image

dataset_path = "dataset"

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
ids = []
label_ids = {}
current_id = 0

print("Loading dataset...")

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.endswith("jpeg") or file.endswith("jpg"):
            path = os.path.join(root, file)
            label = os.path.basename(root)

            if label not in label_ids:
                label_ids[label] = current_id
                current_id += 1

            id_ = label_ids[label]

            img = Image.open(path).convert("L")
            img_np = np.array(img, "uint8")

            faces.append(img_np)
            ids.append(id_)

if len(faces) == 0:
    print("No images found in dataset ❌")
else:
    recognizer.train(faces, np.array(ids))
    recognizer.save("trainer.yml")
=======
import cv2
import os
import numpy as np
from PIL import Image

dataset_path = "dataset"

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
ids = []
label_ids = {}
current_id = 0

print("Loading dataset...")

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.endswith("jpeg") or file.endswith("jpg"):
            path = os.path.join(root, file)
            label = os.path.basename(root)

            if label not in label_ids:
                label_ids[label] = current_id
                current_id += 1

            id_ = label_ids[label]

            img = Image.open(path).convert("L")
            img_np = np.array(img, "uint8")

            faces.append(img_np)
            ids.append(id_)

if len(faces) == 0:
    print("No images found in dataset ❌")
else:
    recognizer.train(faces, np.array(ids))
    recognizer.save("trainer.yml")
>>>>>>> fe3712a1746a474a3e7df8b939355920585d9381
    print("Training Complete ✅")