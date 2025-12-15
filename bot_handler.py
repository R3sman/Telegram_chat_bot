import telebot
from typing import Dict
from config.settings import settings
from agents.coordinator import CoordinatorAgent

class TelegramBotHandler:
    """Обработчик Telegram бота"""
    
    def __init__(self):
        self.bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
        self.coordinator = CoordinatorAgent()
        self.user_sessions: Dict[int, Dict] = {}
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            welcome_text = (
                "Добро пожаловать в AutoBot! Чат-бот предназначен для автовладельцев и может дать ответы на вопросы по эксплуатации Вашего автомобиля.\n\n"
                "Доступные команды:\n"
                "/load_pdf - Загрузить PDF файл из перечня доступных моделей автомобилей\n"
                "/status - Статус системы\n"
                "/help - Эта справка\n\n"
                "Как пользоваться:\n"
                "1. Нажмите /load_pdf\n"
                "2. Выберите файл из списка\n"
                "3. Задавайте вопросы"
            )
            self.bot.reply_to(message, welcome_text)
        
        @self.bot.message_handler(commands=['load_pdf'])
        def handle_load_pdf(message):
            """Показать список доступных PDF файлов"""
            available_files = [
                "Chery_Tiggo7ProMax.pdf",
                "Geely_coolray.pdf", 
                "Haval_Jolion.pdf",
                "Lada_Granta.pdf",
                "Lada_Vesta.pdf"
            ]
            
            files_text = "\n".join([f"• {file}" for file in available_files])
            
            response = f"""Выберите PDF файл для загрузки:

{files_text}

Просто отправьте название файла (например: Lada_Vesta.pdf)"""
            
            self.bot.reply_to(message, response)
            
            self.user_sessions[message.chat.id] = {"waiting_for_pdf": True}
        
        @self.bot.message_handler(commands=['status'])
        def handle_status(message):
            status = self.coordinator.get_system_status()
            status_text = f"""
            Статус системы:
            
            • PDF загружен: {'✅' if status['pdf_loaded'] else '❌'}
            • База данных: {status['vector_db_status']}
            • Агенты: {status['agents_status']}
            
            Используйте /load_pdf для загрузки документов
            """
            self.bot.reply_to(message, status_text)
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            """Обработка ВСЕХ сообщений"""
            user_id = message.chat.id
            
            if user_id in self.user_sessions and self.user_sessions[user_id].get("waiting_for_pdf"):
                pdf_filename = message.text.strip()
                
                allowed_files = [
                    "Chery_Tiggo7ProMax.pdf",
                    "Geely_coolray.pdf", 
                    "Haval_Jolion.pdf",
                    "Lada_Granta.pdf",
                    "Lada_Vesta.pdf"
                ]
                
                if pdf_filename not in allowed_files:
                    self.bot.reply_to(message, f"Файл '{pdf_filename}' не найден в списке доступных. Пожалуйста, выберите из списка выше.")
                    return
                
                processing_msg = self.bot.reply_to(message, f"Загружаю файл '{pdf_filename}'...")
                
                try:
                    response = self.coordinator.load_pdf(pdf_filename)
                    self.bot.delete_message(message.chat.id, processing_msg.message_id)
                    self.bot.reply_to(message, response)
                except Exception as e:
                    self.bot.delete_message(message.chat.id, processing_msg.message_id)
                    self.bot.reply_to(message, f"Ошибка при загрузке: {str(e)}")
                
                del self.user_sessions[user_id]
                
            elif message.text.startswith('/'):
                self.bot.reply_to(message, "Неизвестная команда. Используйте /help для списка команд")
                
            else:
                if not self.coordinator.pdf_loaded:
                    self.bot.reply_to(message, "Сначала загрузите PDF-файл командой /load_pdf")
                    return

                question = message.text
                processing_msg = self.bot.reply_to(message, "🔍 Ищу информацию в документах...")
                
                try:
                    response = self.coordinator.process_query(question)
                    self.bot.delete_message(message.chat.id, processing_msg.message_id)
                    self.bot.reply_to(message, response)
                except Exception as e:
                    self.bot.delete_message(message.chat.id, processing_msg.message_id)
                    self.bot.reply_to(message, f"Ошибка при обработке вопроса: {str(e)}")
    
    def run(self):
        """Запуск бота"""
        print("Telegram бот запущен...")
        self.bot.infinity_polling()