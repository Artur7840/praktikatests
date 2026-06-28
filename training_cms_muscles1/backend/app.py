from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.db import close_db
import os

# Переключение между ORM и Native SQL
USE_ORM = os.environ.get('USE_ORM', 'True').lower() == 'true'

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    JWTManager(app)
    app.teardown_appcontext(close_db)

    from backend.auth import register, login
    from backend.api import (
        get_muscle_groups, get_exercises, get_exercise,
        create_workout, get_my_workouts, get_workout, log_set, delete_workout,
        get_exercise_versions, get_version_by_id, add_favorite, remove_favorite, get_favorites
    )

    # API маршруты
    app.add_url_rule('/api/register', view_func=register, methods=['POST'])
    app.add_url_rule('/api/login', view_func=login, methods=['POST'])
    app.add_url_rule('/api/muscle-groups', view_func=get_muscle_groups, methods=['GET'])
    app.add_url_rule('/api/exercises', view_func=get_exercises, methods=['GET'])
    app.add_url_rule('/api/exercises/<int:exercise_id>', view_func=get_exercise, methods=['GET'])
    app.add_url_rule('/api/exercises/<int:exercise_id>/versions', view_func=get_exercise_versions, methods=['GET'])
    app.add_url_rule('/api/exercises/versions/<int:version_id>', view_func=get_version_by_id, methods=['GET'])
    app.add_url_rule('/api/workouts', view_func=create_workout, methods=['POST'])
    app.add_url_rule('/api/workouts', view_func=get_my_workouts, methods=['GET'])
    app.add_url_rule('/api/workouts/<int:workout_id>', view_func=get_workout, methods=['GET'])
    app.add_url_rule('/api/workout-exercises/<int:workout_exercise_id>/log', view_func=log_set, methods=['POST'])
    app.add_url_rule('/api/workouts/<int:workout_id>', view_func=delete_workout, methods=['DELETE'])
    app.add_url_rule('/api/favorites', view_func=add_favorite, methods=['POST'])
    app.add_url_rule('/api/favorites/<int:exercise_id>', view_func=remove_favorite, methods=['DELETE'])
    app.add_url_rule('/api/favorites', view_func=get_favorites, methods=['GET'])

    # Маршруты для статики
    @app.route('/debug/add_parent_id', methods=['GET'])
    def add_parent_id():
        try:
            from backend.db import get_db
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='muscle_group' AND column_name='parent_id'
            """)
            if cur.fetchone():
                return "✅ Столбец parent_id уже существует"
            cur.execute("ALTER TABLE muscle_group ADD COLUMN parent_id INTEGER REFERENCES muscle_group(id)")
            conn.commit()
            return "✅ Столбец parent_id успешно добавлен"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    @app.route('/')
    def index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory('../frontend', path)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
