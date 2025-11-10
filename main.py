"""Command line entry point demonstrating report generation flow."""
from __future__ import annotations

from pathlib import Path

from config.settings import load_settings
from engine import ReportEngine
from export.plain_text import PlainTextExporter
from llm import DummyLLMClient
from templates import load_report_template_from_json


def build_sample_context() -> dict:
    """Return example business data used to populate the sample report."""

    return {
        "device": {
            "name": "离心泵A1",
            "type": "离心泵",
            "usage_summary": "设备全年保持连续运行，关键部件在第三季度完成维护。",
        },
        "inspection": {
            "year": "2024",
            "measurements": [
                {
                    "item": "额定流量",
                    "standard": "120 m3/h",
                    "measured": "118",
                    "conclusion": "合格",
                },
                {
                    "item": "振动值",
                    "standard": "≤ 4.5 mm/s",
                    "measured": "3.8",
                    "conclusion": "合格",
                },
            ],
        },
    }


def main() -> None:
    """Load a template, generate the report, and print it to stdout."""

    settings = load_settings()
    template_path = Path("templates/example_template.json")
    template = load_report_template_from_json(template_path)

    context_data = build_sample_context()

    # Use dummy client for demonstration. In production instantiate BailianLLMClient
    # with credentials from ``settings``.
    llm_client = DummyLLMClient()

    engine = ReportEngine(llm_client=llm_client)
    document = engine.generate(template=template, context_data=context_data)

    exporter = PlainTextExporter()
    output = exporter.export(document)
    print(output)

    if settings.bailian_api_key:
        print("\n提示: 检测到配置了百炼 API Key，可将 DummyLLMClient 替换为 BailianLLMClient 进行真实调用。")


if __name__ == "__main__":
    main()
