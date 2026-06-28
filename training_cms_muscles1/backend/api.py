from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.db import close_db
import os

# Переменная для переключения между ORM и Native SQL
USE_ORM = os.environ.get('USE_ORM', 'False').lower() == 'true'

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    JWTManager(app)
    app.teardown_appcontext(close_db)

    # Импорт всех функций из api.py
    from backend.auth import register, login
    from backend.api import (
        get_muscle_groups,
        get_exercises,
        get_exercise,
        create_exercise,        # 👈 POST
        update_exercise,        # 👈 PUT
        delete_exercise,        # 👈 DELETE
        get_exercise_versions,  # 👈 GET /versions
        get_version_by_id,      # 👈 GET /versions/{id}
        create_workout,
        get_my_workouts,
        get_workout,
        log_set,
        delete_workout,
        add_favorite,
        remove_favorite,
        get_favorites
    )

    # ---------- Аутентификация ----------
    app.add_url_rule('/api/register', view_func=register, methods=['POST'])
    app.add_url_rule('/api/login', view_func=login, methods=['POST'])

    # ---------- Группы мышц (иерархия) ----------
    app.add_url_rule('/api/muscle-groups', view_func=get_muscle_groups, methods=['GET'])

    # ---------- Упражнения (CRUD + версионирование) ----------
    app.add_url_rule('/api/exercises', view_func=get_exercises, methods=['GET'])
    app.add_url_rule('/api/exercises', view_func=create_exercise, methods=['POST'])        # CREATE
    app.add_url_rule('/api/exercises/<int:exercise_id>', view_func=get_exercise, methods=['GET'])          # READ
    app.add_url_rule('/api/exercises/<int:exercise_id>', view_func=update_exercise, methods=['PUT'])       # UPDATE
    app.add_url_rule('/api/exercises/<int:exercise_id>', view_func=delete_exercise, methods=['DELETE'])    # DELETE
    app.add_url_rule('/api/exercises/<int:exercise_id>/versions', view_func=get_exercise_versions, methods=['GET'])
    app.add_url_rule('/api/exercises/versions/<int:version_id>', view_func=get_version_by_id, methods=['GET'])

    # ---------- Тренировки (требуют JWT) ----------
    app.add_url_rule('/api/workouts', view_func=create_workout, methods=['POST'])
    app.add_url_rule('/api/workouts', view_func=get_my_workouts, methods=['GET'])
    app.add_url_rule('/api/workouts/<int:workout_id>', view_func=get_workout, methods=['GET'])
    app.add_url_rule('/api/workout-exercises/<int:workout_exercise_id>/log', view_func=log_set, methods=['POST'])
    app.add_url_rule('/api/workouts/<int:workout_id>', view_func=delete_workout, methods=['DELETE'])

    # ---------- Избранное (требуют JWT) ----------
    app.add_url_rule('/api/favorites', view_func=add_favorite, methods=['POST'])
    app.add_url_rule('/api/favorites', view_func=get_favorites, methods=['GET'])
    app.add_url_rule('/api/favorites/<int:exercise_id>', view_func=remove_favorite, methods=['DELETE'])

    # ---------- Статические файлы фронтенда ----------
    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory('../frontend', path)

    return app
