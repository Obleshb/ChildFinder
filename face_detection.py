import cv2
import numpy as np
import logging
from PIL import Image
import os

class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        logging.basicConfig(level=logging.DEBUG)

    def detect_faces(self, image_path):
        try:
            logging.info(f"Attempting to detect faces in image: {image_path}")
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                logging.error(f"Could not load image from path: {image_path}")
                raise ValueError("Could not load image")

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces with more lenient parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,  # Slightly reduced from 1.3 for better accuracy
                minNeighbors=3,   # Keep the more lenient detection
                minSize=(20, 20)  # Keep the smaller minimum face size
            )

            logging.info(f"Found {len(faces)} faces in the image")

            # If no faces found, try with even more lenient parameters
            if len(faces) == 0:
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=2,
                    minSize=(10, 10)
                )
                logging.info(f"Second attempt found {len(faces)} faces")

            return len(faces) > 0, faces

        except Exception as e:
            logging.error(f"Face detection error: {str(e)}")
            return False, []

    def compare_faces(self, image1_path, image2_path):
        try:
            logging.info(f"Comparing faces between images: {image1_path} and {image2_path}")

            # Detect faces in both images
            faces1_found, faces1 = self.detect_faces(image1_path)
            faces2_found, faces2 = self.detect_faces(image2_path)

            if not (faces1_found and faces2_found):
                logging.warning("No faces found in one or both images")
                return 0.0

            # Read images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)

            if img1 is None or img2 is None:
                logging.error("Failed to load one or both images")
                return 0.0

            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            # Extract the largest face from each image
            x1, y1, w1, h1 = faces1[0]
            x2, y2, w2, h2 = faces2[0]

            face1 = gray1[y1:y1+h1, x1:x1+w1]
            face2 = gray2[y2:y2+h2, x2:x2+w2]

            # Resize faces to same size
            face1 = cv2.resize(face1, (100, 100))
            face2 = cv2.resize(face2, (100, 100))

            # Compare using multiple methods for better accuracy
            methods = [
                ('Correlation', cv2.HISTCMP_CORREL),
                ('Chi-Square', cv2.HISTCMP_CHISQR),
                ('Intersection', cv2.HISTCMP_INTERSECT)
            ]

            similarities = []
            for method_name, method in methods:
                # Calculate histograms
                hist1 = cv2.calcHist([face1], [0], None, [256], [0, 256])
                hist2 = cv2.calcHist([face2], [0], None, [256], [0, 256])

                # Normalize histograms
                cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
                cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

                # Compare histograms
                similarity = cv2.compareHist(hist1, hist2, method)

                # Convert chi-square and intersection to a 0-1 scale
                if method == cv2.HISTCMP_CHISQR:
                    similarity = 1 / (1 + similarity)
                elif method == cv2.HISTCMP_INTERSECT:
                    similarity = similarity / (np.sum(hist1) + 1e-10)

                similarities.append(similarity)
                logging.info(f"{method_name} similarity: {similarity}")

            # Calculate final similarity score (average of all methods)
            final_similarity = np.mean(similarities)
            logging.info(f"Final similarity score: {final_similarity}")

            return max(0.0, min(1.0, final_similarity))

        except Exception as e:
            logging.error(f"Face comparison error: {str(e)}", exc_info=True)
            return 0.0