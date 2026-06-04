import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import init_db
from werkzeug.security import generate_password_hash
from backend.config import DB_PATH

init_db()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

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
    cursor.execute('INSERT OR IGNORE INTO muscle_group (name, description, photo_url) VALUES (%s, %s, %s)', (name, desc, url))

exercises = [
    # Грудные (1)
    ('Жим штанги лёжа', 'Базовое упражнение для массы груди', 'Лягте на скамью, гриф на уровне глаз.', 'medium', 'https://picsum.photos/id/1/400/300', 1),
    ('Жим гантелей лёжа', 'Лучшая амплитуда', 'Гантели опускайте глубже.', 'medium', 'https://picsum.photos/id/2/400/300', 1),
    ('Отжимания на брусьях', 'Низ груди и трицепс', 'Наклоняйте корпус вперёд.', 'hard', 'https://picsum.photos/id/3/400/300', 1),
    ('Отжимания от пола', 'Домашнее упражнение', 'Руки шире плеч.', 'easy', 'https://picsum.photos/id/4/400/300', 1),
    ('Сведение рук в кроссовере', 'Изоляция верха груди', 'Стойте в наклоне.', 'medium', 'https://picsum.photos/id/5/400/300', 1),
    # Спина (2)
    ('Тяга штанги в наклоне', 'Ширина спины', 'Наклон 45°.', 'medium', 'https://picsum.photos/id/6/400/300', 2),
    ('Тяга верхнего блока', 'Широчайшие', 'Тяните к груди.', 'easy', 'https://picsum.photos/id/7/400/300', 2),
    ('Тяга гантели к поясу', 'Односторонняя', 'Упритесь в скамью.', 'medium', 'https://picsum.photos/id/8/400/300', 2),
    ('Гиперэкстензия', 'Поясница', 'Римский стул.', 'easy', 'https://picsum.photos/id/9/400/300', 2),
    ('Подтягивания', 'Классика', 'Широкий хват.', 'hard', 'https://picsum.photos/id/10/400/300', 2),
    ('Тяга нижнего блока', 'Низ широчайших', 'Тяните к животу.', 'medium', 'https://picsum.photos/id/11/400/300', 2),
    # Ноги (3)
    ('Приседания со штангой', 'База для ног', 'Спина прямая.', 'medium', 'https://picsum.photos/id/12/400/300', 3),
    ('Жим ногами', 'Безопасно', 'Выжимайте пятками.', 'easy', 'https://picsum.photos/id/13/400/300', 3),
    ('Разгибание ног', 'Квадрицепс', 'Тренажёр.', 'easy', 'https://picsum.photos/id/14/400/300', 3),
    ('Сгибание ног', 'Бицепс бедра', 'Валик на пятках.', 'easy', 'https://picsum.photos/id/15/400/300', 3),
    ('Выпады с гантелями', 'Ягодицы', 'Шаг вперёд.', 'medium', 'https://picsum.photos/id/16/400/300', 3),
    ('Румынская тяга', 'Задняя поверхность', 'Прямые ноги.', 'medium', 'https://picsum.photos/id/17/400/300', 3),
    # Плечи (4)
    ('Жим штанги сидя', 'Передние дельты', 'Гриф к ключицам.', 'medium', 'https://picsum.photos/id/18/400/300', 4),
    ('Жим гантелей сидя', 'Все пучки', 'Локти 90°.', 'medium', 'https://picsum.photos/id/19/400/300', 4),
    ('Разведение гантелей', 'Средняя дельта', 'Лёгкий вес.', 'easy', 'https://picsum.photos/id/20/400/300', 4),
    ('Тяга к подбородку', 'Трапеции', 'Узкий хват.', 'medium', 'https://picsum.photos/id/21/400/300', 4),
    ('Обратные разведения', 'Задняя дельта', 'Согнитесь.', 'medium', 'https://picsum.photos/id/22/400/300', 4),
    # Бицепс (5)
    ('Подъём штанги на бицепс', 'Брахиалис', 'Локти прижаты.', 'easy', 'https://picsum.photos/id/23/400/300', 5),
    ('Подъём гантелей сидя', 'Пиковое сокращение', 'Рука за спинкой.', 'medium', 'https://picsum.photos/id/24/400/300', 5),
    ('Молотки', 'Плечевая мышца', 'Нейтральный хват.', 'easy', 'https://picsum.photos/id/25/400/300', 5),
    ('Концентрированный подъём', 'Пик бицепса', 'Локоть в бедро.', 'medium', 'https://picsum.photos/id/26/400/300', 5),
    ('Подъём на блоке', 'Равномерно', 'Трос снизу.', 'easy', 'https://picsum.photos/id/27/400/300', 5),
    # Трицепс (6)
    ('Французский жим', 'Длинная головка', 'Штанга за головой.', 'medium', 'https://picsum.photos/id/28/400/300', 6),
    ('Разгибание в наклоне', 'Фокус', 'Гантель.', 'easy', 'https://picsum.photos/id/29/400/300', 6),
    ('Отжимания узким хватом', 'Трицепс', 'Локти вдоль тела.', 'medium', 'https://picsum.photos/id/30/400/300', 6),
    ('Кикбэк на блоке', 'Внешняя головка', 'Трос сверху.', 'easy', 'https://picsum.photos/id/31/400/300', 6),
    ('Жим лёжа узким хватом', 'Трицепс', 'Хват уже плеч.', 'medium', 'https://picsum.photos/id/32/400/300', 6),
    # Пресс (7)
    ('Скручивания', 'Верхний пресс', 'Поясница прижата.', 'easy', 'https://picsum.photos/id/33/400/300', 7),
    ('Обратные скручивания', 'Нижний пресс', 'Колени к груди.', 'easy', 'https://picsum.photos/id/34/400/300', 7),
    ('Велосипед', 'Косые', 'Локоть к колену.', 'medium', 'https://picsum.photos/id/35/400/300', 7),
    ('Планка', 'Статика', 'Прямая линия.', 'easy', 'https://picsum.photos/id/36/400/300', 7),
    ('Подъём ног в висе', 'Пресс', 'Вис на перекладине.', 'hard', 'https://picsum.photos/id/37/400/300', 7),
    # Ягодицы (8)
    ('Ягодичный мост', 'Начальный', 'Упритесь лопатками.', 'easy', 'https://picsum.photos/id/38/400/300', 8),
    ('Приседания плие', 'Внутренняя поверхность', 'Носки наружу.', 'medium', 'https://picsum.photos/id/39/400/300', 8),
    ('Болгарские выпады', 'Ягодицы', 'Задняя нога на скамье.', 'hard', 'https://picsum.photos/id/40/400/300', 8),
    ('Махи ногой в кроссовере', 'Изоляция', 'Лицом к блоку.', 'medium', 'https://picsum.photos/id/41/400/300', 8),
]
for name, desc, tech, diff, img, mg_id in exercises:
    cursor.execute('''INSERT OR IGNORE INTO exercise (name, description, technique, difficulty, photo_url, muscle_group_id)
                      VALUES (%s, %s, %s, %s, %s, %s)''', (name, desc, tech, diff, img, mg_id))

hashed = generate_password_hash('student')
cursor.execute('INSERT OR IGNORE INTO user (email, password, role) VALUES (%s, %s, %s)',
               ('student@example.com', hashed, 'student'))

conn.commit()
conn.close()
print("База данных создана и заполнена (41 упражнение, 8 групп, тестовый пользователь).")
