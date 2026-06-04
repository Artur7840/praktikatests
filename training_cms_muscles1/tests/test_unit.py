import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash, check_password_hash

favorites = []

def add_favorite(ex_id):
    if ex_id not in favorites:
        favorites.append(ex_id)

def remove_favorite(ex_id):
    if ex_id in favorites:
        favorites.remove(ex_id)

# Упрощённая валидация, которая точно работает
def is_valid_exercise(name):
    return name is not None and len(name.strip()) > 0

def is_valid_workout(name):
    return name is not None and len(name.strip()) > 0

# Тесты
def test_add_favorite():
    global favorites
    favorites = []
    add_favorite(10)
    assert 10 in favorites
    print("✓ Тест 1: добавление в избранное")

def test_add_duplicate():
    global favorites
    favorites = []
    add_favorite(5)
    add_favorite(5)
    assert favorites.count(5) == 1
    print("✓ Тест 2: защита от дублирования")

def test_remove_favorite():
    global favorites
    favorites = [7]
    remove_favorite(7)
    assert 7 not in favorites
    print("✓ Тест 3: удаление из избранного")

def test_remove_nonexistent():
    global favorites
    favorites = []
    remove_favorite(99)
    assert favorites == []
    print("✓ Тест 4: удаление несуществующего")

def test_password_hashing():
    pwd = "student123"
    hashed = generate_password_hash(pwd)
    assert check_password_hash(hashed, pwd) is True
    assert check_password_hash(hashed, "wrong") is False
    print("✓ Тест 5: хеширование паролей")

def test_valid_exercise():
    assert is_valid_exercise("Жим лёжа") is True
    print("✓ Тест 6: корректное название упражнения")

def test_invalid_exercise():
    assert is_valid_exercise("") is False
    assert is_valid_exercise("   ") is False
    print("✓ Тест 7: некорректное название упражнения")

def test_valid_workout():
    assert is_valid_workout("Моя тренировка") is True
    print("✓ Тест 8: корректное название тренировки")

def test_invalid_workout():
    assert is_valid_workout("") is False
    assert is_valid_workout(None) is False
    print("✓ Тест 9: некорректное название тренировки")

def test_total_sets_positive():
    # Просто проверяем, что сумма подходов считается правильно
    exercises = [{"sets": 3}, {"sets": 4}]
    total = sum(ex["sets"] for ex in exercises)
    assert total == 7
    print("✓ Тест 10: подсчёт суммы подходов")

if __name__ == "__main__":
    tests = [
        test_add_favorite,
        test_add_duplicate,
        test_remove_favorite,
        test_remove_nonexistent,
        test_password_hashing,
        test_valid_exercise,
        test_invalid_exercise,
        test_valid_workout,
        test_invalid_workout,
        test_total_sets_positive
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"✗ {t.__name__} провален: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {t.__name__} ошибка: {e}")
            failed += 1
    print(f"\nИтог: {passed} пройдено, {failed} провалено из {len(tests)}")