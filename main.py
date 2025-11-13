"""命令行入口：演示如何按照模板与业务数据生成报告。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import Settings, load_settings
from engine import ReportEngine
from export.plain_text import PlainTextExporter
from llm import BailianConfig, BailianLLMClient, DummyLLMClient, LLMClient
from templates import load_report_template_from_json

BASE_DIR = Path(__file__).resolve().parent


def build_sample_context() -> Dict[str, Any]:
    """返回一个示例业务数据，用于演示报告生成流程。"""

    return {
        "product": {
            "name": "抗压力水杯套件",
            "model": "PX-300",
            "brand": "清众集团",
            "material": "航空级铝材 + 复合缓冲层",
            "scenario": "极寒作业与户外徒步",
        },
        "function_overview": {
            "core_features": [
                "杯体在 -30℃ 至 90℃ 变化下保持密封",
                "防护环可快速替换以适配不同冲击等级",
                "食品级内胆通过多项第三方检测",
            ],
            "usage_summary": "面向长时间户外值守人员，强调抗压、保温与饮水安全的综合表现。",
        },
        "testing": {
            "year": "2024",
            "location": "清众集团联合实验中心",
            "partners": [
                "清众结构实验室",
                "Hydrotech 材料团队",
            ],
            "focus": "验证极端冲击与微量物质监测模块的稳定性。",
            "collaboration_summary": "双方共同制定跌落、静压及微量物质限值，形成联合检测基线。",
        },
        "measurement_items": [
            {
                "item": "有效容量",
                "standard": "500 ± 10 ml",
                "measured": "498 ml",
                "conclusion": "合格",
                "remarks": "24h 容量保持率 99.2%",
            },
            {
                "item": "抗击打能力",
                "standard": "1.5 m 跌落 10 次",
                "measured": "通过 12 次跌落",
                "conclusion": "优于标准",
                "remarks": "外壳无裂纹，仅表面擦伤",
            },
            {
                "item": "微量物质含量",
                "standard": "重金属 ≤ 0.005 mg/L",
                "measured": "未检出",
                "conclusion": "合格",
                "remarks": "第三方复测一致",
            },
        ],
    }


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="根据模板和输入数据生成中文报告。")
    parser.add_argument(
        "-i",
        "--input",
        dest="input_path",
        type=Path,
        help="输入业务数据的 JSON 文件路径，留空则使用内置示例。",
    )
    return parser.parse_args(argv)


def _load_context_from_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"未找到输入文件: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("输入 JSON 顶层必须是对象（形如 { ... }）。")
    return data


def _build_llm_client(settings: Settings) -> LLMClient:
    """根据配置自动选择 LLM 客户端。"""

    if (
        settings.bailian_api_key
        and settings.bailian_endpoint
        and settings.bailian_model
    ):
        config = BailianConfig(
            api_key=settings.bailian_api_key,
            endpoint=settings.bailian_endpoint,
            model=settings.bailian_model,
        )
        return BailianLLMClient(config)

    return DummyLLMClient()


def main(argv: Optional[List[str]] = None) -> None:
    """按模板生成报告并输出到终端。"""

    args = _parse_args(argv)

    settings = load_settings()
    template_path = BASE_DIR / "templates" / "example_template.json"
    template = load_report_template_from_json(template_path)

    if args.input_path is not None:
        try:
            context_data = _load_context_from_file(args.input_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise SystemExit(f"无法加载输入数据: {exc}") from exc
    else:
        context_data = build_sample_context()

    llm_client = _build_llm_client(settings)

    engine = ReportEngine(llm_client=llm_client)
    document = engine.generate(template=template, context_data=context_data)

    exporter = PlainTextExporter()
    output = exporter.export(document)
    print(output)

    if isinstance(llm_client, DummyLLMClient):
        print(
            "\n提示: 当前使用 DummyLLMClient，可在 config/config.yml 中配置百炼参数后自动切换到 BailianLLMClient。"
        )
    else:
        print("\n提示: 已使用百炼接口生成正文，详见上方输出。")


if __name__ == "__main__":
    main()
