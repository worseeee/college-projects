import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
ImageClassifier = mp.tasks.vision.ImageClassifier
ImageClassifierOptions = mp.tasks.vision.ImageClassifierOptions
VisionRunningMode = mp.tasks.vision.RunningMode

predictions = []

options = ImageClassifierOptions(
    base_options=BaseOptions(model_asset_path='efficientnet_lite0.tflite'),
    max_results=5,
    running_mode=VisionRunningMode.IMAGE)

classifier = vision.ImageClassifier.create_from_options(options)

image = mp.Image.create_from_file('catanddog.jpg')

classification_result = classifier.classify(image)

# STEP 5: Process the classification result. In this case, visualize it.
top_category = classification_result.classifications[0].categories[0]
predictions.append(f"{top_category.category_name} ({top_category.score:.2f})")

print(predictions)