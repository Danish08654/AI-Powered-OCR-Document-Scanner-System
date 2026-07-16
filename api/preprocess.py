import cv2
import numpy as np


def preprocess_image(image_path):

    try:
        image = cv2.imread(image_path)

        if image is None:
            raise Exception("Image not loaded properly")

        # -----------------------------------
        # 1. Convert to grayscale
        # -----------------------------------
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # -----------------------------------
        # 2. Resize (VERY IMPORTANT for OCR)
        # -----------------------------------
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # -----------------------------------
        # 3. Noise removal (stronger than Gaussian blur)
        # -----------------------------------
        gray = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)

        # -----------------------------------
        # 4. Sharpen image (improves character edges)
        # -----------------------------------
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])

        gray = cv2.filter2D(gray, -1, kernel)

        # -----------------------------------
        # 5. Adaptive threshold (better OCR separation)
        # -----------------------------------
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2
        )

        # -----------------------------------
        # 6. Morphological cleanup (removes noise)
        # -----------------------------------
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        return thresh

    except Exception as e:
        raise Exception(f"Preprocessing Error: {str(e)}")