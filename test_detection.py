import os
import pathlib
import random
import cv2
from pycoral.utils import edgetpu
from pycoral.utils import dataset
from pycoral.adapters import common
from pycoral.adapters import classify
from pycoral.adapters import detect

# Specify the TensorFlow model, labels, and image
script_dir = pathlib.Path(__file__).parent.absolute()
model_file = os.path.join(script_dir, 'models (edgetpu)/sunny_edgetpu.tflite')
label_file = os.path.join(script_dir, 'sunnylabels.txt')

images_path = os.path.join(script_dir, 'images')
filenames = os.listdir(os.path.join(images_path))
random_index = random.randint(0, len(filenames) - 1)
INPUT_IMAGE = os.path.join(images_path, filenames[random_index])

# Initialize the TF interpreter
interpreter = edgetpu.make_interpreter(model_file)
interpreter.allocate_tensors()

# Resize the image
size = common.input_size(interpreter)
image = cv2.imread(INPUT_IMAGE)
image = cv2.resize(image, (320, 320))

# Run an inference
common.set_input(interpreter, image)
interpreter.invoke()
classes = classify.get_classes(interpreter, top_k=1)
objs = detect.get_objects(interpreter, 0.4, [1, 1])

# Print the result
labels = dataset.read_label_file(label_file)
for c in classes:
  print('%s: %.5f' % (labels.get(c.id, c.id), c.score))

for obj in objs:
  print("obj")
  print(labels.get(obj.id, obj.id))
  print('  id:    ', obj.id)
  print('  score: ', obj.score)
  print('  bbox:  ', obj.bbox)

  cv2.rectangle(image, (obj.bbox.xmin, obj.bbox.xmax), (obj.bbox.ymin, obj.bbox.ymax), (0, 255, 0), 2)

cv2.imshow('Object Detection', image)
cv2.waitKey(0)