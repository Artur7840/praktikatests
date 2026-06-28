from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ---------- Muscle Group ----------
class MuscleGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    parent_id: Optional[int] = None

class MuscleGroupCreate(MuscleGroupBase):
    pass

class MuscleGroupOut(MuscleGroupBase):
    id: int
    created_at: datetime
    children: List['MuscleGroupOut'] = []

# ---------- Exercise ----------
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    technique: Optional[str] = None
    difficulty: str = "medium"
    photo_url: Optional[str] = None
    muscle_group_id: int
    type: str = "strength"  # strength, cardio, stretching
    
    # Силовые
    default_sets: Optional[int] = None
    default_reps: Optional[int] = None
    default_weight: Optional[float] = None
    
    # Кардио
    default_duration_min: Optional[int] = None
    default_distance_km: Optional[float] = None
    default_calories: Optional[int] = None
    
    # Растяжка
    default_duration_sec: Optional[int] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(ExerciseBase):
    pass

class ExerciseOut(ExerciseBase):
    id: int
    current_version_id: Optional[int] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

class ExerciseVersionOut(BaseModel):
    id: int
    exercise_id: int
    version_number: int
    valid_from: datetime
    name: str
    description: Optional[str]
    technique: Optional[str]
    difficulty: str
    photo_url: Optional[str]
    muscle_group_id: int
    type: str
    default_sets: Optional[int]
    default_reps: Optional[int]
    default_weight: Optional[float]
    default_duration_min: Optional[int]
    default_distance_km: Optional[float]
    default_calories: Optional[int]
    default_duration_sec: Optional[int]
    is_current: bool

# ---------- Workout ----------
class WorkoutExerciseBase(BaseModel):
    exercise_id: int
    sets: int = 3
    reps: int = 10
    weight: Optional[float] = None

class WorkoutCreate(BaseModel):
    name: str
    exercises: List[WorkoutExerciseBase]

class WorkoutOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    exercises: List[dict]

class WorkoutLogCreate(BaseModel):
    set_number: int
    reps_done: int
    weight_used: float

# ---------- User ----------
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Для рекурсивных ссылок
MuscleGroupOut.update_forward_refs()
