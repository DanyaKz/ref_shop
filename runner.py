from message_handler import Message_init
import asyncio
import aioschedule
import json

class Runner(Message_init):
    def __init__(self):
        with open('config.json', encoding='utf-8') as mgs:
            self.config = json.load(mgs)
        self.token = self.config['bot_api']
        super().__init__(self.token)
        


    async def scheduler(self):
        aioschedule.every().day.at("07:00").do(self.daily_admin_response)
        aioschedule.every().day.at("07:30").do(self.daily_users_response)
        # aioschedule.every(10).seconds.do(self.dailоy_admin_response)
        aioschedule.every().day.at("08:00").do(self.daily_zero_users_response)
        aioschedule.every().day.at("08:30").do(self.daily_payment)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    async def on_startup(self,_):
        asyncio.create_task(self.scheduler())

    def run_funcs(self):
        self.start_handler()
        self.reg_callback_handler()
        self.qiwi_callback_handler()
        self.menu_callback_handler()
        self.get_new_callback_handler()
        self.pages()
        self.view_callback_handler()
        self.admin_callback_handler()
        self.delete_callback_handler()
        self.update_callback_handler()
        self.was_it_paid_callback_handler()
        # Hothing to input after this comment
        self.get_pic()
        self.all_messages_handler()
        self.execute_bot(self.on_startup)
    
    

bot = Runner()
try: 
    bot.run_funcs()
except Exception as e:
    # asyncio.create_task(bot.send_to_developer(e))
    bot.run_funcs()
