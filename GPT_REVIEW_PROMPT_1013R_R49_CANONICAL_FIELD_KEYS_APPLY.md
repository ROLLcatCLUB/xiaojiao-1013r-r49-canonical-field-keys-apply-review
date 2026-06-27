# GPT Review Prompt: 1013R_R49_CANONICAL_FIELD_KEYS_APPLY

Please review this lightweight R49 package only for field-key application correctness. Do not review UI aesthetics.

## Review Target

R49 applies the R48 recovered canonical field ledger to the current R21 page copy and R45-R47 existing edit-card bridge.

## Required Checks

1. Confirm the current R21 page copy has 12 edit items in `r6p-section-edit-data`.
2. Confirm all 12 edit items have `canonical_field_key`.
3. Confirm these 6 short IDs have `explicit_alias_of`:
   - `unit_info -> unit_basic_info`
   - `core_literacy -> core_literacy_goals`
   - `student_start -> student_starting_point`
   - `knowledge_skills -> knowledge_and_skills`
   - `lesson_chain -> lesson_task_chain`
   - `materials_scaffolds -> skills_materials_scaffolds`
4. Confirm `material_requests` is present only as a material prompt field and has `formal_apply_allowed=false`.
5. Confirm the page has a material prompt marker: `data-canonical-field-key="material_requests"`.
6. Confirm R45-R47 candidate normalize requires `canonical_field_key`, `target_field_key`, and `explicit_alias_of`.
7. Confirm the validator proves a raw patch missing canonical keys is rejected.

## Expected Verdict

If all checks pass:

```text
R49 = PASS_CANONICAL_FIELD_KEYS_APPLIED_TO_CURRENT_PAGE_COPY
NEXT = R50_FIELD_AWARE_EDIT_CARD_VISIBLE_SMOKE
```

## Hard Boundaries

- Do not request a page rollback.
- Do not request a new static page.
- Do not ask to connect provider/model/runtime.
- Do not ask to write database/Feishu/memory.
- Do not treat R45-R47 as the field standard.
- Do not allow standalone blue candidate cards in the page body.
