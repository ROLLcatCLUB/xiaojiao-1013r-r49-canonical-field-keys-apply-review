# 1013R_R49_CANONICAL_FIELD_KEYS_APPLY GitHub Review

This is a lightweight independent GPT review package. It does not publish the full `xiaobei-core` workspace.

## Scope

R49 is the implementation step after R48:

- R48 restored the field authority ledger.
- R49 applies canonical field keys to the current R21 page copy and tightens the R45-R47 candidate normalization gate.

R49 is not a new static page. The current carrier is still the R21 page copy.

## What Changed

- The current R21 `r6p-section-edit-data` now has 12 edit items.
- Every edit item has `canonical_field_key`.
- The 6 short page IDs keep `current_alias` and have explicit `explicit_alias_of`.
- `material_requests` is restored as a material prompt field only.
- The material prompt DOM carries `data-canonical-field-key="material_requests"`.
- R45-R47 `field_patch_candidates` must carry `canonical_field_key`, `target_field_key`, and `explicit_alias_of`.
- A raw patch missing canonical keys is rejected by normalize before it can enter the existing edit-card bridge.

## Validation Summary

`validate_1013R_R49_canonical_field_keys_apply.py` passes.

- `page_edit_item_count=12`
- `canonical_field_count=12`
- `alias_count=6`
- `material_requests_present=true`
- `material_prompt_marker_present=true`
- `missing_canonical_raw_patch_rejected=true`
- `orphan_ui=0`

## Boundaries

- `do_not_rollback_r21=true`
- `do_not_create_new_page=true`
- `do_not_modify_r36=true`
- `provider_model_call_allowed=false`
- `runtime_integration_allowed=false`
- `database_write_allowed=false`
- `feishu_write_allowed=false`
- `memory_write_allowed=false`
- `formal_apply_allowed=false`
- `standalone_blue_card_allowed=false`

R45-R47 remains an existing edit-card bridge only. It is not a field standard.

## Must-Review Files

- `GPT_REVIEW_PROMPT_1013R_R49_CANONICAL_FIELD_KEYS_APPLY.md`
- `REVIEW_PACKAGE_MANIFEST.md`
- `artifacts/validate_1013R_R49_canonical_field_keys_apply_result.json`
- `artifacts/prep_room_page_copy_binds_unified_package_1013R_R21_R49.html`
- `validators/apply_1013R_R49_canonical_field_keys_to_page.py`
- `validators/validate_1013R_R49_canonical_field_keys_apply.py`
- `source_refs/prep_room_in_page_model_quality_loop_1013R_R45_R47.py`
- `r48_refs/prep_room_recovered_field_ledger_1013R_R48.json`
- `r48_refs/prep_room_current_page_field_diff_1013R_R48.json`
- `r48_refs/prep_room_field_to_edit_card_bridge_1013R_R48.json`
