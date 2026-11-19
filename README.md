# ComfyUI-MTAI-Optional-Image-Loader

[English](README.en.md)

独立的 ComfyUI 可选图片加载节点。没有选择文件时输出真正的 `None`，有文件时复用ComfyUI 原生 LoadImage。无需 MTAI 画布、晨羽账号或另一个 MTAI 插件；不添加额外 Python 依赖。

## 行为

| 输入 | 输出 |
| --- | --- |
| 文件未提供、JSON `null`、空字符串、纯空白或下拉框 `None` | `(None, None, False)` |
| `enabled=false` | `(None, None, False)`，不检查或读取文件 |
| 有效文件且 `enabled=true` | 标准图片数据，`has_image=true` |
| 已填写但不存在、不是文件或无法解码 | 报错，不静默替换为空值 |

文件选择框的 `None` 是保留空值。节点默认启用；无需为了省略素材而禁用整个节点。

**下游必须支持 `None`。** 这不是通用的执行跳过开关：连接到必须接收图片的保存、预览或处理节点时，下游仍可能报错。官方 H3 参考输入支持忽略 `None`，其他节点应分别确认。节点不生成占位素材，也不使用会阻断下游的 `ExecutionBlocker`。

## 安装

需要 Python 3.10+，以及包含ComfyUI 原生 LoadImage的 ComfyUI。支持标准 `custom_nodes` 安装方式，Windows Portable 同样适用。

在 **ComfyUI 使用的环境** 中执行：

```sh
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/hbtsdb/ComfyUI-MTAI-Optional-Image-Loader.git
```

也可以下载项目 ZIP，解压为 `ComfyUI/custom_nodes/ComfyUI-MTAI-Optional-Image-Loader/`。确认 `__init__.py` 直接位于该目录，不要多嵌套一层。重启 ComfyUI 并刷新页面，在 `MTAI/optional inputs` 分类搜索 **MTAI Optional Load Image**。

晨羽、其他云平台、本机和容器的安装方式相同：将插件安装到实际运行任务的 ComfyUI 环境。云平台须允许安装自定义节点；持久保留请按平台方式保存环境或镜像，不保证销毁实例后插件仍存在。

## 使用和 API

- 输入：`image` 文件名；`enabled` 布尔值，默认 `true`。
- 输出：IMAGE、MASK、has_image。
- 文件名沿用 ComfyUI 原生规则，包括输入子目录和其支持的注解路径。
- 在 ComfyUI 中选择或上传文件，或先使用标准 `/upload/image` 接口上传，再将返回的文件名（含返回的子目录）写入 `image`。
- `has_image` 表示本次是否加载了素材，不代表文件存在性探测开关。

下面及 `examples/` 中是 **API 图的节点片段**，需要接入完整工作流；它们没有输出终点，不能单独当生成任务提交。

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

使用文件时将 `null` 换成已上传的 `"uploaded-reference.png"`。只有确实不提供素材时才留空；文件名拼错会报错。

不注册晨羽同名节点，也不自动修改已有工作流。需要将原加载节点替换为本节点、重新连接输出，并重新导出 API JSON。

## 验证

```sh
python -m unittest discover -s tests -v
```

测试使用标准库和 ComfyUI 边界测试替身，覆盖空值、关闭开关、有效文件调用、缺失/损坏文件和同名文件更新后的缓存失效。它们不证明真实解码器、前端上传控件或完整 H3 推理已通过；安装后的实机检查见 [TESTING.md](TESTING.md)。

## 来源与许可证

MIT，见 [LICENSE](LICENSE)。本项目使用 ComfyUI 原生接口，不包含晨羽节点源码，也没有复制 ComfyUI 的解码实现。ComfyUI 和其运行依赖仍遵循各自许可证。
