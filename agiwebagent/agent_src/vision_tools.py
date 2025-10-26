# agiwebagent/agent_src/vision_tools.py

import base64
import io
import json
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel, Field
from typing import List, Optional


class UIElement(BaseModel):
    """Represents a single detected UI element on the page."""
    label: str = Field(description="The text content or label of the element.")
    type: str = Field(description="The type of element (e.g., 'button', 'text', 'heading', 'input', 'link').")
    location: List[int] = Field(description="Bounding box coordinates as [x1, y1, x2, y2].")


class VisualScanResult(BaseModel):
    """The complete visual scan of the viewport."""
    elements: List[UIElement] = Field(description="A list of all detected UI elements.")


class VisionExtractor:
    def __init__(self, client: OpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model
        self.system_prompt = """
        You are an expert UI/UX analyst. Your task is to analyze a website screenshot
        and return a structured JSON object of all visible UI elements.
        
        You must identify:
        - All text (as 'text')
        - All buttons (as 'button')
        - All headings (as 'heading')
        - All input fields (as 'input')
        - All links (as 'link')
        
        For each element, you MUST provide:
        1.  `label`: The text content of the element.
        2.  `type`: The type of element (e.g., 'button', 'text', 'heading').
        3.  `location`: The bounding box coordinates `[x1, y1, x2, y2]`.
        
        Respond ONLY with the valid JSON object defined by the `VisualScanResult` schema.
        """

    def _image_to_base64_url(self, image: Image.Image) -> str:
        """Convert PIL image to base64 data URL."""
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")
        with io.BytesIO() as buffer:
            image.save(buffer, format="JPEG")
            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{image_base64}"

    def extract_content(self, image: Image.Image, prompt: str) -> str:
        """
        Takes a PIL image, sends it to the vision model, and returns
        a JSON string of the extracted UI elements.
        """
        base64_image_url = self._image_to_base64_url(image)

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                response_format=VisualScanResult,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_image_url, "detail": "low"},
                            },
                        ],
                    },
                ],
                max_tokens=2048,
                temperature=0.0,
            )


            parsed_result: VisualScanResult = completion.choices[0].message.parsed
            return parsed_result.model_dump_json(indent=2)

        except Exception as e:
            print(f"❌ VisionExtractor Error: {e}")
            return json.dumps({"error": str(e), "elements": []})