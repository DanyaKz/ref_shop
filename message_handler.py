import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import sys
import logging
import json
import time
import datetime
import io
import random
from admin_init import Admin_Init
import asyncio
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton ,ContentType, InputMedia, InputFile
import os

class Message_init(Admin_Init):
    def __init__(self,API_TOKEN):
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.bot = Bot(token=API_TOKEN)
        self.dp = Dispatcher(self.bot)
        self.owner = 1299800437 #owner's telegram id
        # self.owner = 1032707306
        with open('messages.json', encoding='utf-8') as mgs:
            self.list_of_msgs = json.load(mgs)
        with open('keyboard.json', encoding='utf-8') as kb:
            self.KB = json.load(kb)

    def execute_bot(self,on_startup): 
        executor.start_polling(self.dp, skip_updates=True,on_startup=on_startup)

    def start_handler(self):
        @self.dp.message_handler(commands=['start'])
        async def process_start_command(message: types.Message):
            print(message)
            user_id = message['from']['id']
            isExists = self.is_user_exists(user_id)
            if user_id == self.owner:
                await self.bot.send_message(self.owner, 'Административное меню',reply_markup=self.KB['admin'])
            else:
                if bool(isExists):
                    if isExists['lvl'] < 1:
                        print(self.KB['primitive_messages'][0]['new_user'],self.list_of_msgs['primitive_messages'][0]['start'])
                        await self.bot.send_message(user_id, self.list_of_msgs['primitive_messages'][0]['start'], 
                                    reply_markup=self.KB['primitive_messages'][0]['new_user'],
                                    parse_mode = 'HTML')
                    else : 
                        await self.callback_speaker(msg = 'Главное меню:', 
                                                mark=self.KB['menu'],
                                                to = user_id)
                else:
                    data = self.format_info(dict(message))
                    self.add_user(data)
                    await self.bot.send_message(user_id, self.list_of_msgs['primitive_messages'][0]['start'], 
                                    reply_markup=self.KB['primitive_messages'][0]['new_user'],
                                    parse_mode = 'HTML')


    def all_messages_handler(self):
        @self.dp.message_handler(content_types=['text'])
        async def all_msgs(message: types.Message):
            user_id = message['from']['id']
            get_user = self.is_user_exists(user_id)
            if message.from_user.id == self.owner:
                # keyboard = {'keyboard':[['Административное меню']]}
                if message.text and get_user['act'] == 111:
                    await self.callback_speaker(msg = 'Административное меню:', 
                                            mark=self.KB['admin'],
                                            to = user_id)
                else:
                    await self.admin_handler({'msg':message, 'user_id':user_id})

            else:
                # keyboard =  {'keyboard':[['Главное меню']]}
                if get_user['act'] == 111 :
                    if get_user['registration']:
                        # menu panel reply kb
                        # print(self.get_len(user_id))
                        await self.callback_speaker(msg = 'Главное меню:', 
                                                mark=self.KB['menu'],
                                                to = user_id)
                    else:
                        await self.bot.send_message(user_id,
                            'Друг, для полного доступа к боту, тебе необходимо завершить регистрацию!')
                elif get_user['act'] == 1:
                    #ввод и подтверждение телефона
                    number = self.try_parse_number(message.text)
                    if number[1]:
                        if self.is_number_exists(number[0]):
                            await self.bot.send_message(user_id, 'Номер, который вы ввели, уже занят! Введите другой номер:', 
                                reply_markup=self.KB['primitive_messages'][11]['phone_number'],
                                parse_mode = 'HTML')
                        else:
                            self.set_action(111,user_id)
                            self.set_number(number[0], user_id)
                            print(get_user['phone_number'])
                            await self.bot.send_message(user_id, self.list_of_msgs['is_number_correct'].replace('***', '+'+number[0]), 
                                    reply_markup=self.KB['is_number_correct'],
                                    parse_mode = 'HTML')
                    else:
                        # self.set_action(1,user_id)
                        await self.bot.send_message(user_id, 
                            f'Ваш номер телефона <b><u>{number[0]}</u></b> введен неверно\n'+self.list_of_msgs['primitive_messages'][11]['phone_number'], 
                            reply_markup=self.KB['primitive_messages'][11]['phone_number'],
                            parse_mode = 'HTML')

    def get_pic(self):
        @self.dp.message_handler(content_types=[ContentType.PHOTO])
        async def picture(message):
            print(message)
            try:
                user_id = message['from']['id']
                get_user = self.is_user_exists(user_id)
                if get_user['user_id'] == self.owner and get_user['act'] == 5:
                    print(1)
                    await self.bot.delete_message(chat_id = message.chat.id ,message_id = message.message_id-1)
                    img = await message.photo[-1].download()
                    image = img.name.split('/')[1]
                    last_course = self.get_last_course()
                    yes = InlineKeyboardButton('Да', callback_data='admin9')
                    again = InlineKeyboardButton('Заполнить заново', callback_data='admin4')
                    menu = InlineKeyboardButton('Сбросить и выйти', callback_data='admin0')
                    mark = InlineKeyboardMarkup().add(yes,again)
                    mark.add(menu)
                    self.image_db({'course_id':last_course['course_id'],'image':image})
                    msg = f"Сохраняем?\n\n{last_course['course_id']}.{last_course['title']}\n\n{last_course['descriptionn']}\n\n{last_course['link']}"
                    await self.callback_speaker(msg= msg, 
                                                    mark = mark,
                                                    to = user_id,
                                                    img = f"{image}")
                elif get_user['user_id'] == self.owner and get_user['act'] == 9:
                    print(2)
                    img = await message.photo[-1].download()
                    image = img.name.split('/')[1]
                    get_c_id = self.select_from_queue()['course_id']
                    self.update_last_queue({'col':'image', 'data': image})
                    yes = InlineKeyboardButton('Да', callback_data=f'upd|image|{get_c_id}')
                    menu = InlineKeyboardButton('Сбросить и выйти', callback_data='admin0')
                    mark = InlineKeyboardMarkup().add(yes).add(menu)

                    msg = f"Сохраняем?"
                    await self.callback_speaker(msg= msg, 
                                                    mark = mark,
                                                    to = user_id,
                                                    img = f"{image}")
                elif get_user['user_id'] == self.owner and get_user['act'] == 13:
                    print(2)
                    img = await message.photo[-1].download()
                    image = img.name.split('/')[1]
                    self.add_pic_msgs(image)
                    menu = InlineKeyboardButton('Сбросить и выйти', callback_data='admin0')
                    mark = InlineKeyboardMarkup().add(menu)

                    await self.bot.send_message(user_id , "Ну и на последок напиши данные для кнопки в формате \n\n<b><i><u>ТЕКСТ КНОПКИ</u> - <u>ССЫЛКА</u></i></b>",
                    parse_mode = 'HTML',
                    reply_markup= mark)
                    self.set_action(14,user_id)

                await self.bot.delete_message(chat_id = message.chat.id ,message_id = message.message_id-1)
                
            except Exception as e:
                print(e)



    def reg_callback_handler(self):
        @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'))
        async def main_handler(call: types.CallbackQuery):
            print(call)
            print(call.data)
            code_length = len(call.data)
            code = call.data[-(code_length-3):]
            user_id = call['from']['id']
            get_user = self.is_user_exists(user_id)
            print(not get_user['registration'])
            if code.isdigit():
                code = int(code)
            # print(not get_user['registration'] and code != 11)
            if not get_user['registration']:
                
                if code in range(1,4) and code in [11,12]:
                    await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                if code in range(0,12):
                    
                    inl_kb , msg = list(self.KB['primitive_messages'][code].values())[0] , list(self.list_of_msgs['primitive_messages'][code].values())[0]
                    print(inl_kb,msg)
                    if code == 3:
                        await self.callback_speaker(msg= msg, 
                                                    mark = inl_kb,
                                                    to = user_id,
                                                    img = '1.png')
                    else:
                        await self.callback_speaker(msg= msg, 
                                                    mark = inl_kb,
                                                    to = user_id)
                    
                    
            else:
                await call.answer('Вы уже завершили регистрацию 🤗' ,show_alert = True)
                await self.callback_speaker(msg= 'Главное меню:', 
                                                    mark = self.KB['menu'],
                                                    to = user_id)
    
    
    def was_it_paid_callback_handler(self):
        @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('paid'))
        async def main_handler(call: types.CallbackQuery):
            print(call)
            print(call.data)
            code_length = len(call.data)
            code = call.data[-(code_length-4):]
            user_id = call['from']['id']
            get_user = self.is_user_exists(user_id)
            check = await self.before_check(user_id,int(code))
            print(check)
            if isinstance(check,bool):
                print(1)
                if check:
                    if not get_user['registration']:
                        await self.callback_speaker(msg = self.list_of_msgs['primitive_messages'][4]['wanna_earn'], 
                                            mark=self.KB['primitive_messages'][4]['wanna_earn'],
                                            to = user_id)
                    await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                else :
                    await call.answer(text='Вы еще не оплатили. Если же вы оплатили, то попробуйте подтвердить оплату через несколько минут.',show_alert=True)
            else:
                await call.answer(text=check,show_alert=True)
                await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                


    def qiwi_callback_handler(self):
        @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('buy'))
        async def main_handler(call: types.CallbackQuery):
            print(call)
            print(call.data)
            code_length = len(call.data)
            code = call.data[-(code_length-3):]
            user_id = call['from']['id']
            get_user = self.is_user_exists(user_id)
            print(code)
            if code.isdigit():
                    code = int(code)
            if code == 1:
                to_send = {'amount':10,
                            'user_id':user_id,
                            'course_id':1,
                            'owner':self.owner
                            }
                print(code)
                await self.payment_message(to_send)
                print(code)
            # elif code == 2:
                
            elif code == 3:
                self.set_action(1,user_id)
                if get_user['registration']:
                    await self.callback_speaker(msg = self.list_of_msgs['primitive_messages'][11]['phone_number'], 
                                                mark=self.KB['primitive_messages'][11]['phone_number'],
                                                to = user_id)
                else: 
                    await self.bot.send_message(user_id,self.list_of_msgs['primitive_messages'][11]['phone_number'] , parse_mode='HTML')
            elif code == 4:
                self.set_action(111,user_id)
                await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                await self.callback_speaker(msg = 'Главное меню:', 
                                            mark=self.KB['menu'],
                                            to = user_id)
            elif code == 5:
                await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                msg = list(self.list_of_msgs['primitive_messages'][12].values())[0]

                if not get_user['registration']:
                    self.set_reg_done(user_id)
                    await self.callback_speaker(msg =  msg.replace('ref_link',get_user['personal_link']), 
                                            mark=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Главное меню')),
                                            to = user_id)
                    
                else:
                    await self.bot.send_message(user_id, 
                        text = ' '.join(msg.split('\n')[:2]) ,parse_mode = 'HTML', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Главное меню')))
                    await self.callback_speaker(msg = 'Главное меню:', 
                                            mark=self.KB['menu'],
                                            to = user_id)
            elif code == 6:
                inl_kb , msg = list(self.KB['primitive_messages'][11].values())[0] , list(self.list_of_msgs['primitive_messages'][11].values())[0]
                self.set_action(1,user_id)
                await self.callback_speaker(msg= msg, 
                                            mark = inl_kb,
                                            to = user_id)
    
    def menu_callback_handler(self):
        @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('menu'))
        async def main_handler(call: types.CallbackQuery):
            print(call)
            print(call.data)
            code_length = len(call.data)
            code = int(call.data[-(code_length-4):])
            user_id = call['from']['id']
            get_user = self.is_user_exists(user_id)
            print(code)
            await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
            code_0_3 = [['Главное меню','menu'],['Бизнес-идеи','business_ideas'],['Рефералка','referal']]
            menu = InlineKeyboardButton('Меню', callback_data='menu0')
            mark = InlineKeyboardMarkup()
            if code in [0,1,2]:
                print(code_0_3[code][1])
                await self.callback_speaker(msg = code_0_3[code][0], 
                                            mark=self.KB[code_0_3[code][1]],
                                            to = user_id)
            elif code == 3:
                correct = InlineKeyboardButton('Исправить', callback_data='buy6')
                mark.add(correct, menu)
                await self.callback_speaker(msg = f"<i>Твой QIWI-кошелек для получения реферальных бонусов:\n<b><u>+{get_user['phone_number']}</u></b></i>", 
                                            mark=mark,
                                            to = user_id)
            elif code == 4:
                balance = get_user['balance']
                mark.add(menu)
                msg = self.list_of_msgs['balance'].replace('balance', str(balance))
                await self.callback_speaker(msg = msg, 
                                            mark=mark,
                                            to = user_id)
            elif code == 5:
                get = InlineKeyboardButton('Приобрести', url='https://t.me/SIYP_ideas/7')
                mark.add(get,menu)
                await self.callback_speaker(msg = "Перейди в канал с Бизнес-идеями.\nВыбери необходимую.\nНажми «Приобрести»", 
                                            mark=mark,
                                            to = user_id)
            elif code == 6:
                await self.courses_list(call, 1 , True)
            elif code in [7,11]:
                if code == 7:
                    more = InlineKeyboardButton('Давай',callback_data='menu11')
                    mark.add(more)
                    msg = self.list_of_msgs['ref_inf'][0]
                else :
                    msg = self.list_of_msgs['ref_inf'][1].replace('link',get_user['personal_link'])
                mark.add(menu)
                await self.callback_speaker(msg = msg, 
                                            mark=mark,
                                            to = user_id)
            elif code == 8:
                await self.my_children(user_id)
            elif code == 9:
                mark.add(menu)
                await self.bot.send_message(user_id,f"Твоя реферальная ссылка для приглашения пользователей:", parse_mode='HTML')
                await self.bot.send_message(user_id,f"<b><i>{get_user['personal_link']}</i></b>", parse_mode='HTML', disable_web_page_preview=True)
                await self.callback_speaker(msg = f"Ты всегда можешь ее найти в меню.\nВ разделе «Рефералка».", 
                                            mark=mark,
                                            to = user_id)
            elif code == 10:
                await self.my_salary(user_id)

    
    def get_new_callback_handler(self):
            @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('course'))
            async def main_handler(call: types.CallbackQuery):
                print(call)
                print(call.data)
                code_length = len(call.data)
                code = int(call.data[-(code_length-6):])
                user_id = call['from']['id']
                get_user = self.is_user_exists(user_id)
                try:
                    course = self.get_course(code)
                    course['user_id'] = user_id
                    course['amount'] = 100
                    course['owner'] = self.owner
                    await self.payment_message(course)
                except Exception as e:
                    print(e)
    
    def view_callback_handler(self):
            @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('view'))
            async def main_handler(call: types.CallbackQuery):
                print(call)
                print(call.data)
                code_length = len(call.data)
                code = int(call.data[-(code_length-4):])
                user_id = call['from']['id']
                get_course = self.get_course(code)
                try:
                    if int(user_id) == self.owner:
                        back = InlineKeyboardButton('Назад', callback_data='admin1')
                        menu = InlineKeyboardButton('Меню', callback_data='admin0')
                    else:
                        back = InlineKeyboardButton('Вернуться к списку', callback_data='menu6')
                        menu = InlineKeyboardButton('Меню', callback_data='menu0')
                    mark = InlineKeyboardMarkup().add(back,menu)
                    msg = f"<b>{get_course['title']}</b>\n\n{get_course['descriptionn']} \n{get_course['link']}"
                    await self.callback_speaker(msg = msg, mark=mark,
                                            to = user_id, img = get_course['image'])
                    await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                except:
                    pass

    def delete_callback_handler(self):
        @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('del'))
        async def del_handler(call: types.CallbackQuery):
            try:
                await self.bot.delete_message(chat_id = self.chanel_id ,message_id = int(call.data[3:]))
                await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                await self.callback_speaker(to = call.message.chat.id, 
                                            msg  = 'Пост с канала был удален успешно.',
                                            mark = self.KB['admin'])
            except aiogram.utils.exceptions.MessageCantBeDeleted:
                await self.callback_speaker(to = call.message.chat.id, 
                                            msg  = 'К сожалению, данный пост с канала не может быть удален.Скорее всего прошло больше 48 часов. Рекомендую удалить вручную',
                                            mark = self.KB['admin'])
                await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)


    def update_callback_handler(self):
        @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('upd'))
        async def del_handler(call: types.CallbackQuery):
            get_user = self.is_user_exists(call['from']['id'])
            act = ["название","описание","ссылку"]
            data = call.data.split('|')
            menu = InlineKeyboardButton('Выйти', callback_data='admin0')
            mark = InlineKeyboardMarkup().add(menu)
            course_id = int(data[2])
            print(data)
            if data[1].isdigit():
                code = int(data[1])
                self.set_action(code+5,call['from']['id'])
                self.add_to_queue_db(course_id)

                if code+5 in range(6,9):
                    if code == 3:
                        msg = f'Введи новую {act[code-1]}: '
                    else:
                        msg = f'Введи новое {act[code-1]}: '
                    await self.callback_speaker(msg = msg, mark=mark,
                                        to = call.message.chat.id)
                elif code+5 == 9:
                    await self.callback_speaker(msg = f'Загрузи новую картинку: ', mark=mark,
                                        to = call['from']['id'])
                
            else:
                
                # col = ['title','descriptionn','link']
                queue = self.select_from_queue()
                columns = [(self.upd_title_db , {'title':queue['title'], 'course_id': course_id}),
                            (self.desc_db , {'descriptionn':queue['descriptionn'], 'course_id': course_id}),
                            (self.link_db , {'link':queue['link'], 'course_id': course_id}),
                            (self.image_db , {'image':queue['image'], 'course_id': course_id})
                    ]
                

                for i in range(len(columns)):
                    if i == get_user['act']-6:
                        columns[i][0](columns[i][1])

                get_course = self.get_course(course_id)
                get = InlineKeyboardButton('Приобрести за 100 руб.', callback_data=f"course{course_id}")
                mark = InlineKeyboardMarkup().add(get)
                try:
                    if get_user['act'] not in [8,9]:
                        await self.bot.edit_message_caption(
                                chat_id=self.chanel_id,
                                message_id=get_course['msg_id'],
                                caption=f"{get_course['course_id']}. {get_course['title']}\n\n{get_course['descriptionn']}",
                                reply_markup=mark
                            )
                    elif get_user['act'] == 9:

                        file = InputMedia(media=InputFile(f"photos/{get_course['image']}"), caption=f"{get_course['course_id']}.{get_course['title']}\n\n{get_course['descriptionn']}")
                        await self.bot.edit_message_media(chat_id=self.chanel_id,
                                media = file,
                                message_id=get_course['msg_id'],
                                reply_markup=mark)


                    await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                    await self.callback_speaker(to = call.message.chat.id, 
                                                msg  = 'Пост был успешно обновлен.',
                                                mark = self.KB['admin'])
                except aiogram.utils.exceptions.MessageCantBeEdited: 
                    await self.callback_speaker(to = call.message.chat.id, 
                                                msg  = 'К сожалению, данный пост в канале не может быть обновлен, но он был обновлен в базе данных.Скорее всего прошло больше 48 часов. Рекомендую обновить вручную',
                                                mark = self.KB['admin'])
                    await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                except aiogram.utils.exceptions.MessageNotModified:
                    await call.answer('Вами не было внесено никаких изменений. Если вы действительно хотите изменить содержимое публикации, сравните новые данные с публикацией, дабы избежать дублирования.' ,show_alert = True)
                    await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
                    await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id-1)
                self.set_action(111,call['from']['id'])


    def admin_callback_handler(self):
        @self.dp.callback_query_handler(lambda c: c.data and c.data.startswith('admin'))
        async def main_handler(call: types.CallbackQuery):
            print(call)
            # print(call.data)
            code_length = len(call.data)
            code = int(call.data[-(code_length-5):])
            user_id = call['from']['id']
            get_user = self.is_user_exists(user_id)
            get_course = self.get_course(code)
            menu = InlineKeyboardButton('Меню', callback_data='admin0')
            mark = InlineKeyboardMarkup().add(menu)
            last_course = self.get_last_course()
            last_queue = self.select_from_queue()
            last_msg = self.get_last_msg()
            print('get_user',get_user)
            if get_user['act'] in range(3,6) and code!= 9:
                try :
                    os.remove(f"photos/{last_course['image']}")
                except:
                    pass
                self.del_idea_db(last_course['course_id'])
            if get_user['act'] in range(6,10):
                self.del_queue(last_queue['idqueue_to_update'])
                if last_queue['image'] != None:
                    if not self.is_image_exists(last_queue['image']):
                        os.remove(f"photos/{last_queue['image']}")
                print(last_queue)
            if get_user['act'] in [13,14]:
                self.delete_msgs_db()
                if last_msg['img'] != None:
                    if not self.is_image_exists(last_msg['img']):
                        os.remove(f"photos/{last_msg['img']}")
                print(last_queue)
            if code == 0:
                self.set_action(111,user_id)
                await self.callback_speaker(msg = 'Административное меню', mark=self.KB['admin'],
                                        to = user_id)
            
            elif code == 1:
                await self.callback_speaker(msg = 'Выберите дейтсвие для бизнес-идей:', mark=self.KB['courses_admin'],
                                        to = user_id)

            elif code == 2:
                self.set_action(11,user_id)
                await self.callback_speaker(msg = 'Напишите ваше сообщение для активных пользователей:', mark=mark,
                                        to = user_id)
                    
            elif code == 3:
                users = InlineKeyboardButton('Юзеры', callback_data='admin7')
                money = InlineKeyboardButton('Деньги', callback_data='admin8')
                mark.add(users,money)
                await self.callback_speaker(msg = 'Отчеты:', mark=mark,
                                            to = user_id)
            elif code == 4:
                self.set_action(2,user_id)
                await self.callback_speaker(msg = 'Понял. Начинаем добавление новой бизнес-идеи. Сначала запишем её <b><u>название</u></b> :', mark=mark,
                                            to = user_id)
            elif code == 5:
                self.set_action(12,user_id)
                await self.callback_speaker(msg = 'Понял. Начинаем обновление бизнес-идеи. Введи <b><u>порядковый номер</u></b> обновляемой бизнес-идеи:', mark=mark,
                                            to = user_id)
            elif code == 6:
                self.set_action(10,user_id)
                await self.callback_speaker(msg = 'Понял. Начинаем удаление, введи <b><u>порядковый номер</u></b> бизнес-идеи', mark=mark,
                                            to = user_id)
            elif code == 7:
                msg = self.list_of_msgs['response_users']
                response = self.db_response_users()
                for i in range(len(response)):
                    msg = msg.replace(f'c_{i}', f"{response[i]['count(1)']}")
                await self.callback_speaker(msg = msg, mark=mark,
                                            to = user_id)
            elif code == 8:
                msg = self.list_of_msgs['response_money']
                response = self.db_response_money()
                for i in range(len(response)):
                    msg = msg.replace(f's_{i}', f"{response[i]['sum']}")
                await self.callback_speaker(msg = msg, mark=mark,
                                            to = user_id)
            elif code == 9:
                await self.send_course()
                self.set_action(111,user_id)
                await self.callback_speaker(msg = 'Административное меню', mark=self.KB['admin'],
                                        to = user_id)
            await self.bot.delete_message(chat_id = call.message.chat.id , message_id = call.message.message_id)
            if code == 10:
                last_msg = self.get_last_msg()
                self.confirm_msgs(last_msg['id_sent_messages'])
                print(last_msg)
                await self.send_to_users({'user_id':user_id, 'msg' : last_msg, 'mark':self.KB['admin']})


    def pages(self):
        @self.dp.callback_query_handler(lambda c: c.data == 'get_more')
        async def nexthandler(message: types.CallbackQuery):
            try:
                # print(message.message.reply_markup.inline_keyboard)
                page = message.message.reply_markup.inline_keyboard[1][1].text.split()[-1]
            except Exception as e:
                print(message.message.reply_markup.inline_keyboard[1])
                page = message.message.reply_markup.inline_keyboard[1][0].text.split()[-1]
            print(page)
            await self.courses_list(message,int(page))
            await self.bot.delete_message(chat_id = message.message.chat.id , message_id = message.message.message_id)

        @self.dp.callback_query_handler(lambda c: c.data == 'get_prev')
        async def prevhandler(message: types.CallbackQuery):
            page = message.message.reply_markup.inline_keyboard[1][0].text.split()[-1]
            print(page)
            await self.courses_list(message,int(page))
            await self.bot.delete_message(chat_id = message.message.chat.id , message_id = message.message.message_id)

    


