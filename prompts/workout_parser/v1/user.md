Task: Extract a **single Program** object (with nested Workouts → Exercises → Sets) from the attached PDF provided as an input file.

Constraints & policy
- Output must be **one JSON object** that validates against the provided Pydantic schema (Structured Outputs).
- If the document is too long for a single pass, return a **partial** Program and add this to `program.notes`:
  "Truncated due to context; remaining pages require a second pass."
- Infer the **program name** from the clearest header; if unclear, fall back to the source PDF filename without extension.
- **Workout boundaries**: Use headings like "Week 1 — Push", "Day 3 – Shoulders & Legs", "Base Session A1", or obvious day rows in tables to start a new workout. If uncertain, **merge into the current workout** conservatively.
- **Scheduling**: If a rotation (e.g., `["Push","Pull","Legs","Rest"]`) is apparent, set `schedule.rotation`. If weekdays are explicit, set `schedule.calendar_map`. If both are clear, include both.
- **Schemes**: Prefer known scheme types (`fixed`, `range`, `percent`, `rpe`, `amrap`, `mrs`, `cluster`, `drop_set`, `emom`, `timed_hold`, `rest_pause`, `myo_reps`, `widowmaker`) before `custom`.
- **Units**: Preserve source units per set/exercise; do not convert.
- **Narrative-only pages**: If a page obviously represents a workout day but lacks explicit exercises, create a **workout with zero exercises** and add the salient instructions to `workout.notes`.

Output shape
- Program → Workouts → Exercises → SetPrescription(s) with a discriminated `scheme.type`.

Edge-case guidance (examples; adapt only if present)
- Spreadsheet day rows (e.g., CAP3) with AMRAP/MRS/EMOM legends → map to `amrap` / `mrs` / `emom`.
- DC/MD style rest-pause or loaded stretches → `rest_pause` or `timed_hold`.
- 20+ rep “widowmaker” sets → `widowmaker`.

Return: **only** the JSON object. No commentary.
