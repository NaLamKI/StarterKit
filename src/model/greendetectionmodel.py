import io
import os.path


import cv2
import numpy as np
from PIL import Image as PilImage
from PIL.ExifTags import TAGS, GPSTAGS

class DummyGreenDetectionModel:
    """
    Processes an input image to highlight green areas and extracts relevant information.
    """
    # Define range for green color
    lower_green = np.array([30, 40, 40])
    upper_green = np.array([85, 255, 255])
    # Define image formats usable for the model
    IMAGE_EXTENSIONS = ["jpg", "bmp", "gif", "tif", "tiff", "png", "jpeg", "ppm", "pgm", "webm"]

    def __call__(self, file: io.BufferedReader) -> dict:
        """
        Args:
            file: A buffered input image.
        Returns:
            A dictionary with:
                - 'image': The image with green areas highlighted.
                - 'green': The proportion of green pixels.
                - 'coordinates': The GPS coordinates from the image, if available.
        """
        image = PilImage.open(file)
        uri = os.path.basename(file.name)

        # extract geo data from image meta data
        coordinates = self._get_coordinates(image)

        image = np.array(image)

        mask = self._create_mask(image)

        # Create an image with green areas in color and the rest in grayscale
        output_image = self._highlight_green(image, mask)

        # Calculate the proportion of green pixels
        p_green = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
        return {'image': output_image, 'green': p_green, 'coordinates': coordinates, 'uri': uri}

    def _create_mask(self, image: np.ndarray) -> np.ndarray:
        # Create mask for green color
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        return mask

    @staticmethod
    def _highlight_green(image, mask):
        # Display only green values
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        gray_colored = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        green_only = cv2.bitwise_and(image, image, mask=mask)
        not_green = cv2.bitwise_and(gray_colored, gray_colored, mask=cv2.bitwise_not(mask))
        return cv2.add(green_only, not_green)

    @staticmethod
    def _get_coordinates(image):
        def tuple_to_value(t):
            if isinstance(t, (tuple, list)):
                return float(((t[0] * 60 + t[1]) * 60 + t[2]) / 3600)
            return t

        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for gps_tag in value:
                        sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                        v = value[gps_tag]
                        gps_data[sub_decoded] = v
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
        else:
            return None

        gps_info = exif_data.get('GPSInfo')
        if not isinstance(gps_info, dict):
            return None

        latitude = tuple_to_value(gps_info.get('GPSLatitude', 0))
        longitude = tuple_to_value(gps_info.get('GPSLongitude', 0))
        return [latitude, longitude]
