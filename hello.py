import os
import re

def read_metrics_from_file(file_path):
    """Чтение метрик из файла README.md"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Файл {file_path} не найден!")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None

def parse_metrics(content):
    """Парсинг метрик из содержимого файла"""
    metrics = {
        'team_members': {},
        'project_status': '',
        'in_progress_tasks': [],
        'completed_tasks': [],
        'upcoming_tasks': []
    }
    
    # Парсинг участников команды
    team_section = re.search(r'## Команда проекта\s*\n(.*?)\n\n', content, re.DOTALL)
    if team_section:
        team_lines = team_section.group(1).strip().split('\n')
        for line in team_lines[2:]:  # Пропускаем заголовок и разделитель
            if '|' in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) >= 2:
                    role = re.sub(r'\*\*', '', parts[0])  # Убираем **
                    name = parts[1]
                    metrics['team_members'][name] = role
    
    # Парсинг статуса проекта
    status_match = re.search(r'- \[(x| )\] В процессе разработки\s*- \[(x| )\] На проверке\s*- \[(x| )\] Завершен', content)
    if status_match:
        statuses = status_match.groups()
        if statuses[0] == 'x':
            metrics['project_status'] = 'В процессе разработки'
        elif statuses[1] == 'x':
            metrics['project_status'] = 'На проверке'
        elif statuses[2] == 'x':
            metrics['project_status'] = 'Завершен'
        else:
            metrics['project_status'] = 'Статус не определен'
    
    return metrics

def get_user_metrics(name, metrics):
    """Получение метрик для конкретного пользователя"""
    user_metrics = {
        'name': name,
        'role': 'Не найден в команде',
        'project_status': metrics.get('project_status', 'Не определен'),
        'message': ''
    }
    
    if name in metrics['team_members']:
        user_metrics['role'] = metrics['team_members'][name]
        
        # Создаем персонализированное сообщение в зависимости от роли
        if 'Тимлид' in user_metrics['role']:
            user_metrics['message'] = f"Приветствую, {name}! Как тимлид проекта вы отвечаете за координацию работы."
        elif 'Участник' in user_metrics['role']:
            user_metrics['message'] = f"Добро пожаловать, {name}! Вы участник проекта - важная часть команды."
        elif 'Заказчик' in user_metrics['role']:
            user_metrics['message'] = f"Здравствуйте, {name}! Как заказчик проекта ваше мнение особенно ценно."
        else:
            user_metrics['message'] = f"Привет, {name}! Рады видеть вас в проекте."
    else:
        user_metrics['message'] = f"Привет, {name}! К сожалению, вы не найдены в списке участников проекта."
    
    return user_metrics

def display_metrics(user_metrics):
    """Отображение метрик пользователя"""
    print("\n" + "="*50)
    print(f"ПРИВЕТСТВИЕ ДЛЯ: {user_metrics['name']}")
    print("="*50)
    print(user_metrics['message'])
    print(f"Роль в проекте: {user_metrics['role']}")
    print(f"Статус проекта: {user_metrics['project_status']}")
    print("="*50)

def main():
    # Пути к файлу README.md
    paths = [
        r"C:\Users\shinsetsu\Documents\первой важности\репозитории\allproject\README.md",
        "README.md",
        "./README.md"
    ]
    
    content = None
    for path in paths:
        print(f"Попытка чтения файла: {path}")
        content = read_metrics_from_file(path)
        if content:
            print("Файл успешно прочитан!")
            break
    
    if not content:
        print("Не удалось найти файл README.md")
        return
    
    # Парсинг метрик
    metrics = parse_metrics(content)
    
    # Основной цикл программы
    while True:
        print("\n" + "="*30)
        print("СИСТЕМА ПРИВЕТСТВИЯ ПО МЕТРИКАМ")
        print("="*30)
        print("Доступные имена:")
        for name in metrics['team_members']:
            print(f"- {name}")
        print("\nВведите 'выход' для завершения программы")
        
        name = input("\nВведите ваше ФИО: ").strip()
        
        if name.lower() == 'выход':
            print("До свидания!")
            break
        
        if not name:
            print("Пожалуйста, введите имя!")
            continue
        
        # Поиск точного совпадения
        user_metrics = get_user_metrics(name, metrics)
        
        # Если точное совпадение не найдено, ищем частичное
        if user_metrics['role'] == 'Не найден в команде':
            found = False
            for full_name in metrics['team_members']:
                if name.lower() in full_name.lower():
                    user_metrics = get_user_metrics(full_name, metrics)
                    found = True
                    break
            
            if not found:
                print(f"Имя '{name}' не найдено в метриках проекта.")
                continue
        
        display_metrics(user_metrics)
        
        # Предложение продолжить
        cont = input("\nХотите проверить другое имя? (да/нет): ").lower()
        if cont not in ['да', 'д', 'yes', 'y']:
            print("До свидания!")
            break

if __name__ == "__main__":
    main()