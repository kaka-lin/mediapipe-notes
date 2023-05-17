"""MediaPipe Image Segmentation Example.

The ImageSegmenter object will separate the background and foreground of the image
and apply separate colors for them to highlight where each distinctive area exists.
"""
import math

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


BG_COLOR = (192, 192, 192)  # gray
MASK_COLOR = (255, 255, 255)  # white
# Height and width that will be used by the model
DESIRED_HEIGHT = 480
DESIRED_WIDTH = 480


def visualize(image):
    """Visualizes an image.

    Args:
      image: The input image.
    """
    h, w = image.shape[:2]

    if h < w:
        img = cv2.resize(image, (DESIRED_WIDTH, math.floor(h/(w/DESIRED_WIDTH))))
    else:
        img = cv2.resize(image, (math.floor(w/(h/DESIRED_HEIGHT)), DESIRED_HEIGHT))

    cv2.imshow('image', img)


if __name__ == "__main__":
    IMAGE_FILE = 'images/image.jpg'
    img = cv2.imread(IMAGE_FILE)

    # STEP 1: Create an ImageSegmenter object.
    base_options = python.BaseOptions(
        model_asset_path='model/deeplabv3.tflite')
    # Image segmentation here will use a category mask,
    # which applies a category to each found item based on confidence.
    options = vision.ImageSegmenterOptions(base_options=base_options,
                                           output_category_mask=True)

    # Use the `create_from_options()` function to create the task
    #   including: running mode, display names, max number of results,
    #              confidence threshold, category allow list, and deny list.
    # https://developers.google.com/mediapipe/solutions/vision/object_detector/python#configuration

    # Create the image segmenter
    with vision.ImageSegmenter.create_from_options(options) as segmenter:
        # STEP 2: Load the input image.
        image = mp.Image.create_from_file(IMAGE_FILE)

        # STEP 3: Retrieve the masks for the segmented image
        segmentation_result = segmenter.segment(image)
        category_mask = segmentation_result.category_mask

        # STEP 4: Generate solid color images for showing the output segmentation mask.
        # image_data = image.numpy_view()
        # fg_image = np.zeros(image_data.shape, dtype=np.uint8)
        # fg_image[:] = MASK_COLOR # foreground (white)
        # bg_image = np.zeros(image_data.shape, dtype=np.uint8)
        # bg_image[:] = BG_COLOR # background (gray)

        # > 0.2: forefround
        # condition = np.stack((category_mask.numpy_view(),) * 3, axis=-1) > 0.2
        # output_image = np.where(condition, fg_image, bg_image)

        # print(f'Segmentation mask of {IMAGE_FILE}:')
        # visualize(output_image)

        # Convert the BGR image to RGB
        image_data = cv2.cvtColor(image.numpy_view(), cv2.COLOR_BGR2RGB)

        # Apply effects
        blurred_image = cv2.GaussianBlur(image_data, (55, 55), 0)
        # > 0, 0.1, 0.2: forefround
        condition = np.stack((category_mask.numpy_view(),) * 3, axis=-1) > 0.1
        output_image = np.where(condition, image_data, blurred_image)

        print(f'Blurred background of {IMAGE_FILE}:')
        visualize(output_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
