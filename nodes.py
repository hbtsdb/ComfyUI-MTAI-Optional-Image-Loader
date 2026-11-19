"""Optional image input using ComfyUI's native image loader."""

import os

import folder_paths
from nodes import LoadImage


def _empty(value):
    return value is None or isinstance(value, str) and value.strip() in ("", "None")


class MTAIOptionalLoadImage:
    @classmethod
    def INPUT_TYPES(cls):
        files, options = LoadImage.INPUT_TYPES()["required"]["image"]
        return {"optional": {
            "image": (["None", *files], {**options, "default": "None"}),
            "enabled": ("BOOLEAN", {"default": True}),
        }}

    RETURN_TYPES = ("IMAGE", "MASK", "BOOLEAN")
    RETURN_NAMES = ("IMAGE", "MASK", "has_image")
    FUNCTION = "load_image"
    CATEGORY = "MTAI/optional inputs"
    DESCRIPTION = (
        "Empty or disabled input returns None, None, False. "
        "Selected files use the native image loader; invalid files raise errors. "
        "The downstream node must support None."
    )

    @classmethod
    def VALIDATE_INPUTS(cls, image=None, enabled=True):
        if not isinstance(enabled, bool):
            return "enabled must be a boolean."
        if not enabled or _empty(image):
            return True
        if not isinstance(image, str):
            return "image must be a filename string or null."
        valid = LoadImage.VALIDATE_INPUTS(image)
        if valid is not True:
            return valid
        if not os.path.isfile(folder_paths.get_annotated_filepath(image)):
            return f"Invalid image file: {image}"
        return True

    @classmethod
    def IS_CHANGED(cls, image=None, enabled=True):
        if not enabled or _empty(image):
            return "empty"
        return LoadImage.IS_CHANGED(image)

    def load_image(self, image=None, enabled=True):
        if not enabled or _empty(image):
            return (None, None, False)
        pixels, mask = LoadImage().load_image(image)
        return (pixels, mask, True)
