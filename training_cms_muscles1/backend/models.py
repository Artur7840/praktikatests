from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class MuscleGroup(Base):
    __tablename__ = "muscle_group"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    photo_url = Column(String(500))
    parent_id = Column(Integer, ForeignKey("muscle_group.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    children = relationship("MuscleGroup", backref="parent", remote_side=[id])
    exercises = relationship("Exercise", back_populates="muscle_group")


class Exercise(Base):
    __tablename__ = "exercise"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    technique = Column(Text)
    difficulty = Column(String(20), default="medium")
    photo_url = Column(String(500))
    muscle_group_id = Column(Integer, ForeignKey("muscle_group.id"), nullable=False)
    
    # Поля для наследования (TPH)
    type = Column(String(20), default="strength")  # strength, cardio, stretching
    
    # Силовые
    default_sets = Column(Integer)
    default_reps = Column(Integer)
    default_weight = Column(Float)
    
    # Кардио
    default_duration_min = Column(Integer)
    default_distance_km = Column(Float)
    default_calories = Column(Integer)
    
    # Растяжка
    default_duration_sec = Column(Integer)
    
    # Версионирование
    current_version_id = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    muscle_group = relationship("MuscleGroup", back_populates="exercises")
    versions = relationship("ExerciseVersion", back_populates="exercise")
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    favorites = relationship("Favorite", back_populates="exercise")


class ExerciseVersion(Base):
    __tablename__ = "exercise_version"
    
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    valid_from = Column(DateTime, default=datetime.utcnow)
    
    # Снапшот всех полей упражнения
    name = Column(String(200), nullable=False)
    description = Column(Text)
    technique = Column(Text)
    difficulty = Column(String(20), default="medium")
    photo_url = Column(String(500))
    muscle_group_id = Column(Integer, nullable=False)
    type = Column(String(20), default="strength")
    default_sets = Column(Integer)
    default_reps = Column(Integer)
    default_weight = Column(Float)
    default_duration_min = Column(Integer)
    default_distance_km = Column(Float)
    default_calories = Column(Integer)
    default_duration_sec = Column(Integer)
    is_current = Column(Boolean, default=False)
    
    # Связи
    exercise = relationship("Exercise", back_populates="versions")


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    role = Column(String(20), default="student")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    workouts = relationship("Workout", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")


class Workout(Base):
    __tablename__ = "workout"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="workouts")
    workout_exercises = relationship("WorkoutExercise", back_populates="workout")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercise"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workout.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    sets = Column(Integer, default=3)
    reps = Column(Integer, default=10)
    weight = Column(Float)
    order = Column(Integer, default=0)
    
    # Связи
    workout = relationship("Workout", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    logs = relationship("WorkoutLog", back_populates="workout_exercise")


class WorkoutLog(Base):
    __tablename__ = "workout_log"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_exercise_id = Column(Integer, ForeignKey("workout_exercise.id"), nullable=False)
    set_number = Column(Integer)
    reps_done = Column(Integer)
    weight_used = Column(Float)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    workout_exercise = relationship("WorkoutExercise", back_populates="logs")


class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="favorites")
    exercise = relationship("Exercise", back_populates="favorites")
