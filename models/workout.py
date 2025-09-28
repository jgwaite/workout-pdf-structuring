# Python 3.13, Pydantic v2

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field


# -------------------------------
# Shared / utility
# -------------------------------

class Link(BaseModel):
    """Simple hyperlink to a resource (e.g., form demo, YouTube)."""
    text: str
    url: str


class Load(BaseModel):
    """Typed load to reduce schema ambiguity."""
    unit: Literal["lb", "kg"]
    value: float = Field(..., gt=0)


# -------------------------------
# Scheme variants (discriminated union)
# -------------------------------

class FixedScheme(BaseModel):
    type: Literal["fixed"]
    sets: int = Field(..., ge=1)
    reps: int = Field(..., ge=1)
    load: Optional[Load] = None


class RangeScheme(BaseModel):
    type: Literal["range"]
    sets: int = Field(..., ge=1)
    reps_min: int = Field(..., ge=1)
    reps_max: int = Field(..., ge=1)
    load: Optional[Load] = None


class PercentScheme(BaseModel):
    type: Literal["percent"]
    sets: int = Field(..., ge=1)
    reps: int = Field(..., ge=1)
    percent_1rm: float = Field(..., ge=0.0, le=1.0)


class RPEScheme(BaseModel):
    type: Literal["rpe"]
    sets: int = Field(..., ge=1)
    reps: int = Field(..., ge=1)
    target_rpe: float = Field(..., ge=5.0, le=10.0)


class AmrapScheme(BaseModel):
    type: Literal["amrap"]
    base_sets: int = Field(..., ge=1)
    base_reps: int = Field(..., ge=1)
    amrap_last_set: Optional[bool] = None
    load: Optional[Load] = None


class MRSScheme(BaseModel):
    """Minimum Rep Set (e.g., CAP3-style with EMOM continuation)."""
    type: Literal["mrs"]
    target_reps_min: int = Field(..., ge=1)
    load: Optional[Load] = None
    emom_until_reps: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = None


class ClusterScheme(BaseModel):
    type: Literal["cluster"]
    sets: int = Field(..., ge=1)
    work_set_pattern: str  # e.g., "8,5,4,3"
    intra_rest_s: int = Field(..., ge=5)


class DropSetScheme(BaseModel):
    type: Literal["drop_set"]
    sets: int = Field(..., ge=1)
    drops: int = Field(..., ge=1)
    drop_frac: Optional[float] = Field(default=None, ge=0.05, le=0.5)


class EmomScheme(BaseModel):
    type: Literal["emom"]
    minutes: int = Field(..., ge=1)
    reps_per_min: int = Field(..., ge=1)
    load: Optional[Load] = None


class TimedHoldScheme(BaseModel):
    """Use this for stretches/loaded stretches, static holds, vacuums, etc."""
    type: Literal["timed_hold"]
    sets: int = Field(..., ge=1)
    duration_s: int = Field(..., ge=5)


class RestPauseScheme(BaseModel):
    """Rest-pause cluster: near-failure first set, short rests, then mini-sets."""
    type: Literal["rest_pause"]
    sets: int = Field(..., ge=1)  # number of rest-pause clusters
    first_set_reps: Optional[int] = Field(default=None, ge=1)
    mini_reps: Optional[int] = Field(default=None, ge=1)
    mini_sets: Optional[int] = Field(default=None, ge=1)
    rest_between_mini_s: int = Field(default=20, ge=5, le=60)
    target_total_reps: Optional[int] = Field(default=None, ge=1)
    load: Optional[Load] = None
    notes: Optional[str] = None


class MyoRepsScheme(BaseModel):
    """Myo-reps: activation set + repeated short-rest mini-sets."""
    type: Literal["myo_reps"]
    activation_reps: int = Field(..., ge=1)
    mini_reps: int = Field(..., ge=1)
    mini_sets: Optional[int] = Field(default=None, ge=1)
    rest_between_mini_s: int = Field(default=20, ge=5, le=60)
    termination_criteria: Optional[str] = None
    load: Optional[Load] = None
    notes: Optional[str] = None


class WidowmakerScheme(BaseModel):
    """20+ rep ‘widowmaker’ style sets."""
    type: Literal["widowmaker"]
    sets: int = Field(default=1, ge=1)
    target_reps_min: int = Field(default=20, ge=10)
    to_failure: bool = True
    load: Optional[Load] = None
    notes: Optional[str] = None


class SchemeParameter(BaseModel):
    """Key–value parameter used to describe custom scheme settings."""

    key: str
    value_str: Optional[str] = None
    value_num: Optional[float] = None
    value_bool: Optional[bool] = None


class CustomScheme(BaseModel):
    """
    Escape hatch for unknown/new schemes using a list of typed parameters.
    Example:
      {"type":"custom","name":"my-protocol",
       "parameters":[{"key":"bout","value_num":4},{"key":"rest_s","value_num":10}]}
    """

    type: Literal["custom"]
    name: str
    parameters: List[SchemeParameter] = Field(default_factory=list)
    description: Optional[str] = None


ExerciseScheme = Union[
    FixedScheme,
    RangeScheme,
    PercentScheme,
    RPEScheme,
    AmrapScheme,
    MRSScheme,
    ClusterScheme,
    DropSetScheme,
    EmomScheme,
    TimedHoldScheme,
    RestPauseScheme,
    MyoRepsScheme,
    WidowmakerScheme,
    CustomScheme,
]


# -------------------------------
# Workout objects
# -------------------------------

class SetPrescription(BaseModel):
    """
    A single set (or block of identical sets) with a scheme.
    Lets an exercise mix protocols (e.g., Top set = AMRAP; Backoffs = percent).
    """
    label: Optional[str] = Field(default=None, description="e.g. 'Warmup', 'Top', 'Backoff 1'")
    scheme: ExerciseScheme
    rest_seconds: Optional[int] = Field(default=None, ge=10, le=600)
    cues: Optional[List[str]] = None


class Exercise(BaseModel):
    ordinal: int = Field(..., ge=1)
    name: str
    tags: Optional[List[str]] = None                # e.g., ["primary","chest"]
    sets: List[SetPrescription]                     # set-level protocols
    links: Optional[List[Link]] = None
    superset_with: Optional[int] = Field(default=None, ge=1)  # ordinal of paired exercise


class ReplacementMovement(BaseModel):
    """Optional swap-ins for core movements (e.g., if stalled or equipment)."""
    name: str
    sets: Optional[List[SetPrescription]] = None
    when_to_use: Optional[str] = None


class OptionalBlocks(BaseModel):
    replacement_movements: Optional[List[ReplacementMovement]] = None
    accessories_suggestions: Optional[List[str]] = None


class WorkoutMeta(BaseModel):
    title: str
    week: Optional[int] = Field(default=None, ge=1)
    day_name: Optional[str] = None                  # e.g., "Tuesday" or "Day 1"
    muscle_focus: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class Workout(BaseModel):
    type: Literal["workout"]
    workout_id: str
    meta: WorkoutMeta
    goals: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    exercises: List[Exercise]                       # can be empty if narrative-only day
    optional_blocks: Optional[OptionalBlocks] = None


# -------------------------------
# Program objects
# -------------------------------

class ProgramInfo(BaseModel):
    name: str
    author: Optional[str] = None
    version: str
    description: str
    philosophy: str
    notes: Optional[List[str]] = None


class WeekdayCalendarMap(BaseModel):
    Monday: Optional[str] = None
    Tuesday: Optional[str] = None
    Wednesday: Optional[str] = None
    Thursday: Optional[str] = None
    Friday: Optional[str] = None
    Saturday: Optional[str] = None
    Sunday: Optional[str] = None


class ProgramSchedule(BaseModel):
    """
    Use 'rotation' for sequences like PPL+Rest (no weekdays).
    Use 'calendar_map' to bind day names to weekdays for fixed weekly rhythms.
    """

    rotation: Optional[List[str]] = Field(
        default=None,
        description="e.g. ['Push','Pull','Legs','Rest']"
    )
    calendar_map: Optional[WeekdayCalendarMap] = None


class Calendar(BaseModel):
    weeks: int = Field(..., ge=1)
    repeatable: bool
    rest_guidance: str
    deload_rules: Optional[str] = None


class ProgressionSpec(BaseModel):
    """Concrete description of how to progress loads/volume."""

    increase_training_max_lb: Optional[float] = None
    decrease_training_max_pct: Optional[float] = Field(default=None, ge=0, le=1)
    per_week_add_lb: Optional[float] = None
    cap_weeks: Optional[int] = Field(default=None, ge=1)
    condition: Optional[str] = None


class ProgressionRule(BaseModel):
    """Structured progression logic applied to tagged exercises."""

    id: str
    applies_to_tags: Optional[List[str]] = None
    applies_to_exercises: Optional[List[str]] = None
    spec: ProgressionSpec
    notes: Optional[str] = None


class Globals(BaseModel):
    superset_conventions: Optional[str] = None
    warmup_guidance: Optional[str] = None
    accessory_policy: Optional[str] = None


class Program(BaseModel):
    """
    Final canonical object for a whole PDF.
    Contains the entire schedule and all workouts (no cross-refs/IDs needed elsewhere).
    """
    type: Literal["program"]
    program_id: str
    program: ProgramInfo
    split_overview: str
    schedule: Optional[ProgramSchedule] = None
    calendar: Calendar
    progression_rules: List[ProgressionRule]
    globals: Globals
    workouts: List[Workout]                        # <-- embedded full workouts
