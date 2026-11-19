# Installation acceptance / 安装验收

The Python contract tests pass locally. The following real ComfyUI checks are pending; no claim of a cloud installation or full H3 run is made yet.

本地 Python 行为测试已通过；以下真实 ComfyUI 验证尚待执行。

1. Install this project alone, restart ComfyUI, and confirm `MTAIOptionalLoadImage` appears in `/object_info` and its native upload control appears in the editor. / 单独安装、重启，确认节点注册及上传控件。
2. Connect an empty enabled node to a consumer that supports `None`. Submit API inputs with the filename omitted, `null`, `""`, and `"None"`. Expect `(None, None, False)` and continued downstream execution. / 启用时分别测试缺省、null、空字符串、None，预期返回空值，下游继续。
3. Upload a real image, set the returned filename, and confirm standard image output with `has_image=true`; verify the actual content downstream. / 上传真实素材，确认内容及 has_image。
4. Set `enabled=false` while the selected file is missing. Expect empty output without reading/validating the file. With `enabled=true`, a nonempty missing or corrupt file must report an error. / 关闭时允许失效文件；开启时失效或损坏文件须报错。
5. Replace a file's contents without changing its name and run again; expect a new result rather than stale cached media. / 同名文件内容变化后应重新加载。
6. In a copy of the H3 workflow, replace only the corresponding loader type, keep one reference populated and the remaining slots empty, and confirm those empty references do not prevent the intended output branch from running. / 在 H3 副本中替换同类加载节点，保留一个素材，其余为空，确认实际生成分支运行。

Record the tested ComfyUI/frontend/Python versions and actual result before marking these checks passed. / 验收时记录实际版本及结果。

## 0.1.1 upload control regression / 上传控件回归

Update, restart ComfyUI, hard-refresh the browser and add a fresh node. Confirm the upload button opens the correct media picker, uploads a real file, updates the filename, and produces valid output. Then select `None` and confirm the nullable downstream consumer still executes. Verify workflow save/reload keeps the filename and enabled switch. These browser checks remain pending until performed on the installed plugin. / 更新、重启、强刷后新建节点，检查上传、文件名回填、真实输出、切回 None 后继续执行，以及保存重开后的参数；实机检查仍待完成。
