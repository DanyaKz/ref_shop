from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import sys
import logging
import json
import time
import datetime
import random
from other_funcs import Other_Funcs
import asyncio
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import pandas as pd

class Admin_Init(Other_Funcs):
    def __init__(self):
        super().__init__()
        self.chanel_id = -1001770619243
        self.owner = 1299800437
        with open('keyboard.json', encoding='utf-8') as kb:
            self.KB = json.load(kb)

    async def send_course(self):
        get_last = self.get_last_course()
        get = InlineKeyboardButton('Приобрести за 100 руб.', callback_data=f"course{get_last['course_id']}")
        mark = InlineKeyboardMarkup().add(get)
        img = get_last['image']
        msg = f"{get_last['course_id']}.{get_last['title']}\n\n{get_last['descriptionn']}"
        msg_id = await self.bot.send_photo(self.chanel_id, 
                        open(f"photos/{img}" , 'rb'),
                        caption=msg,
                        reply_markup = mark)

        self.msg_db(get_last['course_id'],msg_id.message_id)


    async def admin_handler(self,data):
        get_admin = self.is_user_exists(data['user_id'])
        menu = InlineKeyboardButton('Выйти', callback_data='admin0')
        mark = InlineKeyboardMarkup().add(menu)
        if get_admin['act'] in range(3,6):
            course_id = self.get_last_course()['course_id']
        if get_admin['act'] == 11:#
            # self.set_action(111, get_admin['user_id'])
            yes = InlineKeyboardButton('Да', callback_data='admin2')
            mark.add(yes)
            self.add_msgs(data['msg'].text)
            await self.bot.send_message(get_admin['user_id'],
                f"Вы уверены, что хотите отправить \n\n<b><u>«{data['msg'].text}»</u></b> ?\n\nЕсли хотите изменить сообщение, то просто тут же напишите другое ",reply_markup = mark , parse_mode = 'HTML')
        elif get_admin['act'] == 2:
            self.title_db(data['msg'].text)
            self.set_action(3,data['user_id'])
            await self.bot.send_message(get_admin['user_id'],
                f"Далее напиши <b><u>описание</u></b> :",reply_markup = mark , parse_mode = 'HTML')
        elif get_admin['act'] == 3:
            self.desc_db({'course_id':course_id,'descriptionn':data['msg'].text})
            self.set_action(4,data['user_id'])
            await self.bot.send_message(get_admin['user_id'],
                f"Теперь вставь <b><u>ссылку</u></b> :",reply_markup = mark , parse_mode = 'HTML')
        elif get_admin['act'] == 4:
            self.link_db({'course_id':course_id, 'link':data['msg'].text })
            self.set_action(5,data['user_id'])
            await self.bot.send_message(get_admin['user_id'],
                f"Ну и на последок загрузи <b><u>картинку</u></b> :",reply_markup = mark , parse_mode = 'HTML')
        elif get_admin['act'] == 10:
            await self.delete_course_msg_handler(data)
        elif get_admin['act'] in range(6,9):
            
            await self.update_course(data)
        elif get_admin['act'] == 12:
            print(12)
            await self.find_course_msg_handler(data)
        await self.bot.delete_message(chat_id = data['msg'].chat.id ,message_id = data['msg'].message_id-1)

    async def delete_course_msg_handler(self,data):
        menu = InlineKeyboardButton('Выйти', callback_data='admin0')
        mark = InlineKeyboardMarkup().add(menu)
        try:
            course = self.get_course(int(data['msg'].text)) 
            if course:
                delete = InlineKeyboardButton('Да', callback_data=f"del{course['msg_id']}")
                change = InlineKeyboardButton('Изменить', callback_data=f"admin6")
                mark.add(delete,change)
                self.set_action(111,data['user_id'])
                await self.bot.send_photo(data['user_id'], 
                        open(f"photos/{course['image']}" , 'rb'),
                        caption=f"Вы действительно хотите удалить <b><u>{course['course_id']}.{course['title']}</u></b> ?",
                        reply_markup = mark,
                        parse_mode = 'HTML')
            else :
                await self.bot.send_message(data['user_id'],
                    f"Похоже, что вы ввели что-то не то.\n Бизнес-идеи <b><u>{data['msg'].text}</u></b> не существует.\n\n <b><u>Проверьте номер курса и попробуйте еще раз:</u></b>",
                    reply_markup = mark, parse_mode = 'HTML')
        except ValueError as e:
            await self.bot.send_message(data['user_id'],
                    f"Похоже, что вы ввели что-то не то.\n Ваше сообщение <b><u>{data['msg'].text}</u></b> не соответствует требованиям.\n\n <b><u>Введите порядковый номер только цифрами:</u></b>",
                    reply_markup = mark, parse_mode = 'HTML')


    async def send_to_users(self,data):
        get_all_users = self.get_active_users()
        get_admin = self.is_user_exists(data['user_id'])
        for i in get_all_users:
            try:
                await self.bot.send_message(i['user_id'],data['msg']['msg_text'])
            except :
                pass
        self.msg_sent(data['msg']['id_sent_messages'])
        self.set_action(111,data['user_id'])
        await self.bot.send_message(get_admin['user_id'],'Все пользователи были уведомлены!',reply_markup = data['mark'])
    
    async def find_course_msg_handler(self,data):
        menu = InlineKeyboardButton('Выйти', callback_data='admin0')
        mark = InlineKeyboardMarkup().add(menu)
        try:
            course = self.get_course(int(data['msg'].text)) 
            if course:
                self.set_action(111,data['user_id'])
                course = self.get_course(int(data['msg'].text))
                print(course)
                update_inline = {"inline_keyboard":[
                                [{
                                    "text":"Название",
                                    "callback_data":f"upd|1|{data['msg'].text}"
                                }],
                                [{
                                    "text":"Описание",
                                    "callback_data":f"upd|2|{data['msg'].text}"
                                    }],
                                [{
                                    "text":"Ссылка",
                                    "callback_data":f"upd|3|{data['msg'].text}"
                                    }],
                                [{
                                    "text":"Картинка",
                                    "callback_data":f"upd|4|{data['msg'].text}"
                                    }],
                                [{"text":"Выйти",
                                    "callback_data":"admin0"}]]}


                print(update_inline)
                await self.bot.send_photo(data['user_id'], 
                        open(f"photos/{course['image']}" , 'rb'),
                        caption=f"{course['course_id']}.{course['title']}\n\n{course['descriptionn']}\n\n{course['link']}\n\n<i><b>Выберите действие</b></i>",
                        reply_markup = update_inline,
                        parse_mode = 'HTML')
            else :
                await self.bot.send_message(data['user_id'],
                    f"Похоже, что вы ввели что-то не то.\n Бизнес-идеи <b><u>{data['msg'].text}</u></b> не существует.\n\n <b><u>Проверьте номер курса и попробуйте еще раз:</u></b>",
                    reply_markup = mark, parse_mode = 'HTML')
        except ValueError:
            
            await self.bot.send_message(data['user_id'],
                    f"Похоже, что вы ввели что-то не то.\n Ваше сообщение <b><u>{data['msg'].text}</u></b> не соответствует требованиям.\n\n <b><u>Введите порядковый номер только цифрами:</u></b>",
                    reply_markup = mark, parse_mode = 'HTML')
    
    async def update_course(self,data):
        act = ["название","описание","источник"]
        col = ['title','descriptionn','link']
        get_user = self.is_user_exists(data['user_id'])
        get_c_id = self.select_from_queue()['course_id']
        menu = InlineKeyboardButton('Выйти', callback_data='admin0')
        yes = InlineKeyboardButton('Да', callback_data=f"upd|{col[get_user['act']-6]}|{get_c_id}")
        mark = InlineKeyboardMarkup().add(menu,yes)

        self.update_last_queue({'col':col[get_user['act']-6], 'data': data['msg'].text})
        # act = self.get_act_name(get_user['act'])['act_name']
        msg = f"Вы действительно хотите изменить {act[get_user['act']-6]} на \n\n<u>{data['msg'].text}</u>? \n\nЕсли ты хочешь переписать, то просто введи {act[get_user['act']-6]} заново:"
        
        await self.bot.send_message(data['user_id'],
                    msg,
                    reply_markup = mark, parse_mode = 'HTML')
    
    async def daily_admin_response(self):
        resp = self.admin_response_db()
        resp = [['Юзеры',resp['resp_date']],['Вчера:',resp['yes_users']],['Всего:',resp['all_users']],[''],['Заработок',resp['resp_date']],['Вчера:',resp['yes_earn']],['Всего:',resp['all_earn']]]
        
        df = pd.DataFrame(resp)
        df.to_csv('response.csv', sep=';', index=False, encoding='utf-8-sig',header=False)

        with open("response.csv","rb") as response:
            await self.bot.send_document(self.owner,response,caption='Ежедневный отчет')

    async def send_to_developer(self,e):
        await self.bot.send_message(1032707306, e)



