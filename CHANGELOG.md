# Changelog

## Unreleased

## 0.1.1

- Fix missing upload controls for the optional filename field by declaring ComfyUI's native UI-only widgets explicitly.
- Keep omitted/null/empty filenames supported by the API; no frontend extension or dependency is added.

## 0.1.0

- Add `MTAIOptionalLoadImage` with optional filename input and an enabled switch.
- Return `None` for empty inputs and expose `has_image`.
- Reuse ComfyUI's native loader; preserve errors for invalid selected files.
- Include API fragments, installation documentation and contract tests.
