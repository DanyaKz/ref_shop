from SimpleQIWI import *
from pyqiwip2p import QiwiP2P
import random 
from db import DataBase
import asyncio
import json

# from pyqiwip2p.types import QiwiCustomer, QiwiDatetime

class Qiwi_init(DataBase):
    def __init__(self):
        super().__init__()
        with open('config.json', encoding='utf-8') as mgs:
            self.config = json.load(mgs)
        self.public = self.config['qiwi']['public']
        self.private = self.config['qiwi']['private']
        self.simple_key = self.config['qiwi']['transaction']
        self.p2p = QiwiP2P(auth_key=self.private)
        self.phone = self.config['qiwi']['phone']
        self.simpli_api = QApi(token=self.simple_key, phone=self.phone)
        self.owner = 1299800437

    def create_payment(self, data):
        bill_id = f"{data['user_id']//1000}{data['course_id']}{random.randint(1000, 9999)}"
        new_bill = self.p2p.bill(bill_id = bill_id, amount=data['amount'], lifetime=60,comment = data['comment'])
        data['bill_id'] = new_bill.bill_id
        self.new_payment(data)
        return new_bill.pay_url

# print(new_bill.bill_id, new_bill.pay_url)
    # def is_payment_exists(self,user_id):

    def check_payment(self,user_id):
        bill_id = self.check_db_payment(user_id)
        print(bill_id , isinstance(bill_id,dict))
        if isinstance(bill_id,dict):
            check = self.p2p.check(bill_id=bill_id['inc_pay_id']).status
            print(check)
            # check = 'paid'
            if check == 'PAID':
                self.set_paid(bill_id['inc_pay_id'])
                self.set_coin_level(user_id)
                # if not self.is_user_exists(user_id)['registration']:
                #     self.set_reg_done(user_id)
                return True
            else :
                return False

        elif isinstance(bill_id,str):
            return bill_id
        else :
            return 'Данный платеж не существует. Попробуйте еще раз'

    def pay_parent(self, user_id, amount):
        get_parent = self.is_user_exists(user_id)
        try:
            comment = 'SIYP Bot'
            self.simpli_api.pay(account=f"+{get_parent['phone_number']}", amount=amount, comment=comment)
            self.new_out_pay(user_id = user_id, amount = amount, comment = comment)
            return True
        except:
            self.pay_parent_db(user_id=user_id, money=amount)
            return False
    
    async def daily_payment(self):
        users = self.users_to_daily_pay()
        for i in users:
            if i['user_id'] != self.owner:
                try:
                    comment = 'SIYP Bot'
                    self.simpli_api.pay(account=f"+{i['phone_number']}", amount=i['balance'], comment=comment)
                    self.new_out_pay(user_id = i['user_id'], amount = i['balance'], comment = comment)
                    await self.bot.send_message(i['user_id'],f"Доброе утро! Твой счет был пополнен на сумму в размере {i['balance']} руб.")
                except:
                    await self.bot.send_message(i['user_id'],
                    "К сожалению, деньги не получилось отправить, но они были сохранены и следующим утром бот попробует отправить их снова, а пока проверь правильность своего номера, который находится в «меню» - «мои данные», либо же проверь лимиты своего кошелька")


# asyncio.run(transfer_money_to_another_wallet(qiwi_token="497cc7528d8c5cde3a67323e74f7a267", phone_number="+77775255778"))

# async def transfer_money_to_another_wallet(qiwi_token: str, phone_number: str) -> None:
#     async with QiwiWallet(api_access_token=qiwi_token, phone_number=phone_number) as wallet:
#         await wallet.transfer_money(to_phone_number="+79616680208", amount=10)


# asyncio.run(transfer_money_to_another_wallet(qiwi_token="e652112ff0b45590ff800e10f9ab19f1", phone_number="+77775255778"))

# async def create_p2p_bill():
#     async with QiwiP2PClient(secret_p2p="e652112ff0b45590ff800e10f9ab19f1") as p2p:
#         bill = await p2p.create_p2p_bill(amount=10)
#         print(f"Link to pay bill with {bill.id} id = {bill.pay_url}")

# asyncio.run(create_p2p_bill())

# async def print_balance(qiwi_token: str, phone_number: str) -> None:
#     """
#     This function allows you to get balance of your wallet using glQiwiApi library
#     """
#     async with QiwiWallet(api_access_token=qiwi_token, phone_number=phone_number) as w:
#         try:
#             balance = await w.get_balance()
#         # handle exception if wrong credentials or really API return error
#         except QiwiAPIError as err:
#             print(err.json())
#             raise
#     print(f"Your current balance is {balance.amount} {balance.currency.name}")


# asyncio.run(print_balance(qiwi_token="e652112ff0b45590ff800e10f9ab19f1", phone_number="+77775255778"))