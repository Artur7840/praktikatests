import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

# Получаем URL базы данных из переменной окружения
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    # Если переменной нет, возможно, проект запущен не на Render
    # Здесь можно добавить fallback для локальной разработки, если нужно
    try:
        from backend.config import Config
        DATABASE_URL = Config.DATABASE_URL
    except ImportError:
        pass

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задан. Установите переменную окружения.")

def get_conn():
    """Возвращает соединение с базой данных."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def setup_database():
    conn = get_conn()
    with conn.cursor() as cur:
        # ... существующие таблицы muscle_group, exercise, "user" ...
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout_exercise (
                id SERIAL PRIMARY KEY,
                workout_id INTEGER NOT NULL REFERENCES workout(id) ON DELETE CASCADE,
                exercise_id INTEGER NOT NULL REFERENCES exercise(id) ON DELETE CASCADE,
                sets INTEGER DEFAULT 3,
                reps INTEGER DEFAULT 10,
                weight REAL,
                "order" INTEGER DEFAULT 0
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout_log (
                id SERIAL PRIMARY KEY,
                workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercise(id) ON DELETE CASCADE,
                set_number INTEGER,
                reps_done INTEGER,
                weight_used REAL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    conn.close()
    print("✅ Таблицы успешно созданы (если их не было).")

def seed_muscle_groups(cur):
    """Заполняет таблицу групп мышц."""
    groups = [
        ('Грудные', 'Упражнения для развития грудных мышц', 'https://picsum.photos/id/100/400/300'),
        ('Спина', 'Тренировка широчайших и трапеций', 'https://picsum.photos/id/101/400/300'),
        ('Ноги', 'Квадрицепсы, бицепс бедра, ягодицы', 'https://picsum.photos/id/102/400/300'),
        ('Плечи', 'Дельтовидные мышцы', 'https://picsum.photos/id/103/400/300'),
        ('Бицепс', 'Сгибатели рук', 'https://picsum.photos/id/104/400/300'),
        ('Трицепс', 'Разгибатели рук', 'https://picsum.photos/id/105/400/300'),
        ('Пресс', 'Мышцы кора', 'https://picsum.photos/id/106/400/300'),
        ('Ягодицы', 'Укрепление ягодичных', 'https://picsum.photos/id/107/400/300'),
    ]
    for name, desc, url in groups:
        cur.execute("""
            INSERT INTO muscle_group (name, description, photo_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, (name, desc, url))
    print(f"  ➕ Группы мышц: добавлено/проверено {len(groups)}")

def seed_exercises(cur):
    """Заполняет таблицу упражнений."""
    exercises = [
        # Грудные (muscle_group_id = 1)
        ('Жим штанги лёжа', 'Базовое упражнение для массы груди', 'Лягте на скамью, гриф на уровне глаз. Опускайте до груди, выжимайте вверх.', 'medium', 'https://picsum.photos/id/1/400/300', 1),
        ('Жим гантелей лёжа', 'Лучшая амплитуда', 'Гантели опускайте глубже, чем штангу.', 'medium', 'https://picsum.photos/id/2/400/300', 1),
        ('Отжимания на брусьях', 'Низ груди и трицепс', 'Наклоняйте корпус вперёд.', 'hard', 'https://picsum.photos/id/3/400/300', 1),
        ('Отжимания от пола', 'Домашнее упражнение', 'Руки шире плеч – грудь, уже – трицепс.', 'easy', 'https://picsum.photos/id/4/400/300', 1),
        ('Сведение рук в кроссовере', 'Изоляция верха груди', 'Стойте в наклоне, сводите руки перед собой.', 'medium', 'https://picsum.photos/id/5/400/300', 1),
        # Спина (muscle_group_id = 2)
        ('Тяга штанги в наклоне', 'Ширина спины', 'Наклон 45°, тяните к низу живота.', 'medium', 'https://picsum.photos/id/6/400/300', 2),
        ('Тяга верхнего блока', 'Развитие широчайших', 'Тяните за голову или к груди.', 'easy', 'https://picsum.photos/id/7/400/300', 2),
        ('Тяга гантели к поясу', 'Односторонняя нагрузка', 'Упритесь коленом в скамью, тяните гантель к животу.', 'medium', 'https://picsum.photos/id/8/400/300', 2),
        ('Гиперэкстензия', 'Поясница, выпрямители', 'Ложитесь на римский стул, сгибайтесь и поднимайтесь.', 'easy', 'https://picsum.photos/id/9/400/300', 2),
        ('Подтягивания', 'Классика спины', 'Широкий хват – ширина, узкий – толщина.', 'hard', 'https://picsum.photos/id/10/400/300', 2),
        ('Тяга нижнего блока', 'Низ широчайших', 'Сядьте, ноги в упор, тяните к животу.', 'medium', 'https://picsum.photos/id/11/400/300', 2),
        # Ноги (muscle_group_id = 3)
        ('Приседания со штангой', 'Основное для ног', 'Держите спину прямой, не округляйте поясницу.', 'medium', 'https://picsum.photos/id/12/400/300', 3),
        ('Жим ногами', 'Безопасная альтернатива приседу', 'Платформа под углом 45°, выжимайте пятками.', 'easy', 'https://picsum.photos/id/13/400/300', 3),
        ('Разгибание ног в тренажёре', 'Изоляция квадрицепса', 'Сядьте, валик на голеностопе, разгибайте до упора.', 'easy', 'https://picsum.photos/id/14/400/300', 3),
        ('Сгибание ног сидя', 'Бицепс бедра', 'Валик на пятках, сгибайте, не отрывая таз.', 'easy', 'https://picsum.photos/id/15/400/300', 3),
        ('Выпады с гантелями', 'Ягодицы и квадрицепс', 'Шаг вперёд, колено передней ноги не выходит за носок.', 'medium', 'https://picsum.photos/id/16/400/300', 3),
        ('Румынская тяга', 'Растяжка бицепса бедра', 'Штанга скользит по ногам с прямыми ногами.', 'medium', 'https://picsum.photos/id/17/400/300', 3),
        # Плечи (muscle_group_id = 4)
        ('Жим штанги сидя', 'Передние дельты', 'Опускайте гриф к ключицам, не разводите локти.', 'medium', 'https://picsum.photos/id/18/400/300', 4),
        ('Жим гантелей сидя', 'Все пучки дельт', 'Локти под 90°, поднимайте над головой.', 'medium', 'https://picsum.photos/id/19/400/300', 4),
        ('Разведение гантелей в стороны', 'Средняя дельта', 'Наклон чуть вперёд, лёгкий вес, без рывков.', 'easy', 'https://picsum.photos/id/20/400/300', 4),
        ('Тяга штанги к подбородку', 'Трапеции и передние дельты', 'Хват узкий, тяните локтями вверх.', 'medium', 'https://picsum.photos/id/21/400/300', 4),
        ('Обратные разведения в тренажёре', 'Задняя дельта', 'Согнитесь, грудь к спинке, разводите руки.', 'medium', 'https://picsum.photos/id/22/400/300', 4),
        # Бицепс (muscle_group_id = 5)
        ('Подъём штанги на бицепс', 'Брахиалис и бицепс', 'Локти прижаты, не раскачивайтесь.', 'easy', 'https://picsum.photos/id/23/400/300', 5),
        ('Подъём гантелей сидя на наклонной', 'Пиковое сокращение', 'Рука за спинкой, опускайте медленно.', 'medium', 'https://picsum.photos/id/24/400/300', 5),
        ('Молотковые сгибания', 'Плечевая мышца', 'Гантели нейтральным хватом, поднимайте к плечу.', 'easy', 'https://picsum.photos/id/25/400/300', 5),
        ('Концентрированный подъём', 'Пик бицепса', 'Сядьте, локоть упирается в бедро, подъём гантели.', 'medium', 'https://picsum.photos/id/26/400/300', 5),
        ('Подъём на блоке', 'Равномерная нагрузка', 'Блок снизу, тяните к плечу, не отрывая локоть.', 'easy', 'https://picsum.photos/id/27/400/300', 5),
        # Трицепс (muscle_group_id = 6)
        ('Французский жим сидя', 'Длинная головка', 'Штанга за головой, опускайте ко лбу.', 'medium', 'https://picsum.photos/id/28/400/300', 6),
        ('Разгибание руки в наклоне', 'Фокус на трицепс', 'Гантель, рука параллельно корпусу, разгибайте.', 'easy', 'https://picsum.photos/id/29/400/300', 6),
        ('Отжимания узким хватом', 'Трицепс и грудь', 'Кисти под грудью, локти вдоль тела.', 'medium', 'https://picsum.photos/id/30/400/300', 6),
        ('Разгибание на блоке (кикбэк)', 'Средняя и внешняя головки', 'Трос в верхней точке, рука согнута, разгибайте до конца.', 'easy', 'https://picsum.photos/id/31/400/300', 6),
        ('Жим лёжа узким хватом', 'Трицепс', 'Хват уже плеч, локти ближе к телу.', 'medium', 'https://picsum.photos/id/32/400/300', 6),
        # Пресс (muscle_group_id = 7)
        ('Скручивания на полу', 'Верхний пресс', 'Поясница прижата, скручивайте грудную клетку к тазу.', 'easy', 'https://picsum.photos/id/33/400/300', 7),
        ('Обратные скручивания', 'Нижний пресс', 'Ноги согнуты, подтягивайте колени к груди.', 'easy', 'https://picsum.photos/id/34/400/300', 7),
        ('Велосипед', 'Косые мышцы', 'Локоть к противоположному колену.', 'medium', 'https://picsum.photos/id/35/400/300', 7),
        ('Планка', 'Статика кора', 'Держите тело прямой линией от пяток до макушки.', 'easy', 'https://picsum.photos/id/36/400/300', 7),
        ('Подъём ног в висе', 'Пресс и сгибатели бедра', 'Вис на перекладине, поднимайте прямые ноги.', 'hard', 'https://picsum.photos/id/37/400/300', 7),
        # Ягодицы (muscle_group_id = 8)
        ('Ягодичный мост', 'Начальный уровень', 'Упритесь лопатками в скамью, поднимайте таз.', 'easy', 'https://picsum.photos/id/38/400/300', 8),
        ('Приседания плие', 'Внутренняя поверхность бедра', 'Ноги шире плеч, носки наружу, приседайте глубже.', 'medium', 'https://picsum.photos/id/39/400/300', 8),
        ('Болгарские выпады', 'Ягодицы и стабильность', 'Задняя нога на скамье, передняя делает выпад.', 'hard', 'https://picsum.photos/id/40/400/300', 8),
        ('Махи ногой в кроссовере', 'Изоляция ягодиц', 'Стойка лицом к блоку, мах прямой ногой назад.', 'medium', 'https://picsum.photos/id/41/400/300', 8),
    ]
    for ex in exercises:
        cur.execute("SELECT id FROM exercise WHERE name = %s AND muscle_group_id = %s", (ex[0], ex[5]))
        if cur.fetchone() is None:
            cur.execute("""
                INSERT INTO exercise (name, description, technique, difficulty, photo_url, muscle_group_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ex)
    print(f"  ➕ Упражнения: добавлено/проверено {len(exercises)}")

def seed_user(cur):
    """Добавляет тестового пользователя."""
    email = 'student@example.com'
    password = 'student'
    hashed = generate_password_hash(password)
    cur.execute("""
        INSERT INTO "user" (email, password, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
    """, (email, hashed, 'student'))
    print("  ➕ Тестовый пользователь: student@example.com / student")

def main():
    print("🌱 Запуск seed.py для PostgreSQL...")
    setup_database()
    conn = get_conn()
    cur = conn.cursor()
    seed_muscle_groups(cur)
    seed_exercises(cur)
    seed_user(cur)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ База данных полностью заполнена!")

if __name__ == '__main__':
    main()
