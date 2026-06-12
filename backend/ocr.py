# import cv2
# import easyocr
# import os

# reader = easyocr.Reader(["en"], gpu=False)


# def preprocess_image(image_path: str):
#     img = cv2.imread(image_path)

#     # Resize only if image is small
#     height, width = img.shape[:2]

#     if width < 1200:
#         scale = 1200 / width
#         img = cv2.resize(
#             img,
#             None,
#             fx=scale,
#             fy=scale,
#             interpolation=cv2.INTER_CUBIC
#         )

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Light cleanup only, fast
#     gray = cv2.bilateralFilter(gray, 5, 50, 50)

#     processed_path = image_path.replace(".", "_processed.")

#     cv2.imwrite(processed_path, gray)

#     return processed_path


# def extract_text_from_image(image_path: str):
#     processed_path = preprocess_image(image_path)

#     results = reader.readtext(
#         processed_path,
#         detail=0,
#         paragraph=False,
#         decoder="greedy",
#         batch_size=4
#     )

#     return "\n".join(results)


import cv2
import easyocr
import os

reader = easyocr.Reader(["en"], gpu=False)


def preprocess_image(image_path: str):
    img = cv2.imread(image_path)

    if img is None:
        raise Exception(f"Cannot read image: {image_path}")

    height, width = img.shape[:2]

    if width < 1200:
        scale = 1200 / width
        img = cv2.resize(
            img,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 5, 50, 50)

    name, ext = os.path.splitext(image_path)
    processed_path = f"{name}_processed{ext}"

    cv2.imwrite(processed_path, gray)

    return processed_path


def extract_text_from_image(image_path: str):
    print("OCR STARTED")

    # TEMPORARY TEST
    return "TEST OCR"