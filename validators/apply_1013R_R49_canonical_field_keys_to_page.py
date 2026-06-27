from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = "1013R_R49_CANONICAL_FIELD_KEYS_APPLY_TO_CURRENT_PAGE_COPY"
R21_HTML = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R21_page_copy_binds_unified_package" / "prep_room_page_copy_binds_unified_package_1013R_R21.html"

ALIASES = {
    "unit_info": ("unit_basic_info", "unit_basic_info", "renamed"),
    "curriculum_basis": ("curriculum_basis", None, "rendered"),
    "core_literacy": ("core_literacy_goals", "core_literacy_goals", "renamed"),
    "student_start": ("student_starting_point", "student_starting_point", "renamed"),
    "unit_questions": ("unit_questions", None, "rendered"),
    "knowledge_skills": ("knowledge_and_skills", "knowledge_and_skills", "renamed"),
    "performance_task": ("performance_task", None, "rendered"),
    "learning_progression": ("learning_progression", None, "rendered"),
    "lesson_chain": ("lesson_task_chain", "lesson_task_chain", "renamed"),
    "assessment_evidence": ("assessment_evidence", None, "rendered"),
    "materials_scaffolds": ("skills_materials_scaffolds", "skills_materials_scaffolds", "renamed"),
}


def parse_edit_data(text: str) -> tuple[re.Match[str], list[dict]]:
    match = re.search(r'(<script id="r6p-section-edit-data" type="application/json">)(.*?)(</script>)', text, flags=re.S)
    if not match:
        raise RuntimeError("r6p-section-edit-data not found")
    payload = json.loads(match.group(2))
    if not isinstance(payload, list):
        raise RuntimeError("r6p-section-edit-data must be a list")
    return match, payload


def bind_item(item: dict) -> dict:
    item = dict(item)
    if item.get("id") not in ALIASES:
        return item
    canonical, explicit_alias_of, status = ALIASES[item["id"]]
    item.update(
        {
            "canonical_field_key": canonical,
            "current_alias": item["id"] if item["id"] != canonical else None,
            "explicit_alias_of": explicit_alias_of,
            "current_page_status": status,
            "field_authority_source": "1013I_R6N_R9A",
            "field_binding_stage": STAGE,
            "preview_only": True,
        }
    )
    return item


def material_requests_item() -> dict:
    return {
        "id": "material_requests",
        "title": "资料补充",
        "canonical_field_key": "material_requests",
        "current_alias": None,
        "explicit_alias_of": None,
        "current_page_status": "rendered_as_material_prompt",
        "field_authority_source": "1013I_R6N_R9A",
        "field_binding_stage": STAGE,
        "current": "缺教材目录、单元页、课时安排或示范图片时，只能生成临时预览。",
        "suggestion": "请先补教材材料或确认暂无材料；小教只能把缺口提示给老师，不写入正式课包。",
        "before": "资料缺口未进入字段账本。",
        "after": "资料补充作为缺材料提示字段出现，教师补齐或确认后再继续生成更稳定的大单元设计。",
        "impact": ["教材资料", "大屏素材", "课件图片", "学习单材料"],
        "view_note": "这里只提示缺资料和待确认项，不生成正式课包内容。",
        "teacher_intent": "补齐缺资料后再生成。",
        "why_this_change": "R48 确认 material_requests 是缺失 canonical 字段，R49 将其补回资料提示位。",
        "risk_note": "资料补充不能写入正式课包，也不能伪造教材、学生数据或图片来源。",
        "destination": "material_prompt_only",
        "preview_only": True,
        "formal_apply_allowed": False,
    }


def apply_html_markers(text: str) -> str:
    text = text.replace(
        '<section class="nb-material-front-prompt" aria-label="资料补充提示">',
        '<section class="nb-material-front-prompt" aria-label="资料补充提示" data-canonical-field-key="material_requests" data-r49-material-requests-prompt="true" data-formal-apply-allowed="false">',
    )
    if 'data-r49-canonical-field-bindings="true"' not in text:
        text = text.replace(
            'data-r6p-r2-lesson-style-modal="true" data-r6s-candidate-modal-preview="true"',
            'data-r6p-r2-lesson-style-modal="true" data-r49-canonical-field-bindings="true" data-r6s-candidate-modal-preview="true"',
            1,
        )
    return text


def main() -> None:
    text = R21_HTML.read_text(encoding="utf-8")
    match, items = parse_edit_data(text)
    rebound = [bind_item(item) for item in items if item.get("id") != "material_requests"]
    if not any(item.get("id") == "material_requests" for item in rebound):
        rebound.append(material_requests_item())
    new_payload = json.dumps(rebound, ensure_ascii=False)
    text = text[: match.start(2)] + new_payload + text[match.end(2) :]
    text = apply_html_markers(text)
    R21_HTML.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"stage": STAGE, "page_edit_item_count": len(rebound)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
