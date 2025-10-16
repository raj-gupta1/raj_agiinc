# agent_src/utils.py
import argparse
import base64
import io
from agisdk.REAL.browsergym.utils.obs import flatten_axtree_to_str
import numpy as np
from PIL import Image



def image_to_jpg_base64_url(image: np.ndarray | Image.Image) -> str:
    """Convert image to base64 encoded JPEG URL."""
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")

    with io.BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{image_base64}"


def str2bool(v):
    """Helper function to handle boolean command-line arguments."""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')