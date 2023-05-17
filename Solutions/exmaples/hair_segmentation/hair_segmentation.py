"""MediaPipe Hair Segmentation and Recolor Example.

Hair segmentation model:
    This model takes an image of a person, locates the hair on their head,
    and outputs a image segmentation map for their hair.
    You can use this model for recoloring hair or applying other hair effects.

    segmentation categories:
    - 0: background
    - 1: hair
"""
import math

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    IMAGE_FILE = 'images/image.jpg'
    img = cv2.imread(IMAGE_FILE)

    # STEP 1: Create an ImageSegmenter object.
    base_options = python.BaseOptions(
        model_asset_path='model/hair_segmenter.tflite')
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

        # STEP 4: Recoloring hair
        ## 1. Convert the BGR image to RGB
        image_data = cv2.cvtColor(image.numpy_view(), cv2.COLOR_BGR2RGB)
        ## 2. Create mask - 0: backgroun, 1: hair
        mask = np.where(category_mask.numpy_view() > 0, 1, 0)

        ## 3. Apply the color you want to change
        # mask_n = np.stack(mask * 3, axis=-1)
        mask_n = np.zeros(image_data.shape, dtype=np.uint8)
        mask_n[:, :, 0] = mask * 255
        mask_n[:, :, 1] = mask * 0
        mask_n[:, :, 2] = mask * 0

        ## 4. Apply mask: using addWeighted
        alpha = 0.8
        beta = (1.0 - alpha)
        # g(x) = (1-alpha) * x + alpha * y
        output_image = cv2.addWeighted(image_data, alpha, mask_n, beta, 0.0)

        print(f'Segmentation mask of {IMAGE_FILE}:')
        visualize(output_image)
