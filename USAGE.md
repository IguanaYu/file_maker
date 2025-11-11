# 使用手册（模板 + 输入数据全流程）

本手册面向**第一次接触项目、没有耐心翻文档**的同学，按“照做就行”的方式一步步说明：模板怎么做、输入数据怎么准备，以及最终如何生成报告。

---

## 0. 基本概念

| 名称 | 作用 | 存放位置 |
| --- | --- | --- |
| 模板（Template） | 决定报告结构：有哪些标题、正文、表格，是否用 LLM 生成等。 | `file_maker/templates/*.json` |
| 输入数据（Context/Input） | 提供模板所需的具体业务数据，如设备信息、测量表格。 | 任意 `.json` 文件，建议放在 `file_maker/` 或 `data/` 目录下 |
| 运行命令 | `python file_maker/main.py --template ... --input ...`（若不传参数则使用默认模板和示例数据） | 终端执行 |

---

## 1. 快速上手清单

1. **复制模板**  
   - 在 `file_maker/templates/` 内复制一份现有模板，如：  
     ```
     cp templates/example_template.json templates/tank_template.json
     ```
2. **修改模板**  
   - 根据需求改动新模板中的块（blocks），决定每一块是固定文本、模板填充还是 LLM 生成。
3. **准备输入 JSON**  
   - 将真实业务数据按照模板里的 `data_bindings` 结构填好，例如 `tank_info.json`。
4. **运行命令**  
   - 在仓库根目录执行：  
     ```bash
     python file_maker/main.py --template file_maker/templates/tank_template.json --input file_maker/tank_info.json
     ```
5. **查看输出**  
   - 程序会把生成的文本打印到终端，如需保存可追加 `> report.txt`。

---

## 2. 如何制作模板（Template）

模板文件是一个 JSON，核心字段为 `blocks` 数组。每个 block 对应报告中的一个“部分”，例如标题、正文、表格等。

### 2.1 Block 关键字段

| 字段 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- |
| `block_id` | 是 | 唯一标识符，便于排查问题。 | `"function_section_content"` |
| `block_type` | 是 | `TITLE` / `SECTION_CONTENT` / `TABLE`。 | `"TABLE"` |
| `generation_strategy` | 是 | `FIXED`（固定文本）、`TEMPLATE_FILL`（字符串填充）、`LLM`（调用大模型）、`FIXED` + `TABLE` 用于渲染表格。 | `"LLM"` |
| `template_text` | 否 | `FIXED` 或 `TEMPLATE_FILL` 时使用的基准文本。 | `"{inspection_year}年{device_name}检验报告"` |
| `data_bindings` | 否 | 当 block 需要上下文数据（LLM/TEMPLATE_FILL）时，写清楚“模板占位符”对应的输入路径。 | `"device_name": "product.name"` |
| `constraints` | 否 | 给 LLM 的额外约束，如风格、字数。 | `"max_words": "200"` |
| `table_columns` | `TABLE` 必填 | 表头配置，`header`=显示名称，`field`=数据字段，`unit` 可选。 | `[{"header":"判定","field":"conclusion"}]` |
| `row_data_source` | `TABLE` 必填 | 表格数据在输入 JSON 中的路径。 | `"measurement_items"` |

### 2.2 模板制作步骤

1. **确认报告骨架**：列出需要的标题、段落、表格。
2. **对应 block**：为每个部分写一个 block。
   - 需要固定文本就用 `generation_strategy: "FIXED"` + `template_text`。
   - 要根据输入字段渲染但不调用 LLM，使用 `TEMPLATE_FILL` 并在 `template_text` 中放占位符 `{placeholder}`。
   - 需要 LLM 撰写的段落，设为 `LLM` 并写好 `data_bindings` 与 `constraints`。
   - 表格用 `block_type: "TABLE"`, `row_data_source` 指向输入 JSON 中的列表。
3. **保存**：命名为 `xxx_template.json`，放在 `templates/` 下。

> **别忘了验证 JSON 是否合法**：可用 `python -m json.tool templates/xxx_template.json` 检查格式。

---

## 3. 如何准备输入数据（Input JSON）

输入 JSON 必须是一个对象（最外层 `{}`），字段结构需覆盖模板里的所有 `data_bindings` 路径。

### 3.1 读取路径示例

模板中的 `data_bindings` 如果是 `"device_name": "product.name"`，则输入 JSON 需要：
```json
{
  "product": {
    "name": "抗压力水杯套件"
  }
}
```
如果是 `"measurement_items"` 这种列表路径，就需要：
```json
{
  "measurement_items": [
    {"item": "容量", "standard": "500ml", "measured": "498ml", "conclusion": "合格"}
  ]
}
```

### 3.2 建议的写法

1. **逐字段检查**：对照模板中每个 block 的 `data_bindings` 和 `table_columns`，确认输入 JSON 有对应字段。
2. **保持 UTF-8 编码**：保存时选 UTF-8 或 UTF-8 with BOM（程序会自动兼容）。
3. **分主题维护**：不同项目/产品单独建文件，例如：
   - `tank_info.json`
   - `food_lab_info.json`
   - `wind_turbine_qc.json`

### 3.3 快速验证

运行：
```bash
python - <<'PY'
import json, pathlib
path = pathlib.Path("file_maker/tank_info.json")
json.loads(path.read_text(encoding="utf-8"))
print("JSON 结构合法")
PY
```
看到 “JSON 结构合法” 说明没有语法问题。

---

## 4. 运行与调试

### 4.1 基础命令

```bash
# 默认使用 example_template + 内置示例数据
python file_maker/main.py

# 指定模板 + 输入数据（推荐）
python file_maker/main.py --template file_maker/templates/tank_template.json --input file_maker/tank_info.json
```

> `--template` 参数尚未默认启用。如果你需要多模板支持，请先在 `main.py` 中添加该参数（可参考 README/Issues）。现阶段如需更换模板，可暂时替换 `templates/example_template.json` 或手动修改脚本指向新的文件。

### 4.2 常见报错排查

| 报错 | 排查思路 |
| --- | --- |
| `Context file not found` | 输入的 JSON 路径写错了，确认是否相对仓库根目录。 |
| `Row data source ... must resolve to a list` | 模板中的 `row_data_source` 指向的字段不是列表，检查输入 JSON。 |
| `KeyError` / `None` 内容 | `data_bindings` 中的路径找不到对应字段，补齐输入 JSON。 |
| LLM 返回 Dummy 提示 | `config/config.yml` 中的百炼配置没填完整，或命令在错误目录执行。 |

---

## 5. 示例：坦克质量检测报告

1. 复制模板：`cp templates/example_template.json templates/tank_template.json`
2. 根据坦克报告需求修改 `tank_template.json`，调整标题/段落/表格。
3. 收集坦克的质检数据（基础参数、检测结果、表格数据等），写入 `tank_info.json`，字段要与模板里的 `data_bindings` 对应。
4. 运行命令（假设未来支持 `--template` 参数）：  
   ```bash
   python file_maker/main.py --template file_maker/templates/tank_template.json --input file_maker/tank_info.json
   ```
5. 检查终端输出或保存成文件：  
   ```bash
   python file_maker/main.py --template ... --input ... > tank_report.txt
   ```

---

## 6. 温馨提示

- 模板先于数据：先确定报告有哪些块，再去收集/整理输入数据。
- 小步迭代：每改一个 block 就跑一次命令，及时发现字段缺失问题。
- 版本留档：复杂模板建议用 Git 分支或复制一份旧版本，避免误删。
- 如果使用真实百炼接口，请确认网络和 API Key 都可用，避免运行时超时。

只要按照上面步骤走，哪怕“很笨没耐心”，也能在 10 分钟内做出一份新的模板 + 报告。需要进一步自动化（多模板切换、Web 界面等）再随时提需求。祝使用顺利！
