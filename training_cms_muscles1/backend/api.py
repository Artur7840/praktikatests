from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db import query_one, query_all, execute

def get_muscle_groups():
    rows = query_all('SELECT id, name, photo_url FROM muscle_group')
    return jsonify([dict(row) for row in rows])

def get_exercises():
    muscle_id = request.args.get('muscle', type=int)
    if muscle_id:
        rows = query_all('SELECT id, name, difficulty, photo_url, muscle_group_id, description FROM exercise WHERE muscle_group_id = %s', (muscle_id,))
    else:
        rows = query_all('SELECT id, name, difficulty, photo_url, muscle_group_id, description FROM exercise')
    return jsonify([dict(row) for row in rows])

def get_exercise(exercise_id):
    row = query_one('SELECT id, name, description, technique, difficulty, photo_url, muscle_group_id FROM exercise WHERE id = %s', (exercise_id,))
    if not row:
        return jsonify({'msg': 'Not found'}), 404
    return jsonify(dict(row))

@jwt_required()
def create_workout():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get('name')
    exercises = data.get('exercises', [])
    if not name:
        return jsonify({'msg': 'Workout name required'}), 400
    if not exercises:
        return jsonify({'msg': 'At least one exercise required'}), 400
    workout_id = execute('INSERT INTO workout (name, user_id) VALUES (%s, %s)', (name, user_id))
    for idx, ex in enumerate(exercises):
        execute('''INSERT INTO workout_exercise (workout_id, exercise_id, sets, reps, weight, "order")
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (workout_id, ex['exercise_id'], ex.get('sets', 3), ex.get('reps', 10), ex.get('weight'), idx))
    return jsonify({'id': workout_id, 'msg': 'Workout created'}), 201

@jwt_required()
def get_my_workouts():
    user_id = int(get_jwt_identity())
    rows = query_all('SELECT id, name, created_at FROM workout WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
    return jsonify([{'id': row['id'], 'name': row['name'], 'created_at': row['created_at']} for row in rows])

@jwt_required()
def get_workout(workout_id):
    user_id = int(get_jwt_identity())
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
    exercises_list = []
    for row in we_rows:
        exercises_list.append({
            'id': row['id'],
            'exercise_id': row['exercise_id'],
            'name': row['name'],
            'photo_url': row['photo_url'],
            'sets': row['sets'],
            'reps': row['reps'],
            'weight': row['weight'],
            'order': row['order']
        })
    return jsonify({'id': workout['id'], 'name': workout['name'], 'exercises': exercises_list})

@jwt_required()
def log_set(workout_exercise_id):
    user_id = int(get_jwt_identity())
    we = query_one('''
        SELECT we.id FROM workout_exercise we
        JOIN workout w ON we.workout_id = w.id
        WHERE we.id = %s AND w.user_id = %s
    ''', (workout_exercise_id, user_id))
    if not we:
        return jsonify({'msg': 'Unauthorized'}), 403
    data = request.get_json()
    execute('''INSERT INTO workout_log (workout_exercise_id, set_number, reps_done, weight_used)
               VALUES (%s, %s, %s, %s)''',
            (workout_exercise_id, data.get('set_number'), data.get('reps_done'), data.get('weight_used')))
    return jsonify({'msg': 'Set logged'}), 201

@jwt_required()
def delete_workout(workout_id):
    user_id = int(get_jwt_identity())
    workout = query_one('SELECT id FROM workout WHERE id = %s AND user_id = %s', (workout_id, user_id))
    if not workout:
        return jsonify({'msg': 'Workout not found or unauthorized'}), 404
    execute('DELETE FROM workout WHERE id = %s', (workout_id,))
    return jsonify({'msg': 'Workout deleted'}), 200
