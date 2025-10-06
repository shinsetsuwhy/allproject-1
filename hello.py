import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ProjectMetricsAnalyzer:
    """Анализатор метрик проекта с улучшенной обработкой данных"""
    
    def __init__(self):
        self.metrics = {
            'project_info': {},
            'team_members': {},
            'project_status': 'Статус не определен',
            'tasks': {'in_progress': [], 'completed': [], 'upcoming': []}
        }
        self.valid_paths = [
            r"C:\Users\Student\Desktop\allproject\allproject-1\README.md",
            "README.md",
            "./README.md"
        ]
    
    def load_metrics(self) -> bool:
        """Загрузка метрик из файла"""
        for path in self.valid_paths:
            try:
                if os.path.exists(path):
                    print(f"Файл найден: {path}")
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    return self._parse_content(content)
            except Exception as e:
                print(f"Ошибка при чтении {path}: {e}")
        
        print("❌ Не удалось загрузить файл метрик")
        return False
    
    def _parse_content(self, content: str) -> bool:
        """Парсинг содержимого README.md"""
        try:
            # Основная информация о проекте
            self._extract_project_info(content)
            
            # Команда проекта
            self._extract_team_members(content)
            
            # Статус проекта
            self._extract_project_status(content)
            
            # Задачи
            self._extract_tasks(content)
            
            return True
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return False
    
    def _extract_project_info(self, content: str):
        """Извлечение основной информации о проекте"""
        patterns = {
            'educational_institution': r'-\s*\*\*Учебное заведение:\*\*\s*(.+)',
            'discipline': r'-\s*\*\*Дисциплина:\*\*\s*(.+)',
            'group': r'-\s*\*\*Группа:\*\*\s*(.+)',
            'creation_date': r'-\s*\*\*Дата создания:\*\*\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                self.metrics['project_info'][key] = match.group(1).strip()
    
    def _extract_team_members(self, content: str):
        """Извлечение информации о команде"""
        team_section = re.search(
            r'## Команда проекта\s*\n(.*?)(?=\n##|\n#|$)',
            content,
            re.DOTALL
        )
        
        if team_section:
            lines = team_section.group(1).strip().split('\n')
            for line in lines[2:]:  # Пропускаем заголовки таблицы
                if '|' in line and not line.startswith('|-'):
                    parts = [part.strip() for part in line.split('|') if part.strip()]
                    if len(parts) >= 2:
                        role = re.sub(r'\*\*', '', parts[0]).strip()
                        name = parts[1].strip()
                        self.metrics['team_members'][name] = role
    
    def _extract_project_status(self, content: str):
        """Определение статуса проекта"""
        status_checkboxes = re.findall(
            r'- \[(.)\] (В процессе разработки|На проверке|Завершен)',
            content
        )
        
        for marker, status in status_checkboxes:
            if marker.lower() == 'x':
                self.metrics['project_status'] = status
                break
    
    def _extract_tasks(self, content: str):
        """Извлечение информации о задачах"""
        task_sections = re.findall(
            r'### (Задачи в процессе|Выполненные задачи|Предстоящие задачи)\s*\n(.*?)(?=\n###|\n##|$)',
            content,
            re.DOTALL
        )
        
        section_mapping = {
            'Задачи в процессе': 'in_progress',
            'Выполненные задачи': 'completed', 
            'Предстоящие задачи': 'upcoming'
        }
        
        for section_name, tasks_content in task_sections:
            section_key = section_mapping.get(section_name)
            if section_key:
                tasks = re.findall(r'- \[.\] (.+)', tasks_content)
                self.metrics['tasks'][section_key] = [task.strip() for task in tasks if task.strip()]
    
    def find_user(self, search_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Поиск пользователя по имени с поддержкой частичного совпадения"""
        search_name = search_name.lower().strip()
        
        # Точное совпадение
        for name, role in self.metrics['team_members'].items():
            if search_name == name.lower():
                return name, role
        
        # Частичное совпадение по фамилии/имени
        for name, role in self.metrics['team_members'].items():
            name_lower = name.lower()
            # Проверяем фамилию, имя или их комбинации
            if (search_name in name_lower or
                any(part in name_lower for part in search_name.split()) or
                any(name_part in search_name for name_part in name_lower.split())):
                return name, role
        
        return None, None
    
    def get_user_greeting(self, name: str) -> Dict:
        """Формирование персонализированного приветствия"""
        full_name, role = self.find_user(name)
        
        if not full_name:
            return {
                'success': False,
                'message': f"Привет, {name}! К сожалению, вас нет в списке участников проекта.",
                'available_names': list(self.metrics['team_members'].keys())
            }
        
        # Персонализированные сообщения по ролям
        role_greetings = {
            'Тимлид проекта': f"Приветствую, {full_name}! 🎯 Как тимлид проекта вы отвечаете за координацию работы команды.",
            'Участник проекта': f"Добро пожаловать, {full_name}! 👨‍💻 Вы участник проекта - ваша работа очень важна для успеха.",
            'Заказчик проекта': f"Здравствуйте, {full_name}! 📊 Как заказчик проекта ваше мнение и feedback особенно ценны."
        }
        
        greeting = role_greetings.get(role, f"Привет, {full_name}! Рады видеть вас в проекте.")
        
        return {
            'success': True,
            'name': full_name,
            'role': role,
            'greeting': greeting,
            'project_status': self.metrics['project_status'],
            'project_info': self.metrics['project_info']
        }


class MetricsGreeter:
    """Интерактивная система приветствия по метрикам"""
    
    def __init__(self):
        self.analyzer = ProjectMetricsAnalyzer()
    
    def display_welcome(self):
        """Отображение приветственного сообщения"""
        print("\n" + "="*60)
        print("🎉 СИСТЕМА ПРИВЕТСТВИЯ ПО МЕТРИКАМ ПРОЕКТА")
        print("="*60)
    
    def display_user_metrics(self, user_data: Dict):
        """Отображение метрик пользователя"""
        if not user_data['success']:
            print(f"\n❌ {user_data['message']}")
            if user_data.get('available_names'):
                print("\n📋 Доступные имена в проекте:")
                for name in user_data['available_names']:
                    print(f"   • {name}")
            return
        
        print("\n" + "="*60)
        print(f"👤 ПРИВЕТСТВИЕ ДЛЯ: {user_data['name']}")
        print("="*60)
        print(f"💬 {user_data['greeting']}")
        print(f"🎭 Роль: {user_data['role']}")
        print(f"📈 Статус проекта: {user_data['project_status']}")
        
        # Дополнительная информация о проекте
        if user_data['project_info']:
            print("\n📊 Информация о проекте:")
            for key, value in user_data['project_info'].items():
                readable_key = key.replace('_', ' ').title()
                print(f"   • {readable_key}: {value}")
        
        print("="*60)
    
    def run(self):
        """Запуск интерактивной системы"""
        print("🔄 Загрузка метрик проекта...")
        
        if not self.analyzer.load_metrics():
            return
        
        self.display_welcome()
        
        while True:
            print(f"\n👥 Участники проекта: {', '.join(self.analyzer.metrics['team_members'].keys())}")
            print("\n💡 Подсказка: можно ввести полное ФИО или только фамилию/имя")
            print("❌ Введите 'выход' для завершения")
            
            user_input = input("\n🎯 Введите ваше имя: ").strip()
            
            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("\n👋 До свидания! Удачи в проекте!")
                break
            
            if not user_input:
                print("⚠️ Пожалуйста, введите имя")
                continue
            
            # Получение и отображение метрик
            user_metrics = self.analyzer.get_user_greeting(user_input)
            self.display_user_metrics(user_metrics)
            
            # Предложение продолжить
            if user_metrics['success']:
                continue_input = input("\n🔄 Хотите проверить другое имя? (да/нет): ").lower()
                if continue_input not in ['да', 'д', 'yes', 'y', '']:
                    print("\n👋 До свидания! Удачи в проекте!")
                    break


def main():
    """Основная функция программы"""
    try:
        greeter = MetricsGreeter()
        greeter.run()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()