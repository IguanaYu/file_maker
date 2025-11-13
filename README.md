# 检验 / 产品报告生成框架

该项目展示如何通过“结构化模板 + 业务数据 + 大语言模型（LLM）”自动生成中文报告文本。核心目标是验证模板化分块、数据绑定、LLM 调用与导出流程，暂未包含网页或 GUI。

## 功能特点

- **多块模板**：支持标题（TITLE）、正文（SECTION_CONTENT）、表格（TABLE）三类块，自由组合形成报告结构。
- **灵活生成策略**：每个块可选择固定内容、占位符填充或调用 LLM 自动撰写。
- **模板文件化**：模板以 JSON 描述，默认示例位于 `templates/example_template.json`，可轻松复制修改。
- **LLM 抽象**：内置 Dummy 客户端便于本地调试，同时提供 Bailian 客户端以对接阿里云百炼接口。
- **文本导出**：通过 `PlainTextExporter` 将生成结果渲染为易读的纯文本。

## 目录结构

```
config/           # 配置文件与读取逻辑
engine/           # 报告生成引擎、数据绑定、Prompt 构建
export/           # 各类导出器（目前仅纯文本）
llm/              # LLM 客户端抽象与实现
models/           # 报告/模板相关数据模型与枚举
templates/        # 模板示例与加载工具
main.py           # 命令行演示入口
USAGE.md          # 详细使用手册（模板 & 输入制作指南）
```

## 快速体验

1. （可选）在 `config/config.yml` 中填写百炼 API 信息，或设置 `BAILIAN_API_KEY` / `BAILIAN_ENDPOINT` / `BAILIAN_MODEL` 环境变量。
2. 在仓库根目录执行：

   ```bash
   python file_maker/main.py
   ```

   程序会加载默认模板与示例数据，调用 LLM 生成报告并打印到终端。

## 切换百炼调用

1. 编辑 `config/config.yml`：
   ```yaml
   bailian:
     api_key: "<你的真实 Key>"
     endpoint: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
     model: "qwen-plus"
   ```
2. 运行 `python file_maker/main.py`。程序会检测到配置齐全，自动启用 `BailianLLMClient` 并在输出末尾提示“已使用百炼接口生成正文”。
3. 如遇报错，请检查网络、Key、Endpoint 是否正确，或查看百炼返回的错误信息。

## 自定义输入

- 默认示例调用内置的演示数据。若要生成自己的报告，可按 `sample_input.json` / `sample_input2.json` 的格式准备 JSON。
- 运行时通过 `--input` 参数指定：

  ```bash
  python file_maker/main.py --input file_maker/sample_input2.json
  ```

- 请确保输入 JSON 中包含模板 `data_bindings` 所需的字段，详情参见 `USAGE.md`。

## 进阶（多模板 & 指南）

- `USAGE.md` 提供面向“小白用户”的图文说明，包含模板制作、输入整理、命令示例和排错建议。
- 若要支持多套模板，可复制 `templates/example_template.json` 为自定义文件，并在 `main.py` 中扩展 `--template` 参数（或直接覆盖默认模板）。

## 后续计划

- [ ] 接入更多 LLM / 输出格式（Markdown、Docx 等）
- [ ] 增补自动化测试
- [ ] 支持多模板选择或 Web 交互式配置

欢迎根据业务场景自行扩展模板与输入数据，生成更贴合需求的报告文本。***
