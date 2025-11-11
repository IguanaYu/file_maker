# 检验报告生成系统基础框架

该项目演示如何基于“报告模板 + 业务数据 + 大模型”生成检验报告文本。重点聚焦在模板结构、块处理逻辑以及大模型接口设计，未包含前端页面。

## 功能概览

- 模板定义包含标题、章节正文、表格三类块。
- 通过 `ReportEngine` 结合业务数据和 LLM 客户端生成 `ReportDocument`。
- 支持从 JSON 文件加载模板，默认示例位于 `templates/example_template.json`。
- 默认提供 `DummyLLMClient`，并预留 `BailianLLMClient` 以对接真实百炼接口。
- 使用 `PlainTextExporter` 可将生成结果转换为易读文本。

## 目录结构

```
config/           # 配置文件和加载逻辑
engine/           # 核心生成引擎与辅助工具
export/           # 报告导出器
llm/              # LLM 客户端抽象及实现
models/           # 数据模型与枚举定义
templates/        # 模板示例与加载工具
main.py           # 命令行演示入口
```

## 快速开始

1. 可选：在 `config/config.yml` 中填写百炼接口配置，或通过环境变量 `BAILIAN_API_KEY`、`BAILIAN_ENDPOINT`、`BAILIAN_MODEL` 进行设置。
2. 运行命令：

   ```bash
   python main.py
   ```

   程序会加载示例模板、构造演示数据，调用 `DummyLLMClient` 生成报告并输出到终端。

> TODO: 接入真实百炼接口，并补充自动化测试与更多导出格式。

## 百炼接入

1. 在 config/config.yml 中填写真实的 pi_key、endpoint、model，或设置同名环境变量。字段留空时将自动回退到 DummyLLMClient。
2. 执行 python main.py，程序会根据配置自动选择 BailianLLMClient，并在输出末尾提示当前模式。
3. 若调用失败，可检查网络连通性、凭证以及接口返回的错误信息后重试。

## 自定义输入数据

默认示例使用内置的演示数据。如需针对不同设备或检测结果生成报告，可准备一份 JSON 文件并在运行时通过参数传入：

```bash
python main.py --input my_context.json
```

JSON 根对象需包含 `device`、`inspection` 等模板绑定到的字段。结构可参考 `build_sample_context()` 或 `templates/example_template.json` 中的字段绑定说明。
