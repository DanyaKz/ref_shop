from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import sys
import logging
import json
import time
import random
from qiwi_init import Qiwi_init
from db import DataBase
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

class Other_Funcs(Qiwi_init):
    def __init__(self):
        super().__init__()
        # self.owner = 1299800437
        self.owner = 1032707306

    
    async def callback_speaker(self , **kwargs):
        if 'img' in kwargs:
            await self.bot.send_photo(kwargs['to'], 
                        open(f"photos/{kwargs['img']}" , 'rb'),
                        caption=kwargs['msg'],
                        reply_markup = kwargs['mark'],
                        parse_mode = 'HTML')
        else :
            await self.bot.send_message(kwargs['to'], 
                        text = kwargs['msg'] ,reply_markup = kwargs['mark'],parse_mode = 'HTML')
            # print('aa',msg)

    

    def format_info(self, message):
        to_add = {'first_name':'','username':''}

        for key in to_add:
            if key in message['from']:
                to_add[key] = message['from'][key]
            else:
                to_add[key] = 'null'
        to_add_1 = {
            'user_id':message['from']['id'],
            'parent':'null',
            'parent_for_tree':'null'
        }
        # проверить родителя
        if len(message['text'].split()) > 1:
            parent = message['text'].split()[1]
            if self.is_user_exists(parent):
                to_add_1['parent'] = parent
                to_add_1['parent_for_tree'] = self.get_user_s_id(parent)['id']
        
        to_return = {**to_add, **to_add_1}
        return to_return
        
    async def payment_message(self,data):
        #наличие курса
        print(data['user_id'] != data['owner'])
        if data['user_id'] != data['owner']:
            courses = self.select_from_courses(data['course_id'])
            if bool(courses):
                #проверка на наоичие у пользователя
                if bool(self.does_user_have_course(data)):
                    await self.bot.send_message(data['user_id'], 
                                    text = 'У вас уже имеется данный курс. Его можно найти в разделе <b>«Бизнес-идеи»➡️«Мои бизнес-идеи»</b>' , 
                                        parse_mode = 'HTML')
                else:
                    #act = free
                    data['comment'] =f"{courses['course_id']}---{courses['title']}"
                    link = self.create_payment(data)
                    inline_kb = {
                        "inline_keyboard":[
                            [{
                                "text" : "Оплатить",
                                "url":link
                            }],
                            [{
                                "text" : "Оплатил(а)",
                                "callback_data":"buy2"
                            }]]}
                    text = f"<b>Товар:</b> {courses['title']} \n\n<b>Цена:</b> {data['amount']} рублей"
                    await self.bot.send_message(data['user_id'], 
                                    text = text , reply_markup = inline_kb , parse_mode = 'HTML')
            else:
                await self.bot.send_message(data['user_id'], 
                                text = 'Данный курс больше не доступен к продаже' 
                                , parse_mode = 'HTML')
    
    async def before_check(self,user_id):
        check = self.check_payment(user_id)
        if isinstance(check,bool):
            if check:
                last_pay = self.get_last_payment(user_id)
                course = self.select_from_courses(int(last_pay['cooment'].split('---')[0]))
                self.add_to_cart({'user_id':user_id,'course_id':course['course_id']})
                await self.to_pay(user_id, last_pay['value_of_payment'])
                #send_course
                text = f"🥳 Успешная покупка 🥳\n<b>Товар -</b>{course['title']}\n\nПоздравляю с приобретением 😉\n{course['title']} {course['link']}"
                await self.bot.send_photo(user_id, 
                        open(f"photos/{course['image']}" , 'rb'),
                        caption=text,
                        parse_mode ='HTML')
                return True
            else:
                return False
        else:
            return check


    def menu(self):
        pass


    async def to_pay(self, user_id , amount):
        # print(self.get_parents(user_id))
        get_data = self.get_parents(user_id)
        if len(get_data['all_parents']) >= get_data['user_lvl'] and len(get_data['all_parents']) != 0:
            parent = get_data['all_parents'][-get_data['user_lvl']]
            parent_coin_lvl = self.get_coin_lvl(parent['user_id'])['lvl']
            print(parent,parent_coin_lvl,get_data['user_lvl'])
            if parent['user_id'] == self.owner:
                return 0
            if parent_coin_lvl >= get_data['user_lvl'] :
                print(parent_coin_lvl >= get_data['user_lvl'] )
                if get_data['user_lvl'] == 0:
                    print('chmo')
                else:
                    msg = f"Ваш рефер получил новый уровень, за который вы получате вознаграждение {amount/2} руб. \nВаши реферы:"
                    msg += self.combine_clidren_1_lvl(parent['user_id'])
                    print(msg)
                    print(parent['user_id'])
                    await self.bot.send_message(parent['user_id'],
                        msg, parse_mode = 'HTML')
                    if not self.pay_parent(parent['user_id'],amount/2):
                        await self.bot.send_message(parent['user_id'],
                        'К сожалению, деньги не получилось отправить, но они были сохранены и утром бот попробует отправить их снова, а пока проверь правильность своего номера, который находится в «меню» - «мои данные», либо же проверь лимиты своего кошелька')
            else:
                await self.bot.send_message(parent['user_id'],
                    'Ваш рефер превзошел вас и вы упустили возможность заработать. Советую повысить уровень!')
        else : 
            print('Весь кэш админу')
    
    def try_parse_number(self,digit):
        try:
            int(digit)
            if digit[0] in ['+','-']:
                digit = digit[1:]
            return digit, True
        except ValueError:
            return digit, False

    def combine_clidren_1_lvl(self, user_id):
        children = self.get_data_children_1_lvl(user_id)
        to_return = '\n'
        if len(children) > 0:
            for i in range(len(children)):
                to_return += f"""    <i><a href = "https://web.telegram.org/z/#{children[i]['user_id']}">«{children[i]['first_name']}»</a></i>,"""
        return to_return[:-1]
    
    async def courses_list(self, message, page , isFirst = False):
            user_id = message['from']['id']
            users_courses = self.get_users_courses(page,user_id)
            last_page = self.get_len(user_id)['count(1)']
            msg = f'Ваши приобретенные курсы (количество - {last_page}):'
            mark_up = {"inline_keyboard":[]}
            for i in range(len(users_courses)):
                a_course = self.get_course(users_courses[i]['course_id'])
                to_append = [{"text":f"{a_course['title']}","callback_data":f"view{a_course['course_id']}"}]
                mark_up["inline_keyboard"].append(to_append)
            print(last_page)
            next_p = [{"text":f"След. стр. #️⃣ {page+1}","callback_data":"get_more"}]
            prev_p = [{"text":f"Пред. стр. #️⃣ {page-1}","callback_data":"get_prev"}]
            both_p = [prev_p[0],next_p[0]]
            if last_page > 5:
                if isFirst or page == 1:
                    mark_up["inline_keyboard"].append(list(next_p))
                elif ((page == (last_page//5) + 1) and last_page % 5 != 0) or ((page == last_page//5) and last_page % 5 == 0):
                    mark_up["inline_keyboard"].append(list(prev_p))
                else:
                    mark_up["inline_keyboard"].append(both_p)
            mark_up["inline_keyboard"].append([{"text":f"Главное меню","callback_data":"menu0"}])

            await self.bot.send_message(text = msg , chat_id = user_id,
                                        reply_markup = mark_up, parse_mode = "HTML")
    
    async def my_children(self, user_id):
        get_user = self.is_user_exists(user_id)
        children = self.children_lvl_count(user_id)
        children_plus_lvl = self.children_plus_lvl_count(user_id)
        msg = '<i>'
        if bool(len(children)):
            msg += 'Твои рефералы:\n'
            for i in children:
                msg += f"{i['floor']}ур. - {i['c']} чел.\n"
        else:
            msg += f"К сожалению, рефералов , соответствующих твоему уровню, нет."
        msg += f"\nСовет💡\nТы получаешь реферальные с уровней, эквивалентному твоему.\nУ тебя «{get_user['lvl']}» уровень.\n"
        if bool(children_plus_lvl['floor']):
            msg += f"На «{children_plus_lvl['floor']}» уровне – {children_plus_lvl['c']} рефералов.\nСоветую поднять уровень.\nПотенциальный бонус с «{children_plus_lvl['floor']}» уровня – «{children_plus_lvl['c'] * 50}» руб.\n"
        
        msg += '</i>'
        print(msg)
        mark_up = {"inline_keyboard":[[{"text":f"Приобрести Бизнес-идею ","url":"https://t.me/SIYP_ideas"}],
        [{"text":f"Меню","callback_data":"menu0"}]]}
        await self.bot.send_message(user_id, 
                            text = msg ,
                                reply_markup = mark_up , parse_mode = 'HTML')
    
    async def my_salary(self, user_id):
        salary = self.my_salary_db(user_id)['value']
        children = self.children_1_lvl(user_id)['c']
        msg = f"Всего - {salary} руб.\nТы пригласил всего - {children} реф."
        mark_up = {"inline_keyboard":[[{"text":f"Меню","callback_data":"menu0"}]]}
        await self.bot.send_message(user_id, 
                            text = msg , 
                                reply_markup = mark_up , parse_mode = 'HTML')
    
    async def daily_users_response(self):
        users = self.users_over_lower_1_lvl('>')
        lvl_up = InlineKeyboardButton('Повысить уровень', url='https://t.me/SIYP_ideas')
        earn_up = InlineKeyboardButton('Повысить заработок', url='https://t.me/+q6shxvXPtZZiNjli')
        mark = InlineKeyboardMarkup().add(lvl_up).add(earn_up)
        try:
            for u in users:
                if u['user_id'] != self.owner:
                    i = self.users_response_db(u['user_id'])
                    msg = f"Утро доброе 😉\nПодготовил тут для тебя отчет 🤗\n\nРефералы:\nТвой уровень – «{i['user_lvl']}».\nТвои рефералы 1го уровня – «{i['children_first_lvl']}».\nРефералы всех уровней – {i['all_children']}.\nНовых рефералов «вчерашняя дата» - {i['new_first_lvl']}.\n\nТвой заработок:\nЗа «{i['daily_date']}» - {i['earned_yesterday']} руб.\nЗа все время – {i['erned_all']} руб.\n\nТвой баланс – «{i['balance']}» руб.\n{'<b>Проверь лимиты кошелька</b>' if i['balance'] != 0 else ''} \n💡 Совет:\nТвой уровень – «{i['user_lvl']}».\nТы получаешь 50% - с 1 по «{i['user_lvl']}» ур.\nНа «{i['user_lvl']+1}» уровне у тебя – «{i['children_nex_lvl']}» реф.\nВозможный доход от уровня – «{i['children_nex_lvl']*50}» руб.\nСоветую повысить уровень.\n\n💡 Совет:\nТвой заработок развивается быстрее и эффективней, когда ты приглашаешь больше рефералов.\nСоветую посетить канал и максимизировать свой доход 😉"
                    await self.bot.send_message(u['user_id'], 
                                text = msg , 
                                    reply_markup = mark , parse_mode = 'HTML')
        except Exception as e:
            print(e)
    
    async def daily_zero_users_response(self):
        users = self.users_over_lower_1_lvl('<')
        lvl_up = InlineKeyboardButton('Бизнес-идеи', url='https://t.me/SIYP_ideas')
        mark = InlineKeyboardMarkup().add(lvl_up)
        try:
            for i in users:
                msg = "Привет! 😉\nТы еще не определился с Бизнес-идеей?\n\nСоветую сделать это быстрей!\nПока ты думаешь – другие зарабатывают 🤑"
                await self.bot.send_message(i['user_id'], 
                            text = msg , 
                                reply_markup = mark , parse_mode = 'HTML')
        except Exception as e:
            pass
