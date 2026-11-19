"""Contract tests with only the ComfyUI boundary replaced by test doubles.

Run real decoding/API integration checks inside ComfyUI; these tests do not
install or simulate PyTorch, Pillow, PyAV, or ComfyUI's execution engine.
"""

import hashlib
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class OptionalInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / "reference.png"
        self.file.write_bytes(b"first file contents")
        (self.root / "not-media.txt").write_text("not media")
        self.pixels, self.mask = object(), object()
        self.waveform = Mock()
        self.decoder = Mock(return_value=(self.waveform, 48000))
        native = types.ModuleType("nodes")
        native.LoadImage = Mock()
        native.LoadImage.INPUT_TYPES.return_value = {"required": {
            "image": ([self.file.name], {"image_upload": True}),
        }}
        native.LoadImage.VALIDATE_INPUTS.side_effect = lambda name: (
            True if (self.root / name).exists() else f"Invalid image file: {name}"
        )
        native.LoadImage.IS_CHANGED.side_effect = lambda name: hashlib.sha256(
            (self.root / name).read_bytes()
        ).hexdigest()
        native.LoadImage.return_value.load_image.return_value = (self.pixels, self.mask)
        self.native = native.LoadImage
        folders = types.ModuleType("folder_paths")
        folders.get_input_directory = lambda: str(self.root)
        folders.get_annotated_filepath = lambda name: str(self.root / name)
        folders.exists_annotated_filepath = lambda name: (self.root / name).exists()
        folders.filter_files_content_types = lambda files, kinds: [
            name for name in files if name.endswith(".png")
        ]
        extras = types.ModuleType("comfy_extras")
        extras.__path__ = []
        audio = types.ModuleType("comfy_extras.nodes_audio")
        audio.load = self.decoder
        modules = {"nodes": native, "folder_paths": folders,
                   "comfy_extras": extras, "comfy_extras.nodes_audio": audio}
        self.module_patch = patch.dict(sys.modules, modules)
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)
        repo = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "optional_input_test_package", repo / "__init__.py",
            submodule_search_locations=[str(repo)],
        )
        package = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = package
        self.addCleanup(lambda: [sys.modules.pop(name, None) for name in
                                [spec.name, spec.name + ".nodes"]])
        spec.loader.exec_module(package)
        self.cls = package.NODE_CLASS_MAPPINGS["MTAIOptionalLoadImage"]
        self.node = self.cls()
        self.load = getattr(self.node, self.cls.FUNCTION)

    def test_empty_values_allow_execution_without_decoding(self):
        for value in (None, "", "   ", "None"):
            with self.subTest(value=value):
                self.assertIs(self.cls.VALIDATE_INPUTS(**{"image": value}), True)
                self.assertEqual(self.load(**{"image": value}), (None, None, False))
                self.assertEqual(self.cls.IS_CHANGED(**{"image": value}), "empty")
        self.assertEqual(self.load(), (None, None, False))
        self.native.return_value.load_image.assert_not_called()
        self.decoder.assert_not_called()

    def test_disabled_missing_file_does_not_validate_hash_or_decode(self):
        args = {"image": "missing.png", "enabled": False}
        self.assertIs(self.cls.VALIDATE_INPUTS(**args), True)
        self.assertEqual(self.cls.IS_CHANGED(**args), "empty")
        self.assertEqual(self.load(**args), (None, None, False))
        self.native.VALIDATE_INPUTS.assert_not_called()
        self.native.return_value.load_image.assert_not_called()
        self.decoder.assert_not_called()

    def test_optional_image_has_explicit_native_upload_widget(self):
        fields = self.cls.INPUT_TYPES()["optional"]
        self.assertEqual(fields["upload"][0], "IMAGEUPLOAD")
        self.assertEqual(fields["upload"][1]["imageInputName"], "image")
        self.assertTrue(fields["upload"][1]["image_upload"])
        self.assertLess(list(fields).index("image"), list(fields).index("upload"))

    def test_valid_input_uses_native_decoder(self):
        self.assertIs(self.cls.VALIDATE_INPUTS(**{"image": self.file.name}), True)
        result = self.load(**{"image": self.file.name})
        self.assertTrue(result[-1])
        self.assertIs(result[0], self.pixels)
        self.assertIs(result[1], self.mask)
        self.native.return_value.load_image.assert_called_once_with(self.file.name)

    def test_missing_file_is_an_error_not_empty(self):
        result = self.cls.VALIDATE_INPUTS(**{"image": "missing.png"})
        self.assertIsInstance(result, str)
        self.assertIn("Invalid", result)

    def test_directory_is_not_a_file(self):
        (self.root / "folder").mkdir()
        self.assertIsInstance(self.cls.VALIDATE_INPUTS(**{"image": "folder"}), str)

    def test_invalid_api_value_is_rejected(self):
        for value in (42, [], {}):
            self.assertIsInstance(self.cls.VALIDATE_INPUTS(**{"image": value}), str)

    def test_invalid_enabled_api_value_is_rejected(self):
        for value in (None, "false", 0, 1):
            self.assertIsInstance(self.cls.VALIDATE_INPUTS(enabled=value), str)

    def test_corrupt_file_error_is_not_hidden(self):
        self.native.return_value.load_image.side_effect = ValueError("corrupt file")
        self.decoder.side_effect = ValueError("corrupt file")
        with self.assertRaisesRegex(ValueError, "corrupt file"):
            self.load(**{"image": self.file.name})

    def test_same_filename_new_content_invalidates_cache(self):
        first = self.cls.IS_CHANGED(**{"image": self.file.name})
        self.file.write_bytes(b"different file contents")
        self.assertNotEqual(first, self.cls.IS_CHANGED(**{"image": self.file.name}))

    def test_schema_has_optional_upload_field_and_enabled_default(self):
        fields = self.cls.INPUT_TYPES()["optional"]
        self.assertEqual(fields["image"][0][0], "None")
        self.assertIn(self.file.name, fields["image"][0])
        self.assertNotIn("not-media.txt", fields["image"][0])
        self.assertTrue(fields["image"][1]["image_upload"])
        self.assertTrue(fields["enabled"][1]["default"])


if __name__ == "__main__":
    unittest.main()
