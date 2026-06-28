from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend import models, schemas
from typing import List, Optional
from datetime import datetime

# ---------- Muscle Groups ----------
def create_muscle_group(db: Session, data: schemas.MuscleGroupCreate) -> models.MuscleGroup:
    db_item = models.MuscleGroup(**data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_muscle_groups_tree(db: Session, parent_id: Optional[int] = None) -> List[models.MuscleGroup]:
    query = db.query(models.MuscleGroup).filter(models.MuscleGroup.parent_id == parent_id)
    groups = query.all()
    for group in groups:
        group.children = get_muscle_groups_tree(db, group.id)
    return groups

# ---------- Exercises ----------
def create_exercise(db: Session, data: schemas.ExerciseCreate) -> models.Exercise:
    db_item = models.Exercise(**data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_exercise(db: Session, exercise_id: int) -> Optional[models.Exercise]:
    return db.query(models.Exercise).filter(
        models.Exercise.id == exercise_id,
        models.Exercise.is_deleted == False
    ).first()

def get_exercises(db: Session, muscle_group_id: Optional[int] = None, type_filter: Optional[str] = None) -> List[models.Exercise]:
    query = db.query(models.Exercise).filter(models.Exercise.is_deleted == False)
    if muscle_group_id:
        query = query.filter(models.Exercise.muscle_group_id == muscle_group_id)
    if type_filter:
        query = query.filter(models.Exercise.type == type_filter)
    return query.all()

def update_exercise(db: Session, exercise_id: int, data: schemas.ExerciseUpdate) -> Optional[models.Exercise]:
    db_item = get_exercise(db, exercise_id)
    if not db_item:
        return None
    for key, value in data.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_exercise(db: Session, exercise_id: int) -> bool:
    db_item = get_exercise(db, exercise_id)
    if not db_item:
        return False
    db_item.is_deleted = True
    db.commit()
    return True

def get_exercise_versions(db: Session, exercise_id: int) -> List[models.ExerciseVersion]:
    return db.query(models.ExerciseVersion).filter(
        models.ExerciseVersion.exercise_id == exercise_id
    ).order_by(models.ExerciseVersion.version_number).all()

def get_version(db: Session, version_id: int) -> Optional[models.ExerciseVersion]:
    return db.query(models.ExerciseVersion).filter(models.ExerciseVersion.id == version_id).first()

# ---------- Workouts ----------
def create_workout(db: Session, user_id: int, data: schemas.WorkoutCreate) -> models.Workout:
    db_workout = models.Workout(name=data.name, user_id=user_id)
    db.add(db_workout)
    db.flush()
    
    for idx, ex in enumerate(data.exercises):
        db_we = models.WorkoutExercise(
            workout_id=db_workout.id,
            exercise_id=ex.exercise_id,
            sets=ex.sets,
            reps=ex.reps,
            weight=ex.weight,
            order=idx
        )
        db.add(db_we)
    
    db.commit()
    db.refresh(db_workout)
    return db_workout

def get_user_workouts(db: Session, user_id: int) -> List[models.Workout]:
    return db.query(models.Workout).filter(
        models.Workout.user_id == user_id
    ).order_by(models.Workout.created_at.desc()).all()

def get_workout(db: Session, workout_id: int, user_id: int) -> Optional[models.Workout]:
    return db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == user_id
    ).first()

def delete_workout(db: Session, workout_id: int, user_id: int) -> bool:
    db_item = get_workout(db, workout_id, user_id)
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True

# ---------- Workout Log ----------
def log_set(db: Session, workout_exercise_id: int, data: schemas.WorkoutLogCreate) -> models.WorkoutLog:
    db_log = models.WorkoutLog(
        workout_exercise_id=workout_exercise_id,
        set_number=data.set_number,
        reps_done=data.reps_done,
        weight_used=data.weight_used
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# ---------- Favorites ----------
def add_favorite(db: Session, user_id: int, exercise_id: int) -> models.Favorite:
    db_fav = models.Favorite(user_id=user_id, exercise_id=exercise_id)
    db.add(db_fav)
    db.commit()
    db.refresh(db_fav)
    return db_fav

def remove_favorite(db: Session, user_id: int, exercise_id: int) -> bool:
    db_item = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.exercise_id == exercise_id
    ).first()
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True

def get_user_favorites(db: Session, user_id: int) -> List[models.Favorite]:
    return db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id
    ).all()
