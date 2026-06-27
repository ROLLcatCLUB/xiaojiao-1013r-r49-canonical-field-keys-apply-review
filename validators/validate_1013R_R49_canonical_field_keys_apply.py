from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE = "1013R_R49_CANONICAL_FIELD_KEYS_APPLY_TO_CURRENT_PAGE_COPY"
OUT_DIR = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R49_canonical_field_keys_apply_to_current_page_copy"
RESULT = OUT_DIR / "validate_1013R_R49_canonical_field_keys_apply_result.json"
REPORT = OUT_DIR / "prep_room_canonical_field_keys_apply_report_1013R_R49.md"

R21_HTML = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / "1013R_R21_page_copy_binds_unified_package" / "prep_room_page_copy_binds_unified_package_1013R_R21.html"
R45_R47_BACKEND = ROOT / "backend" / "xiaobei_ai" / "prep_room_in_page_model_quality_loop_1013R_R45_R47.py"

CANONICAL_FIELDS = {
    "unit_basic_info",
    "curriculum_basis",
    "core_literacy_goals",
    "student_starting_point",
    "unit_questions",
    "knowledge_and_skills",
    "performance_task",
    "learning_progression",
    "lesson_task_chain",
    "assessment_evidence",
    "skills_materials_scaffolds",
    "material_requests",
}

ALIASES = {
    "unit_info": "unit_basic_info",
    "core_literacy": "core_literacy_goals",
    "student_start": "student_starting_point",
    "knowledge_skills": "knowledge_and_skills",
    "lesson_chain": "lesson_task_chain",
    "materials_scaffolds": "skills_materials_scaffolds",
}


def parse_edit_data(html: str) -> list[dict]:
    match = re.search(r'<script id="r6p-section-edit-data" type="application/json">(.*?)</script>', html, flags=re.S)
    if not match:
        raise AssertionError("r6p-section-edit-data not found")
    data = json.loads(match.group(1))
    if not isinstance(data, list):
        raise AssertionError("r6p-section-edit-data must be a list")
    return data


def validate_page(errors: list[str]) -> dict:
    html = R21_HTML.read_text(encoding="utf-8")
    items = parse_edit_data(html)
    by_id = {item.get("id"): item for item in items}
    canonical_keys = [item.get("canonical_field_key") for item in items]

    if len(items) != 12:
        errors.append(f"expected 12 page edit items, got {len(items)}")
    if set(canonical_keys) != CANONICAL_FIELDS:
        errors.append("page edit items do not cover the 12 canonical fields")

    for item in items:
        item_id = item.get("id")
        canonical = item.get("canonical_field_key")
        if not canonical:
            errors.append(f"{item_id}: missing canonical_field_key")
        if canonical not in CANONICAL_FIELDS:
            errors.append(f"{item_id}: unknown canonical_field_key {canonical}")
        if item_id in ALIASES:
            expected = ALIASES[item_id]
            if canonical != expected:
                errors.append(f"{item_id}: expected canonical {expected}, got {canonical}")
            if item.get("explicit_alias_of") != expected:
                errors.append(f"{item_id}: missing explicit_alias_of {expected}")
            if item.get("current_alias") != item_id:
                errors.append(f"{item_id}: current_alias must preserve the page id")

    material = by_id.get("material_requests")
    if not material:
        errors.append("material_requests edit item missing")
    else:
        if material.get("canonical_field_key") != "material_requests":
            errors.append("material_requests must bind to canonical material_requests")
        if material.get("destination") != "material_prompt_only":
            errors.append("material_requests must remain material_prompt_only")
        if material.get("formal_apply_allowed") is not False:
            errors.append("material_requests must not allow formal apply")

    required_html_markers = [
        'data-r49-canonical-field-bindings="true"',
        'data-canonical-field-key="material_requests"',
        'data-r49-material-requests-prompt="true"',
        'data-shiwei-field-key',
        'data-explicit-alias-of',
    ]
    for marker in required_html_markers:
        if marker not in html:
            errors.append(f"HTML missing marker: {marker}")

    return {
        "page_edit_item_count": len(items),
        "canonical_field_count": len(set(canonical_keys)),
        "alias_count": sum(1 for item in items if item.get("id") in ALIASES),
        "material_requests_present": bool(material),
        "material_prompt_marker_present": 'data-r49-material-requests-prompt="true"' in html,
    }


def validate_backend(errors: list[str]) -> dict:
    source = R45_R47_BACKEND.read_text(encoding="utf-8")
    required_source_markers = [
        "CANONICAL_FIELD_BINDINGS",
        "canonical_field_key",
        "target_field_key",
        "explicit_alias_of",
        "_has_required_canonical_binding",
        "缺任一项会被拒绝进入页面编辑卡",
    ]
    for marker in required_source_markers:
        if marker not in source:
            errors.append(f"backend missing marker: {marker}")

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    module = importlib.import_module("backend.xiaobei_ai.prep_room_in_page_model_quality_loop_1013R_R45_R47")

    fallback_patch_count = 0
    fallback_missing_keys = []
    for candidate_type in [item["id"] for item in module.CANDIDATE_TYPES]:
        patches = module._fallback_field_patches(candidate_type, "候选内容", "原文")
        fallback_patch_count += len(patches)
        for patch in patches:
            for key in ("canonical_field_key", "target_field_key", "explicit_alias_of"):
                if not patch.get(key):
                    fallback_missing_keys.append(f"{candidate_type}:{patch.get('field_patch_id')}:{key}")
    if fallback_missing_keys:
        errors.append("fallback patches missing canonical keys: " + ", ".join(fallback_missing_keys))

    rejected_probe = {
        "field_patch_candidates": [
            {
                "field_patch_id": "probe_missing_canonical_keys",
                "target_section": "teaching_process",
                "target_step_id": "intro",
                "target_field": "teacher_action",
                "before_summary": "probe before",
                "after_candidate": "SHOULD_NOT_PASS_R49_REJECTION_PROBE",
            }
        ]
    }
    normalized = module._normalize_field_patches("teaching_process_cleanup", rejected_probe, "", "原文")
    rejected = all(patch.get("after_candidate") != "SHOULD_NOT_PASS_R49_REJECTION_PROBE" for patch in normalized)
    if not rejected:
        errors.append("raw patch without canonical keys passed normalize")
    if not normalized or not all(patch.get("canonical_field_key") for patch in normalized):
        errors.append("normalize fallback did not return canonical-bound patches")

    return {
        "fallback_patch_count": fallback_patch_count,
        "missing_canonical_raw_patch_rejected": rejected,
        "normalized_patch_count_after_probe": len(normalized),
    }


def write_outputs(errors: list[str], page_summary: dict, backend_summary: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "stage": STAGE,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {
            **page_summary,
            **backend_summary,
            "r21_html": str(R21_HTML.relative_to(ROOT)),
            "r45_r47_backend": str(R45_R47_BACKEND.relative_to(ROOT)),
        },
        "boundary": {
            "do_not_rollback_r21": True,
            "do_not_create_new_page": True,
            "do_not_modify_r36": True,
            "provider_model_call_allowed": False,
            "runtime_integration_allowed": False,
            "database_write_allowed": False,
            "feishu_write_allowed": False,
            "memory_write_allowed": False,
            "formal_apply_allowed": False,
            "standalone_blue_card_allowed": False,
        },
    }
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    REPORT.write_text(build_report(result), encoding="utf-8", newline="\n")


def build_report(result: dict) -> str:
    summary = result["summary"]
    return "\n".join(
        [
            f"# {STAGE}",
            "",
            "## 结论",
            "",
            f"状态：`{result['status']}`。",
            "",
            "R49 将 R48 字段账本实际绑定到当前 R21 页面副本和 R45-R47 既有编辑卡桥接。没有新开页面，没有接 provider/model/runtime，没有 formal apply。",
            "",
            "## 页面绑定",
            "",
            f"- 页面编辑项：{summary.get('page_edit_item_count')}",
            f"- canonical 字段覆盖：{summary.get('canonical_field_count')}",
            f"- alias/rebind 字段：{summary.get('alias_count')}",
            f"- material_requests 提示位：{summary.get('material_requests_present')}",
            f"- material prompt DOM marker：{summary.get('material_prompt_marker_present')}",
            "",
            "## R45-R47 候选约束",
            "",
            f"- fallback field patches：{summary.get('fallback_patch_count')}",
            f"- 缺 canonical key 的 raw patch 被拒绝：{summary.get('missing_canonical_raw_patch_rejected')}",
            f"- probe 后 normalize 返回 canonical fallback 数：{summary.get('normalized_patch_count_after_probe')}",
            "",
            "## 边界",
            "",
            "- `do_not_rollback_r21=true`",
            "- `do_not_create_new_page=true`",
            "- `do_not_modify_r36=true`",
            "- `provider_model_call_allowed=false`",
            "- `runtime_integration_allowed=false`",
            "- `formal_apply_allowed=false`",
            "- `standalone_blue_card_allowed=false`",
            "",
        ]
    )


def main() -> int:
    errors: list[str] = []
    page_summary = validate_page(errors)
    backend_summary = validate_backend(errors)
    write_outputs(errors, page_summary, backend_summary)
    print(f"1013R_R49 validation: {'PASS' if not errors else 'FAIL'}")
    print(json.dumps({"errors": errors, "summary": {**page_summary, **backend_summary}}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
