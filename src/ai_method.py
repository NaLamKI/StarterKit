import sys
import os
from typing import Dict, Any
from fastapi import UploadFile
import torch
from torch import nn
import os
import os.path as osp
sys.path.append(os.path.join(sys.path[0],'model','yolo'))
sys.path.append(os.path.join(sys.path[0],'model'))

from model.yolo_main import DetectMultiBackend
from model.yolo_main import select_device
from model.yolo_main import detect_in_images, detect_in_image
from typing import List
from PIL import Image
import io
import shutil
import os
import base64

validation_weights = "./model/best.pt"
try:
    device = select_device("0")
except Exception as e:
    print("RUNNING ON CPU")
    device = select_device("cpu")
    print(e)

def imgData2base64src(imgData, format = "png"):
    """ Converts image data to base_64 string.
    """
    return "data:image/" + format + ";base64," + base64.b64encode(imgData).decode()

def pil_to_bytes(img, format="JPEG"):
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=100)
    buf.seek(0)
    return buf.read()

def init_model(tmp_path: str) -> nn.Module:
    """Initialize your ai model. This method will be called once, so that the model isn't initialized each time a prediction is made.

    Args:
        tmp_path (str): path where the data will be saved temporarily.

    Raises:
        Exception: if CUDA should be used, but no GPU is available.

    Returns:
        nn.Module: AI model
    """
    print("init model")
    model = DetectMultiBackend(validation_weights, device=device, dnn=False, fp16=False)
    return model

async def save_data(tmp_path: str, files: List[UploadFile]) -> None:
    """Save all uploaded files into the required folder structure.

    Args:
        tmp_path (str): Path where temporary data can be saved
        files (list[UploadFile]): list of UploadFile objects from fastapi
    """
    class_data = osp.join(tmp_path, 'no_class')

    if not osp.exists(class_data):
        os.makedirs(class_data)

    for img_file in files:
        with open(osp.join(class_data, img_file.filename), 'wb') as f:
            f.write(await img_file.read())


def process_files(model: nn.Module, file_list: List[str]) -> List[Dict]:
    global DEVICE, USE_HALF, BATCH_SIZE

    results = []
    for file in file_list:
        img = Image.open(file)
        result = detect_in_image(device, model, img, (img.size[0], img.size[1]))
        results.append({
            "image": file,
            "boxes": result
        })
    return results

def process_data(model: nn.Module, data_path: str) -> Dict[str, Any]:
    """Apply your AI method to the data saved in `save_data()`.

    Args:
        model (nn.Module): typically your model but you just get what you returned in `init_model()`
        data_path (str): path to your data folder

    Returns:
        Dict[str, Any]: Results in a `dict` that can be easily transformed into a JSON response.
    """
    global DEVICE, USE_HALF, BATCH_SIZE
    data_path = os.path.join(data_path, "no_class")
    img = Image.open(os.path.join(data_path, os.listdir(data_path)[0]))
    base_64 = imgData2base64src(pil_to_bytes(img))

    results = detect_in_images(device, model, data_path, (img.size[0], img.size[1]), False, False)
    results["img_data"] = base_64
    return results
