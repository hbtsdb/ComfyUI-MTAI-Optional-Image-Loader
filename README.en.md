# ComfyUI-MTAI-Optional-Image-Loader

[中文](README.md)

A standalone optional image loader for ComfyUI. Empty inputs return real Python `None`; selected files use ComfyUI's native decoder. No MTAI Canvas, Chenyu account, companion plugin, or extra Python dependencies are required.

## Behavior

| Input | Result |
| --- | --- |
| Omitted filename, JSON `null`, empty/whitespace string, or dropdown `None` | `(None, None, False)` |
| `enabled=false` | `(None, None, False)`, without validating or reading a file |
| Valid file and `enabled=true` | Standard media data and `has_image=true` |
| Selected file is missing, is a directory, or cannot be decoded | An error; never silently treated as empty |

`None` is a reserved empty choice. The node is enabled by default. Outputs: **IMAGE, MASK, has_image**.

**The receiving node must handle `None`.** This is not a universal downstream bypass. Save/preview/processing nodes requiring media can still fail on empty input. Official H3 reference conditioning skips `None`; check other consumers individually. No placeholder media, silence, or `ExecutionBlocker` is generated.

## Install

Requires Python 3.10+ and ComfyUI with its built-in LoadImage loader.

```sh
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/hbtsdb/ComfyUI-MTAI-Optional-Image-Loader.git
```

Alternatively extract the project ZIP to `ComfyUI/custom_nodes/ComfyUI-MTAI-Optional-Image-Loader/`, with `__init__.py` directly inside that directory. Restart ComfyUI and refresh the browser. Search for **MTAI Optional Load Image**, category `MTAI/optional inputs`. Standard local, portable, container and cloud installations are supported when they allow custom nodes. Follow your cloud provider's environment/image persistence process to retain installations after an instance is destroyed.

## API

Inputs: `image` (filename), `enabled` (boolean, default `true`). Both can be omitted. Use ComfyUI's normal filename/subfolder/annotation conventions. Upload through its standard `/upload/image` endpoint, then pass the returned filename including its subfolder. A misspelled nonempty filename is an error.

This and the files in `examples/` are **node fragments**, not complete executable workflows: connect them to an appropriate output path first.

```json
{
  "1": {
    "class_type": "MTAIOptionalLoadImage",
    "inputs": {
      "image": null,
      "enabled": true
    }
  }
}
```

Replace `null` with `"uploaded-reference.png"` to load a file. Existing workflows are not migrated. Replace the old loader, reconnect outputs, and export a fresh API graph. No Chenyu node names are registered.

## Tests

```sh
python -m unittest discover -s tests -v
```

These dependency-free contract tests replace the ComfyUI boundary with test doubles. They cover optional values, disabling, native-loader delegation, missing/corrupt files, and file-content cache invalidation. They do not certify real decoding, upload widgets, or full H3 inference. See [TESTING.md](TESTING.md) for installation acceptance checks.

## License

[MIT](LICENSE). Uses native ComfyUI APIs without copying its decoder implementation or Chenyu node code. ComfyUI and runtime dependencies retain their own licenses.
