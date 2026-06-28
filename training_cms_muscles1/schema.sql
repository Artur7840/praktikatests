-- Таблица пользователей
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица групп мышц (иерархия)
CREATE TABLE IF NOT EXISTS muscle_group (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    photo_url TEXT,
    parent_id INTEGER REFERENCES muscle_group(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица упражнений (наследование через TPH)
CREATE TABLE IF NOT EXISTS exercise (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    technique TEXT,
    difficulty TEXT DEFAULT 'medium',
    photo_url TEXT,
    muscle_group_id INTEGER NOT NULL REFERENCES muscle_group(id) ON DELETE CASCADE,
    
    -- Поля для наследования (TPH)
    type VARCHAR(20) DEFAULT 'strength',
    default_sets INTEGER,
    default_reps INTEGER,
    default_weight REAL,
    default_duration_min INTEGER,
    default_distance_km REAL,
    default_calories INTEGER,
    default_duration_sec INTEGER,
    
    -- Версионирование
    current_version_id INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица версий упражнений
CREATE TABLE IF NOT EXISTS exercise_version (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL REFERENCES exercise(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    description TEXT,
    technique TEXT,
    difficulty TEXT DEFAULT 'medium',
    photo_url TEXT,
    muscle_group_id INTEGER NOT NULL,
    type VARCHAR(20) DEFAULT 'strength',
    default_sets INTEGER,
    default_reps INTEGER,
    default_weight REAL,
    default_duration_min INTEGER,
    default_distance_km REAL,
    default_calories INTEGER,
    default_duration_sec INTEGER,
    is_current BOOLEAN DEFAULT FALSE,
    UNIQUE(exercise_id, version_number)
);

-- Таблица тренировок
CREATE TABLE IF NOT EXISTS workout (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);

-- Связь тренировки и упражнения
CREATE TABLE IF NOT EXISTS workout_exercise (
    id SERIAL PRIMARY KEY,
    workout_id INTEGER NOT NULL REFERENCES workout(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercise(id) ON DELETE CASCADE,
    sets INTEGER DEFAULT 3,
    reps INTEGER DEFAULT 10,
    weight REAL,
    "order" INTEGER DEFAULT 0
);

-- Логи выполнения подходов
CREATE TABLE IF NOT EXISTS workout_log (
    id SERIAL PRIMARY KEY,
    workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercise(id) ON DELETE CASCADE,
    set_number INTEGER,
    reps_done INTEGER,
    weight_used REAL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица избранного
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercise(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, exercise_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_exercise_muscle ON exercise(muscle_group_id);
CREATE INDEX IF NOT EXISTS idx_workout_user ON workout(user_id);
CREATE INDEX IF NOT EXISTS idx_workoutex_workout ON workout_exercise(workout_id);
CREATE INDEX IF NOT EXISTS idx_workoutlog_workoutex ON workout_log(workout_exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercise_version ON exercise_version(exercise_id);

-- Функция версионирования упражнений
CREATE OR REPLACE FUNCTION version_exercise()
RETURNS TRIGGER AS $$
DECLARE
    next_ver INTEGER;
BEGIN
    IF OLD.is_deleted != NEW.is_deleted THEN
        RETURN NEW;
    END IF;
    
    SELECT COALESCE(MAX(version_number), 0) + 1 INTO next_ver 
    FROM exercise_version WHERE exercise_id = NEW.id;
    
    INSERT INTO exercise_version (
        exercise_id, version_number, valid_from,
        name, description, technique, difficulty, photo_url,
        muscle_group_id, type,
        default_sets, default_reps, default_weight,
        default_duration_min, default_distance_km, default_calories, default_duration_sec,
        is_current
    ) VALUES (
        OLD.id, next_ver, CURRENT_TIMESTAMP,
        OLD.name, OLD.description, OLD.technique, OLD.difficulty, OLD.photo_url,
        OLD.muscle_group_id, OLD.type,
        OLD.default_sets, OLD.default_reps, OLD.default_weight,
        OLD.default_duration_min, OLD.default_distance_km, OLD.default_calories, OLD.default_duration_sec,
        FALSE
    );
    
    NEW.current_version_id = next_ver;
    UPDATE exercise_version SET is_current = FALSE WHERE exercise_id = NEW.id AND is_current = TRUE;
    UPDATE exercise_version SET is_current = TRUE WHERE exercise_id = NEW.id AND version_number = next_ver;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для версионирования (срабатывает при UPDATE)
CREATE TRIGGER trigger_exercise_version
    BEFORE UPDATE ON exercise
    FOR EACH ROW EXECUTE FUNCTION version_exercise();

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_exercise_updated_at
    BEFORE UPDATE ON exercise
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
