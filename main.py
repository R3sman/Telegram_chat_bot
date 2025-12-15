import os
import sys
from telegram_bot.bot_handler import TelegramBotHandler
from utils.file_processor import create_folders, check_environment

def main():
    """Главная функция приложения"""
    print("="*60)
    print("🚀 Запуск системы из 4 LLM-агентов с Telegram ботом")
    print("="*60)
    
    # Создание папок
    print("\n📁 Проверка структуры папок...")
    create_folders()
    
    # Проверка окружения
    print("🔧 Проверка окружения...")
    if not check_environment():
        sys.exit(1)
    
    # Проверка наличия папки с PDF
    if not os.path.exists("data/pdf_files"):
        os.makedirs("data/pdf_files", exist_ok=True)
        print("📁 Создана папка data/pdf_files/")
        print("   Поместите ваши PDF-файлы в эту папку")
    
    print("\n" + "="*60)
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("="*60)
    
    print("\n📋 Созданные агенты:")
    print("   1. 📄 PDFAnalyzerAgent - анализ PDF файлов")
    print("   2. 🔍 SearchAgent - поиск в векторной базе")
    print("   3. 💬 ResponseFormatterAgent - генерация ответов через GigaChat")
    print("   4. 🎯 CoordinatorAgent - координация всех агентов")
    
    print("\n📋 Структура проекта:")
    project_structure = """
    llm_agents_system/
    ├── config/           - Конфигурация
    ├── agents/           - 4 LLM-агента
    ├── database/         - Векторная база данных
    ├── telegram_bot/     - Telegram бот
    ├── utils/            - Вспомогательные функции
    ├── data/             - Данные и PDF файлы
    ├── .env             - Переменные окружения
    └── main.py          - Главный файл
    """
    print(project_structure)
    
    print("\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
    print("   • Убедитесь, что в папке data/pdf_files есть PDF файлы")
    print("   • Убедитесь, что в .env файле указаны корректные ключи API")
    print("   • Для загрузки PDF используйте команду: /load_pdf имя_файла.pdf")
    
    print("\n" + "="*60)
    print("🤖 Запуск Telegram бота...")
    print("="*60)
    print("\nДля остановки нажмите Ctrl+C\n")
    
    try:
        # Запуск Telegram бота
        bot_handler = TelegramBotHandler()
        bot_handler.run()
        
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
        print("Система остановлена пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        print("\nВозможные причины:")
        print("1. Неверный Telegram bot token в .env файле")
        print("2. Неверный GigaChat API ключ")
        print("3. Проблемы с интернет-соединением")
        print("4. Отсутствие PDF файлов в data/pdf_files/")
        sys.exit(1)

if __name__ == "__main__":
    main()