from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

# Переключение между ORM и Native SQL
USE_ORM = os.environ.get('USE_ORM', 'True').lower() == 'true'

# Импорты для ORM
from backend.database import get_db as get_orm_db
from backend import crud_orm

# Импорты для Native SQL
from backend.db import query_one, query_all, execute

def get_crud():
    if USE_ORM:
        return crud_orm
    else:
        # Для Native SQL используем функции из db.py и отдельные обёртки
        return None  # будет использоваться напрямую

# ---------- Muscle Groups ----------
def get_muscle_groups():
    if USE_ORM:
        db = next(get_orm_db())
        groups = crud_orm.get_muscle_groups_tree(db)
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'description': g.description,
            'photo_url': g.photo_url,
            'children': [{'id': c.id, 'name': c.name} for c in g.children]
        } for g in groups])
    else:
        rows = query_all('SELECT id, name, photo_url FROM muscle_group WHERE parent_id IS NULL')
        return jsonify([dict(row) for row in rows])

# ---------- Exercises ----------
def get_exercises():
    muscle_id = request.args.get('muscle', type=int)
    type_filter = request.args.get('type', type=str)
    
    if USE_ORM:
        db = next(get_orm_db())
        exercises = crud_orm.get_exercises(db, muscle_id, type_filter)
        return jsonify([{
            'id': ex.id,
            'name': ex.name,
            'description': ex.description,
            'difficulty': ex.difficulty,
            'photo_url': ex.photo_url,
            'muscle_group_id': ex.muscle_group_id,
            'type': ex.type
        } for ex in exercises])
    else:
        sql = 'SELECT id, name, difficulty, photo_url, muscle_group_id, description FROM exercise WHERE is_deleted = false'
        params = []
        if muscle_id:
            sql += ' AND muscle_group_id = %s'
            params.append(muscle_id)
        if type_filter:
            sql += ' AND type = %s'
            params.append(type_filter)
        rows = query_all(sql, tuple(params))
        return jsonify([dict(row) for row in rows])

def get_exercise(exercise_id):
    version = request.args.get('version', type=int)
    
    if USE_ORM:
        db = next(get_orm_db())
        if version:
            ex = crud_orm.get_version(db, version)
            if not ex:
                return jsonify({'msg': 'Version not found'}), 404
            return jsonify(dict(ex))
        else:
            ex = crud_orm.get_exercise(db, exercise_id)
            if not ex:
                return jsonify({'msg': 'Not found'}), 404
            return jsonify({
                'id': ex.id,
                'name': ex.name,
                'description': ex.description,
                'technique': ex.technique,
                'difficulty': ex.difficulty,
                'photo_url': ex.photo_url,
                'muscle_group_id': ex.muscle_group_id,
                'type': ex.type,
                'default_sets': ex.default_sets,
                'default_reps': ex.default_reps,
                'default_weight': ex.default_weight
            })
    else:
        sql = 'SELECT id, name, description, technique, difficulty, photo_url, muscle_group_id FROM exercise WHERE id = %s AND is_deleted = false'
        row = query_one(sql, (exercise_id,))
        if not row:
            return jsonify({'msg': 'Not found'}), 404
        return jsonify(dict(row))

def get_exercise_versions(exercise_id):
    if USE_ORM:
        db = next(get_orm_db())
        versions = crud_orm.get_exercise_versions(db, exercise_id)
        return jsonify([dict(v) for v in versions])
    else:
        rows = query_all('SELECT * FROM exercise_version WHERE exercise_id = %s ORDER BY version_number', (exercise_id,))
        return jsonify([dict(row) for row in rows])

def get_version_by_id(version_id):
    if USE_ORM:
        db = next(get_orm_db())
        version = crud_orm.get_version(db, version_id)
        if not version:
            return jsonify({'msg': 'Version not found'}), 404
        return jsonify(dict(version))
    else:
        row = query_one('SELECT * FROM exercise_version WHERE id = %s', (version_id,))
        if not row:
            return jsonify({'msg': 'Version not found'}), 404
        return jsonify(dict(row))

# ---------- Workouts ----------
@jwt_required()
def create_workout():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get('name')
    exercises_data = data.get('exercises', [])
    
    if not name:
        return jsonify({'msg': 'Workout name required'}), 400
    if not exercises_data:
        return jsonify({'msg': 'At least one exercise required'}), 400
    
    if USE_ORM:
        from backend.schemas import WorkoutCreate, WorkoutExerciseBase
        exercises = [WorkoutExerciseBase(**ex) for ex in exercises_data]
        workout_data = WorkoutCreate(name=name, exercises=exercises)
        db = next(get_orm_db())
        workout = crud_orm.create_workout(db, user_id, workout_data)
        return jsonify({'id': workout.id, 'msg': 'Workout created'}), 201
    else:
        workout_id = execute('INSERT INTO workout (name, user_id) VALUES (%s, %s) RETURNING id', (name, user_id))
        for idx, ex in enumerate(exercises_data):
            execute('''INSERT INTO workout_exercise (workout_id, exercise_id, sets, reps, weight, "order")
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (workout_id, ex['exercise_id'], ex.get('sets', 3), ex.get('reps', 10), ex.get('weight'), idx))
        return jsonify({'id': workout_id, 'msg': 'Workout created'}), 201

@jwt_required()
def get_my_workouts():
    user_id = int(get_jwt_identity())
    
    if USE_ORM:
        db = next(get_orm_db())
        workouts = crud_orm.get_user_workouts(db, user_id)
        return jsonify([{
            'id': w.id,
            'name': w.name,
            'created_at': w.created_at
        } for w in workouts])
    else:
        rows = query_all('SELECT id, name, created_at FROM workout WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
        return jsonify([dict(row) for row in rows])

@jwt_required()
def get_workout(workout_id):
    user_id = int(get_jwt_identity())
    
    if USE_ORM:
        db = next(get_orm_db())
        workout = crud_orm.get_workout(db, workout_id, user_id)
        if not workout:
            return jsonify({'msg': 'Unauthorized'}), 403
        return jsonify({
            'id': workout.id,
            'name': workout.name,
            'exercises': [{
                'id': we.id,
                'exercise_id': we.exercise_id,
                'name': we.exercise.name,
                'photo_url': we.exercise.photo_url,
                'sets': we.sets,
                'reps': we.reps,
                'weight': we.weight,
                'order': we.order
            } for we in workout.workout_exercises]
        })
    else:
        workout = query_one('SELECT id, name, user_id FROM workout WHERE id = %s', (workout_id,))
        if not workout or workout['user_id'] != user_id:
            return jsonify({'msg': 'Unauthorized'}), 403
        we_rows = query_all('''
            SELECT we.id, we.sets, we.reps, we.weight, we."order",
                   e.id as exercise_id, e.name, e.photo_url
            FROM workout_exercise we
            JOIN exercise e ON we.exercise_id = e.id
            WHERE we.workout_id = %s
            ORDER BY we."order"
        ''', (workout_id,))
        return jsonify({
            'id': workout['id'],
            'name': workout['name'],
            'exercises': [dict(row) for row in we_rows]
        })

@jwt_required()
def log_set(workout_exercise_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if USE_ORM:
        db = next(get_orm_db())
        from backend.schemas import WorkoutLogCreate
        log_data = WorkoutLogCreate(**data)
        crud_orm.log_set(db, workout_exercise_id, log_data)
        return jsonify({'msg': 'Set logged'}), 201
    else:
        we = query_one('''
            SELECT we.id FROM workout_exercise we
            JOIN workout w ON we.workout_id = w.id
            WHERE we.id = %s AND w.user_id = %s
        ''', (workout_exercise_id, user_id))
        if not we:
            return jsonify({'msg': 'Unauthorized'}), 403
        execute('''INSERT INTO workout_log (workout_exercise_id, set_number, reps_done, weight_used)
                   VALUES (%s, %s, %s, %s)''',
                (workout_exercise_id, data.get('set_number'), data.get('reps_done'), data.get('weight_used')))
        return jsonify({'msg': 'Set logged'}), 201

@jwt_required()
def delete_workout(workout_id):
    user_id = int(get_jwt_identity())
    
    if USE_ORM:
        db = next(get_orm_db())
        if crud_orm.delete_workout(db, workout_id, user_id):
            return jsonify({'msg': 'Workout deleted'}), 200
        return jsonify({'msg': 'Workout not found'}), 404
    else:
        workout = query_one('SELECT id FROM workout WHERE id = %s AND user_id = %s', (workout_id, user_id))
        if not workout:
            return jsonify({'msg': 'Workout not found or unauthorized'}), 404
        execute('DELETE FROM workout WHERE id = %s', (workout_id,))
        return jsonify({'msg': 'Workout deleted'}), 200

# ---------- Favorites ----------
@jwt_required()
def add_favorite():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    exercise_id = data.get('exercise_id')
    
    if USE_ORM:
        db = next(get_orm_db())
        crud_orm.add_favorite(db, user_id, exercise_id)
        return jsonify({'msg': 'Added to favorites'}), 201
    else:
        execute('INSERT INTO favorites (user_id, exercise_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (user_id, exercise_id))
        return jsonify({'msg': 'Added to favorites'}), 201

@jwt_required()
def remove_favorite(exercise_id):
    user_id = int(get_jwt_identity())
    
    if USE_ORM:
        db = next(get_orm_db())
        if crud_orm.remove_favorite(db, user_id, exercise_id):
            return jsonify({'msg': 'Removed from favorites'}), 200
        return jsonify({'msg': 'Not found'}), 404
    else:
        execute('DELETE FROM favorites WHERE user_id = %s AND exercise_id = %s', (user_id, exercise_id))
        return jsonify({'msg': 'Removed from favorites'}), 200

@jwt_required()
def get_favorites():
    user_id = int(get_jwt_identity())
    
    if USE_ORM:
        db = next(get_orm_db())
        favorites = crud_orm.get_user_favorites(db, user_id)
        return jsonify([{
            'id': f.id,
            'exercise_id': f.exercise_id,
            'name': f.exercise.name,
            'photo_url': f.exercise.photo_url,
            'added_at': f.added_at
        } for f in favorites])
    else:
        rows = query_all('''
            SELECT f.id, f.exercise_id, f.added_at, e.name, e.photo_url
            FROM favorites f
            JOIN exercise e ON f.exercise_id = e.id
            WHERE f.user_id = %s
        ''', (user_id,))
        return jsonify([dict(row) for row in rows])


