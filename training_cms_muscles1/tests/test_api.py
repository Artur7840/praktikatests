import requests

BASE_URL = "http://localhost:5000"

def test_home_page():
    """Тест 1: GET / - возвращает HTML главной страницы"""
    url = f"{BASE_URL}/"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    assert "text/html" in response.headers.get("content-type", ""), "Ошибка: ответ не HTML"
    assert "Muscle Training CMS" in response.text or "Упражнения" in response.text, "Ошибка: заголовок не найден"
    
    print("✓ Тест 1 пройден: GET / возвращает HTML страницу")

def test_api_muscle_groups():
    """Тест 2: GET /api/muscle-groups - возвращает список групп мышц"""
    url = f"{BASE_URL}/api/muscle-groups"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    
    data = response.json()
    assert len(data) > 0, "Ошибка: список групп мышц пуст"
    assert "name" in data[0], "Ошибка: нет поля name"
    assert "id" in data[0], "Ошибка: нет поля id"
    
    print(f"✓ Тест 2 пройден: GET /api/muscle-groups - {len(data)} групп")

def test_api_exercises():
    """Тест 3: GET /api/exercises - возвращает список упражнений"""
    url = f"{BASE_URL}/api/exercises"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    
    data = response.json()
    assert len(data) > 0, "Ошибка: список упражнений пуст"
    assert "name" in data[0], "Ошибка: нет поля name"
    assert "difficulty" in data[0], "Ошибка: нет поля difficulty"
    
    print(f"✓ Тест 3 пройден: GET /api/exercises - {len(data)} упражнений")

def test_exercises_filter_by_muscle():
    """Тест 4: GET /api/exercises?muscle=1 - фильтрация по группе (Грудные)"""
    url = f"{BASE_URL}/api/exercises?muscle=1"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    
    data = response.json()
    # Проверяем, что все упражнения имеют muscle_group_id = 1 (если поле есть)
    if len(data) > 0 and "muscle_group_id" in data[0]:
        for ex in data:
            assert ex.get("muscle_group_id") == 1, "Ошибка: упражнение не из группы 1"
    
    print(f"✓ Тест 4 пройден: фильтрация по группе мышц (получено {len(data)} упражнений)")

def test_exercise_detail():
    """Тест 5: GET /api/exercises/1 - детальная информация упражнения"""
    url = f"{BASE_URL}/api/exercises/1"
    response = requests.get(url)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    
    data = response.json()
    assert "name" in data, "Ошибка: нет названия упражнения"
    assert "description" in data or "technique" in data, "Ошибка: нет описания или техники"
    
    print("✓ Тест 5 пройден: детали упражнения (id=1)")

def test_register():
    """Тест 6: POST /api/register - регистрация нового пользователя"""
    url = f"{BASE_URL}/api/register"
    payload = {"email": "testuser@example.com", "password": "test123"}
    response = requests.post(url, json=payload)
    
    # Регистрация может вернуть 201 (создан) или 409 (уже существует)
    assert response.status_code in (201, 409), f"Ошибка: статус {response.status_code}"
    
    print("✓ Тест 6 пройден: регистрация пользователя")

def test_login():
    """Тест 7: POST /api/login - получение JWT токена"""
    url = f"{BASE_URL}/api/login"
    payload = {"email": "student@example.com", "password": "student"}
    response = requests.post(url, json=payload)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    
    data = response.json()
    assert "access_token" in data, "Ошибка: токен не получен"
    
    print("✓ Тест 7 пройден: вход и получение JWT")

def test_create_workout():
    """Тест 8: POST /api/workouts - создание тренировки (требуется JWT)"""
    # Сначала получаем токен
    login_resp = requests.post(f"{BASE_URL}/api/login", json={"email": "student@example.com", "password": "student"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"{BASE_URL}/api/workouts"
    payload = {
        "name": "Тестовая тренировка",
        "exercises": [{"exercise_id": 1, "sets": 3, "reps": 10, "weight": 50}]
    }
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code == 201, f"Ошибка: статус {response.status_code} != 201"
    data = response.json()
    assert "id" in data, "Ошибка: не вернулся ID тренировки"
    
    print("✓ Тест 8 пройден: создание тренировки")

def test_get_my_workouts():
    """Тест 9: GET /api/workouts - список тренировок пользователя"""
    # Получаем токен
    login_resp = requests.post(f"{BASE_URL}/api/login", json={"email": "student@example.com", "password": "student"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"{BASE_URL}/api/workouts"
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    data = response.json()
    assert isinstance(data, list), "Ошибка: ответ не массив"
    
    print(f"✓ Тест 9 пройден: получено {len(data)} тренировок")

def test_delete_workout():
    """Тест 10: DELETE /api/workouts/{id} - удаление тренировки"""
    # Сначала создадим тренировку
    login_resp = requests.post(f"{BASE_URL}/api/login", json={"email": "student@example.com", "password": "student"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаём
    create_payload = {"name": "Для удаления", "exercises": [{"exercise_id": 1, "sets": 1, "reps": 1}]}
    create_resp = requests.post(f"{BASE_URL}/api/workouts", json=create_payload, headers=headers)
    workout_id = create_resp.json()["id"]
    
    # Удаляем
    url = f"{BASE_URL}/api/workouts/{workout_id}"
    response = requests.delete(url, headers=headers)
    
    assert response.status_code == 200, f"Ошибка: статус {response.status_code} != 200"
    assert response.json().get("msg") == "Workout deleted", "Ошибка: сообщение об удалении не получено"
    
    print("✓ Тест 10 пройден: удаление тренировки")

if __name__ == "__main__":
    tests = [
        test_home_page,
        test_api_muscle_groups,
        test_api_exercises,
        test_exercises_filter_by_muscle,
        test_exercise_detail,
        test_register,
        test_login,
        test_create_workout,
        test_get_my_workouts,
        test_delete_workout,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} провален: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ошибка: {e}")
            failed += 1
    
    print(f"\nИтог: {passed} пройдено, {failed} провалено из {len(tests)}")