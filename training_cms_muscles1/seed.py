import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Получаем URL базы данных
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    try:
        from backend.config import Config
        DATABASE_URL = Config.DATABASE_URL
    except ImportError:
        pass

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задан. Установите переменную окружения.")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def setup_database():
    """Создаёт таблицы из schema.sql."""
    conn = get_conn()
    with conn.cursor() as cur:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            cur.execute(sql)
        conn.commit()
    conn.close()
    print("✅ Таблицы успешно созданы (если их не было).")

def seed_muscle_groups(cur):
    groups = [
        ('Грудные', 'Упражнения для развития грудных мышц', 'https://picsum.photos/id/100/400/300', None),
        ('Спина', 'Тренировка широчайших и трапеций', 'https://picsum.photos/id/101/400/300', None),
        ('Ноги', 'Квадрицепсы, бицепс бедра, ягодицы', 'https://picsum.photos/id/102/400/300', None),
        ('Плечи', 'Дельтовидные мышцы', 'https://picsum.photos/id/103/400/300', None),
        ('Бицепс', 'Сгибатели рук', 'https://picsum.photos/id/104/400/300', None),
        ('Трицепс', 'Разгибатели рук', 'https://picsum.photos/id/105/400/300', None),
        ('Пресс', 'Мышцы кора', 'https://picsum.photos/id/106/400/300', None),
        ('Ягодицы', 'Укрепление ягодичных', 'https://picsum.photos/id/107/400/300', None),
    ]
    for name, desc, url, parent in groups:
        cur.execute("""
            INSERT INTO muscle_group (name, description, photo_url, parent_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, (name, desc, url, parent))
    print("  ➕ Группы мышц: добавлено/проверено 8")

def seed_exercises(cur):
    exercises = [
        # Грудные (muscle_group_id = 1)
        ('Жим штанги лёжа', 'Базовое упражнение для массы груди', 'Лягте на скамью, гриф на уровне глаз.', 'medium', 'https://picsum.photos/id/1/400/300', 1, 'strength', 4, 10, 60, None, None, None, None),
        ('Жим гантелей лёжа', 'Лучшая амплитуда', 'Гантели опускайте глубже.', 'medium', 'https://picsum.photos/id/2/400/300', 1, 'strength', 4, 10, 50, None, None, None, None),
        ('Отжимания на брусьях', 'Низ груди и трицепс', 'Наклоняйте корпус вперёд.', 'hard', 'https://picsum.photos/id/3/400/300', 1, 'strength', 3, 12, None, None, None, None, None),
        ('Отжимания от пола', 'Домашнее упражнение', 'Руки шире плеч.', 'easy', 'https://picsum.photos/id/4/400/300', 1, 'strength', 3, 15, None, None, None, None, None),
        ('Сведение рук в кроссовере', 'Изоляция верха груди', 'Стойте в наклоне.', 'medium', 'https://picsum.photos/id/5/400/300', 1, 'strength', 3, 12, 20, None, None, None, None),
        # Спина (muscle_group_id = 2)
        ('Тяга штанги в наклоне', 'Ширина спины', 'Наклон 45°.', 'medium', 'https://picsum.photos/id/6/400/300', 2, 'strength', 4, 10, 70, None, None, None, None),
        ('Тяга верхнего блока', 'Широчайшие', 'Тяните к груди.', 'easy', 'https://picsum.photos/id/7/400/300', 2, 'strength', 3, 12, 40, None, None, None, None),
        ('Тяга гантели к поясу', 'Односторонняя', 'Упритесь в скамью.', 'medium', 'https://picsum.photos/id/8/400/300', 2, 'strength', 3, 10, 25, None, None, None, None),
        ('Гиперэкстензия', 'Поясница', 'Римский стул.', 'easy', 'https://picsum.photos/id/9/400/300', 2, 'strength', 3, 15, None, None, None, None, None),
        ('Подтягивания', 'Классика', 'Широкий хват.', 'hard', 'https://picsum.photos/id/10/400/300', 2, 'strength', 3, 8, None, None, None, None, None),
        ('Тяга нижнего блока', 'Низ широчайших', 'Тяните к животу.', 'medium', 'https://picsum.photos/id/11/400/300', 2, 'strength', 3, 12, 50, None, None, None, None),
        # Ноги (muscle_group_id = 3)
        ('Приседания со штангой', 'База для ног', 'Спина прямая.', 'medium', 'https://picsum.photos/id/12/400/300', 3, 'strength', 4, 10, 80, None, None, None, None),
        ('Жим ногами', 'Безопасно', 'Выжимайте пятками.', 'easy', 'https://picsum.photos/id/13/400/300', 3, 'strength', 4, 12, 100, None, None, None, None),
        ('Разгибание ног', 'Квадрицепс', 'Тренажёр.', 'easy', 'https://picsum.photos/id/14/400/300', 3, 'strength', 3, 12, 40, None, None, None, None),
        ('Сгибание ног', 'Бицепс бедра', 'Валик на пятках.', 'easy', 'https://picsum.photos/id/15/400/300', 3, 'strength', 3, 12, 30, None, None, None, None),
        ('Выпады с гантелями', 'Ягодицы', 'Шаг вперёд.', 'medium', 'https://picsum.photos/id/16/400/300', 3, 'strength', 3, 10, 30, None, None, None, None),
        ('Румынская тяга', 'Задняя поверхность', 'Прямые ноги.', 'medium', 'https://picsum.photos/id/17/400/300', 3, 'strength', 3, 10, 60, None, None, None, None),
        # Плечи (muscle_group_id = 4)
        ('Жим штанги сидя', 'Передние дельты', 'Гриф к ключицам.', 'medium', 'https://picsum.photos/id/18/400/300', 4, 'strength', 4, 10, 40, None, None, None, None),
        ('Жим гантелей сидя', 'Все пучки', 'Локти 90°.', 'medium', 'https://picsum.photos/id/19/400/300', 4, 'strength', 4, 10, 20, None, None, None, None),
        ('Разведение гантелей', 'Средняя дельта', 'Лёгкий вес.', 'easy', 'https://picsum.photos/id/20/400/300', 4, 'strength', 3, 12, 8, None, None, None, None),
        ('Тяга к подбородку', 'Трапеции', 'Узкий хват.', 'medium', 'https://picsum.photos/id/21/400/300', 4, 'strength', 3, 10, 25, None, None, None, None),
        ('Обратные разведения', 'Задняя дельта', 'Согнитесь.', 'medium', 'https://picsum.photos/id/22/400/300', 4, 'strength', 3, 10, 6, None, None, None, None),
        # Бицепс (muscle_group_id = 5)
        ('Подъём штанги на бицепс', 'Брахиалис', 'Локти прижаты.', 'easy', 'https://picsum.photos/id/23/400/300', 5, 'strength', 3, 10, 20, None, None, None, None),
        ('Подъём гантелей сидя', 'Пиковое сокращение', 'Рука за спинкой.', 'medium', 'https://picsum.photos/id/24/400/300', 5, 'strength', 3, 10, 12, None, None, None, None),
        ('Молотки', 'Плечевая мышца', 'Нейтральный хват.', 'easy', 'https://picsum.photos/id/25/400/300', 5, 'strength', 3, 10, 12, None, None, None, None),
        ('Концентрированный подъём', 'Пик бицепса', 'Локоть в бедро.', 'medium', 'https://picsum.photos/id/26/400/300', 5, 'strength', 3, 10, 8, None, None, None, None),
        ('Подъём на блоке', 'Равномерно', 'Трос снизу.', 'easy', 'https://picsum.photos/id/27/400/300', 5, 'strength', 3, 12, 15, None, None, None, None),
        # Трицепс (muscle_group_id = 6)
        ('Французский жим', 'Длинная головка', 'Штанга за головой.', 'medium', 'https://picsum.photos/id/28/400/300', 6, 'strength', 3, 10, 15, None, None, None, None),
        ('Разгибание в наклоне', 'Фокус', 'Гантель.', 'easy', 'https://picsum.photos/id/29/400/300', 6, 'strength', 3, 10, 8, None, None, None, None),
        ('Отжимания узким хватом', 'Трицепс', 'Локти вдоль тела.', 'medium', 'https://picsum.photos/id/30/400/300', 6, 'strength', 3, 12, None, None, None, None, None),
        ('Кикбэк на блоке', 'Внешняя головка', 'Трос сверху.', 'easy', 'https://picsum.photos/id/31/400/300', 6, 'strength', 3, 10, 10, None, None, None, None),
        ('Жим лёжа узким хватом', 'Трицепс', 'Хват уже плеч.', 'medium', 'https://picsum.photos/id/32/400/300', 6, 'strength', 3, 10, 50, None, None, None, None),
        # Пресс (muscle_group_id = 7)
        ('Скручивания', 'Верхний пресс', 'Поясница прижата.', 'easy', 'https://picsum.photos/id/33/400/300', 7, 'strength', 3, 20, None, None, None, None, None),
        ('Обратные скручивания', 'Нижний пресс', 'Колени к груди.', 'easy', 'https://picsum.photos/id/34/400/300', 7, 'strength', 3, 15, None, None, None, None, None),
        ('Велосипед', 'Косые', 'Локоть к колену.', 'medium', 'https://picsum.photos/id/35/400/300', 7, 'strength', 3, 20, None, None, None, None, None),
        ('Планка', 'Статика', 'Прямая линия.', 'easy', 'https://picsum.photos/id/36/400/300', 7, 'strength', 3, 30, None, None, None, None, None),
        ('Подъём ног в висе', 'Пресс', 'Вис на перекладине.', 'hard', 'https://picsum.photos/id/37/400/300', 7, 'strength', 3, 12, None, None, None, None, None),
        # Ягодицы (muscle_group_id = 8)
        ('Ягодичный мост', 'Начальный', 'Упритесь лопатками.', 'easy', 'https://picsum.photos/id/38/400/300', 8, 'strength', 3, 15, 20, None, None, None, None),
        ('Приседания плие', 'Внутренняя поверхность', 'Носки наружу.', 'medium', 'https://picsum.photos/id/39/400/300', 8, 'strength', 3, 12, 30, None, None, None, None),
        ('Болгарские выпады', 'Ягодицы', 'Задняя нога на скамье.', 'hard', 'https://picsum.photos/id/40/400/300', 8, 'strength', 3, 10, 25, None, None, None, None),
        ('Махи ногой в кроссовере', 'Изоляция', 'Лицом к блоку.', 'medium', 'https://picsum.photos/id/41/400/300', 8, 'strength', 3, 12, 10, None, None, None, None),
    ]
    for ex in exercises:
        cur.execute("SELECT id FROM exercise WHERE name = %s AND muscle_group_id = %s", (ex[0], ex[5]))
        if cur.fetchone() is None:
            cur.execute("""
                INSERT INTO exercise (
                    name, description, technique, difficulty, photo_url,
                    muscle_group_id, type,
                    default_sets, default_reps, default_weight,
                    default_duration_min, default_distance_km, default_calories, default_duration_sec
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, ex)
    print("  ➕ Упражнения: добавлено/проверено 41")

def seed_user(cur):
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
