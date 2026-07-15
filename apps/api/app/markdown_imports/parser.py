import re
from dataclasses import dataclass, field
from datetime import date

from markdown_it import MarkdownIt


@dataclass(frozen=True)
class ParsedWarning:
    code: str
    field: str | None
    source: str | None
    message: str


@dataclass(frozen=True)
class ParsedMarkdown:
    report_type: str
    period_from: date | None
    period_to: date | None
    work_detail: str | None
    achievements: str | None
    technologies: str | None
    difficulties: str | None
    improvements: str | None
    member_comment: str | None
    manager_comment: str | None
    member_name: str | None
    project_name: str | None
    warnings: list[ParsedWarning] = field(default_factory=list)


HEADINGS = {
    "メンバー名": "member_name",
    "案件名": "project_name",
    "報告種別": "report_type",
    "対象期間": "period",
    "実施内容": "work_detail",
    "成果": "achievements",
    "課題・苦労": "difficulties",
    "工夫・改善": "improvements",
    "使用技術": "technologies",
    "本人コメント": "member_comment",
    "上司コメント": "manager_comment",
}
REPORT_TYPES = {"定期報告": "periodic", "終了報告": "final", "任意報告": "ad_hoc"}


def parse_markdown(content: str) -> ParsedMarkdown:
    tokens = MarkdownIt("commonmark").parse(content)
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            title = tokens[index + 1].content.strip() if index + 1 < len(tokens) else ""
            current = HEADINGS.get(title)
            if current:
                sections.setdefault(current, [])
        elif index > 0 and tokens[index - 1].type == "heading_open":
            continue
        elif current and token.type in {"inline", "fence", "code_block"}:
            text = token.content.strip()
            if text:
                sections[current].append(text)

    values = {key: _clean("\n".join(parts)) for key, parts in sections.items()}
    warnings: list[ParsedWarning] = []
    raw_type = values.get("report_type")
    report_type = REPORT_TYPES.get(raw_type or "")
    if report_type is None:
        report_type = "ad_hoc"
        warnings.append(
            ParsedWarning(
                "INVALID_REPORT_TYPE",
                "report_type",
                raw_type,
                "報告種別を判定できないため任意報告として保存しました。",
            )
        )

    start, end = _period(values.get("period"))
    if start is None or end is None:
        warnings.append(
            ParsedWarning(
                "INVALID_PERIOD",
                "period",
                values.get("period"),
                "対象期間をISO 8601形式で判定できませんでした。",
            )
        )
    return ParsedMarkdown(
        report_type=report_type,
        period_from=start,
        period_to=end,
        work_detail=values.get("work_detail"),
        achievements=values.get("achievements"),
        technologies=values.get("technologies"),
        difficulties=values.get("difficulties"),
        improvements=values.get("improvements"),
        member_comment=values.get("member_comment"),
        manager_comment=values.get("manager_comment"),
        member_name=values.get("member_name"),
        project_name=values.get("project_name"),
        warnings=warnings,
    )


def _clean(value: str) -> str | None:
    lines = [line.strip().removeprefix("-").strip() for line in value.splitlines()]
    value = "\n".join(line for line in lines if line)
    return value or None


def _period(value: str | None) -> tuple[date | None, date | None]:
    if not value:
        return None, None
    found = re.findall(r"\d{4}-\d{2}-\d{2}", value)
    if len(found) != 2:
        return None, None
    try:
        return date.fromisoformat(found[0]), date.fromisoformat(found[1])
    except ValueError:
        return None, None
