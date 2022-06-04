import pymysql
import sys
from datetime import datetime
import json

class DataBase():
    def __init__(self):

        with open('config.json', encoding='utf-8') as mgs:
            self.config = json.load(mgs)

        self.config_db = self.config['database']
        self.conn =  pymysql.connect(
                            host=self.config_db['host'],
                            user=self.config_db['user'],
                            password=self.config_db['passwd'],
                            database=self.config_db['db'],
                            port = self.config_db['port'],
                            charset='utf8mb4',
                            use_unicode=True,
                            cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.conn.cursor()
        print('Connected')

    def change_quotes(self,data):
        new_data = data.replace('"','\"')
        return new_data

    def is_user_exists(self,data):
        self.cur.execute(f'select * from users where user_id = {int(data)};')
        isExist = self.cur.fetchone()
        if bool(isExist):
            return isExist
        else:
            return False 
    
    def get_parents(self,user_id):
        print(user_id)
        to_return = {}
        my_execute = f"""
            select t.id, t.user_id, u.first_name, t.parent_id , t.lft , t.rgt , t.lvl
            from tree t 
            join users u   
                on t.user_id = u.user_id
            join (select * from tree where user_id = {int(user_id)} ) sub
                on sub.lft > t.lft and sub.rgt < t.rgt
            order by t.id;
        """
        self.cur.execute(my_execute)
        to_return['all_parents'] = self.cur.fetchall()
        #над этим подумать
        to_return['user_lvl'] = self.get_coin_lvl(int(user_id))['lvl']
        # if user_lvl == None :
        #     to_return['user_lvl'] = 0
        # else:
        #     to_return['user_lvl'] = user_lvl['lvl']
        #     print(to_return['user_lvl'])
        return to_return
    
    def new_payment(self,data):
        my_execute = f"""
            INSERT INTO `incoming_payments` (`inc_pay_id`, `user_id`, `value_of_payment`, `cooment`) 
                VALUES ('{data['bill_id']}', '{data['user_id']}', '{data['amount']}', "{self.change_quotes(data['comment'])}");
        """
        self.cur.execute(my_execute)
        self.conn.commit()
    
    def reject_payment(self,data):
        my_execute = f"""
            update incoming_payments set is_it_end = 1 , is_it_success = 0 where inc_pay_id = {data} ;
        """
        self.cur.execute(my_execute)
        self.conn.commit()

    def check_db_payment(self,data):
        my_execute = f"""
            select * from incoming_payments where user_id = {data} and is_it_end = 0 and is_it_success = 0;
        """
        self.cur.execute(my_execute)
        check = self.cur.fetchone()
        if bool(check):
            if (datetime.now() - check['time_of_payment']).total_seconds() > 3600:#
                self.reject_payment(check['inc_pay_id'])
                return 'Платеж был просрочен. Попробуйте еще раз'
            else:
                return check
        else : 
            False
    
    def get_last_payment(self, user_id):
        my_execute = f"""
            select * from incoming_payments where user_id = {user_id} and is_it_end = 1 and is_it_success = 1 
            order by time_of_payment desc limit 1;
        """
        self.cur.execute(my_execute)
        check = self.cur.fetchone()
        return check

    def set_paid(self,data):
        my_execute = f"""
            update incoming_payments set is_it_end = 1 , is_it_success = 1 where inc_pay_id = {data} ;
        """
        self.cur.execute(my_execute)
        self.conn.commit()

    def add_to_cart(self,data):
            my_execute = f"""
                INSERT INTO `shopping_cart` (`buyer`, `course_id`) VALUES ('{data['user_id']}', '{data['course_id']}');
            """
            self.cur.execute(my_execute)
            self.conn.commit()

    def does_user_have_course(self,data):
            self.cur.execute(f"select * from shopping_cart where buyer = {data['user_id']} and course_id = {data['course_id']};")
            return self.cur.fetchone()

    def select_from_courses(self,data):
        self.cur.execute(f"select * from courses where course_id = '{data}';")
        return self.cur.fetchone()

    def get_coin_lvl(self,user_id):
        self.cur.execute(f"select u.lvl from users u where u.user_id = {user_id};")
        return self.cur.fetchone()
    
    def pay_parent_db(self, user_id, money):
        self.cur.execute(f"update users set balance = balance + {money} where user_id = {user_id};")
        self.conn.commit()
    
    def get_user_s_id(self,user_id):
        if user_id == 'null':
            return {'id':'null'}
        else:
            self.cur.execute(f"select id from tree where user_id = {int(user_id)};")
            return self.cur.fetchone()

    def add_user(self,data):
        # my_execute = f"""
        # insert into users(user_id,parent) value({data['user_id']},{data['parent']});
        # insert into tree(user_id,parent_id) value({data['user_id']},{data['parent']});
        # select tree();
        # """
        # self.cur.execute(my_execute)
        self.cur.execute(f"""insert into users(user_id,first_name,username,parent) value({data['user_id']},"{self.change_quotes(data['first_name'])}","{data['username']}",{data['parent']});""")
        self.cur.execute(f"insert into tree(user_id,parent_id) value({data['user_id']},{data['parent_for_tree']});")
        self.cur.execute(f"call tree();")
        self.conn.commit()
    
    def set_coin_level(self,user_id):
        self.cur.execute(f"update users set lvl = lvl + 1 where user_id = {user_id}; ")
        self.conn.commit()

    def get_user_act(self,user_id):
        self.cur.execute(f"select act from users where user_id = {user_id};")
        return self.cur.fetchone()

    def set_action(self,act,user_id):
        print('start',act,user_id)
        self.cur.execute(f"update users set act = {act} where user_id = {user_id} ;")
        self.conn.commit()
        print('done')
    
    def set_number(self,number,user_id):
        self.cur.execute(f"update users set phone_number = {number} where user_id = {user_id} ;")
        self.conn.commit()
    
    def set_reg_done(self, user_id):
        self.cur.execute(f"update users set registration = 1 where user_id = {user_id};")
        self.conn.commit()
    
    def is_number_exists(self,data):
        self.cur.execute(f'select * from users where phone_number = {int(data)};')
        isExist = self.cur.fetchone()
        if bool(isExist):
            return True
        else:
            return False 
    
    def get_users_courses(self,page,user_id):
        limit = 1
        offset = (page - 1)*limit
        self.cur.execute(f'select * from shopping_cart where buyer = {user_id} limit {limit} offset {offset}; ')
        return self.cur.fetchall()
    
    def get_len(self,user_id):
        self.cur.execute(f'select count(1) from shopping_cart where buyer = {user_id};')
        return self.cur.fetchone()
    
    def get_last_course(self):
        self.cur.execute(f'select * from courses order by course_id desc;')
        return self.cur.fetchone()
    
    def set_msg_id_to_course(self,msg_id):
        self.cur.execute(f'update courses set msg_id = {msg_id};')
        self.con.commit()
    
    def get_course(self,course_id):
        self.cur.execute(f'select * from courses where course_id = {course_id};')
        isExist = self.cur.fetchone()
        if bool(isExist):
            return isExist
        else:
            return False
    
    def children_lvl_count(self,user_id):
        my_execute = f"""select t.lvl - sub.lvl 'floor', count('floor') 'c'
            from tree t
            join users u   
                on t.user_id = u.user_id
            join (select * from tree where user_id = '{int(user_id)}' ) sub
                on (sub.lft < t.lft and sub.rgt > t.rgt) 
            where (t.lvl - sub.lvl) <= (select lvl from users where user_id = '{int(user_id)}') 
            and u.lvl > 0
            group by 'floor'
            order by 'floor';
            """
        self.cur.execute(my_execute)
        return self.cur.fetchall()

    def children_plus_lvl_count(self,user_id):
        my_execute = f"""select t.lvl - sub.lvl 'floor', count('floor') 'c'
            from tree t
            join users u   
                on t.user_id = u.user_id
            join (select * from tree where user_id = '{int(user_id)}' ) sub
                on (sub.lft < t.lft and sub.rgt > t.rgt) 
            where (t.lvl - sub.lvl) = (select lvl from users where user_id = '{int(user_id)}') + 1 ;
            """
        self.cur.execute(my_execute)
        return self.cur.fetchone()

    def children_1_lvl(self, user_id):
        my_execute = f"""select count('floor') 'c'
            from tree t
            join users u   
                on t.user_id = u.user_id
            join (select * from tree where user_id = '{int(user_id)}' ) sub
                on (sub.lft < t.lft and sub.rgt > t.rgt) 
            where (t.lvl - sub.lvl) = 1 and u.lvl > 0;"""
        self.cur.execute(my_execute)
        return self.cur.fetchone()

    def my_salary_db(self, user_id):
        self.cur.execute(f"select my_salary({int(user_id)}) 'value';")
        return self.cur.fetchone()

    def get_active_users(self):
        self.cur.execute(f'select * from users where lvl > 1;')
        return self.cur.fetchall()

    def get_last_msg(self):
        self.cur.execute(f"select * from sent_messages order by id_sent_messages desc;")
        return self.cur.fetchone()
    def add_msgs(self,data):
        self.cur.execute(f"INSERT INTO `sent_messages` (`msg_text`) VALUES ('{self.change_quotes(data)}'); ")
        self.conn.commit()
    def confirm_msgs(self,data):
        self.cur.execute(f"update sent_messages set confirm = 1 where id_sent_messages = {data}; ")
        self.conn.commit()
    def msg_sent(self,data):
        self.cur.execute(f"update sent_messages set was_it_sent = 1 where id_sent_messages = {data}; ")
        self.conn.commit()
# 36

    def db_response_users(self):
        my_execute = """
        select count(1) from users where lvl > 0
        union all
        select count(1) from users where lvl > 0 and when_joined = date_format(date_sub(now(), interval 1 day), '%y-%m-%d');"""
        self.cur.execute(my_execute)
        return self.cur.fetchall()

    def db_response_money(self):
        my_execute = """select ifnull(sum(value_of_payment),0) 'sum' from incoming_payments
            union all
            select ifnull(sum(value_of_payment),0) from incoming_payments 
                where date_format(time_of_payment, '%y-%m-%d') = date_format(date_sub(now(), interval 1 day), '%y-%m-%d')
            union all
            select ifnull(sum(balance),0) from users;
            """
        self.cur.execute(my_execute)
        return self.cur.fetchall()
    

    def upd_title_db(self,data):
        print(f"""update courses set title = "{self.change_quotes(data['title'])}" where course_id = {data['course_id']}; """)
        self.cur.execute(f"""update courses set title = "{self.change_quotes(data['title'])}" where course_id = {data['course_id']}; """)
        self.conn.commit()
    def title_db(self,data):
        self.cur.execute(f'INSERT INTO `courses` (`title`) VALUES ("{self.change_quotes(data)}"); ')
        self.conn.commit()
    def desc_db(self,data):
        self.cur.execute(f"""update courses set descriptionn = "{data['descriptionn']}" where course_id = {data['course_id']}; """)
        self.conn.commit()
    def link_db(self,data):
        self.cur.execute(f"""update courses set link = "{self.change_quotes(data['link'])}" where course_id = {data['course_id']}; """)
        self.conn.commit()
    def image_db(self,data):
        self.cur.execute(f"update courses set image = '{data['image']}' where course_id = {data['course_id']}; ")
        self.conn.commit()
    def msg_db(self,course_id,msg_id):
        print(course_id)
        self.cur.execute(f"update courses set msg_id = {msg_id} where course_id = {course_id}; ")
        self.conn.commit()

    def add_to_queue_db(self,data):
        print(data)
        self.cur.execute(f"INSERT INTO `queue_to_update` (`course_id`) VALUES ({data});")
        self.conn.commit()

    def del_idea_db(self,data):
        self.cur.execute(f"delete from courses where course_id = {data}")
        self.conn.commit()
    
    def del_queue(self,data):
        self.cur.execute(f"delete from queue_to_update where idqueue_to_update = {data}")
        self.conn.commit()
    # def update_last_queue(self,data):
    #     my_execute = f"""
    #         update queue_to_update set upd_value = {self.change_quotes(data)} 
    #         where idqueue_to_update =(select idqueue_to_update from queue_to_update 
    #         order by idqueue_to_update desc limit 1);
    #     """
    #     self.cur.execute(my_execute)
    #     self.conn.commit()
    def is_image_exists(self,data):
        my_execute = f"""select * from courses where image = {data}"""
        isExist = self.cur.fetchone()
        if bool(isExist):
            return True
        else:
            return False

    def select_from_queue(self):
        my_execute = f"""select * from queue_to_update 
            order by idqueue_to_update desc limit 1"""
        self.cur.execute(my_execute)
        return self.cur.fetchone()
    
    def get_act_name(self,data):
        print(data)
        my_execute = f"""select act_name
                        from actions 
                        where act_id = {data};"""
        self.cur.execute(my_execute)
        return self.cur.fetchone()
    
    def update_last_queue(self,data):
        my_execute = f"""
            update queue_to_update set {data['col']} = "{self.change_quotes(data['data'])}"
            where idqueue_to_update = (select sub.idqueue_to_update from (select * from queue_to_update)sub 
            order by idqueue_to_update desc limit 1);
        """
        self.cur.execute(my_execute)
        self.conn.commit()
    
    def users_over_lower_1_lvl(self,lvl):
        my_execute = f"""select *
                        from users where lvl {lvl} 1"""
        self.cur.execute(my_execute)
        return self.cur.fetchall()

    def users_response_db(self,data):
        self.cur.execute(f"call daily_users('{data}');")
        self.conn.commit()
        my_execute = f"""
                        select * from daily_response
                        where user_id = '{data}' 
                        order by id_daily desc
                        limit 1;"""
        self.cur.execute(my_execute)
        return self.cur.fetchone()
    
    def admin_response_db(self):
        self.cur.execute("call daily_admin();")
        self.conn.commit()
        my_execute = f"""
                        select * from admin_response order by id_admin desc limit 1;"""
        self.cur.execute(my_execute)
        return self.cur.fetchone()
    
    def get_data_children_1_lvl(self, user_id):
        my_execute = f"""
            select u.user_id, u.first_name
            from tree t
            join users u   
                on t.user_id = u.user_id
            join (select * from tree where user_id = '{int(user_id)}' ) sub
                on (sub.lft < t.lft and sub.rgt > t.rgt) 
            where (t.lvl - sub.lvl) = 1 and u.lvl > 0;"""
        self.cur.execute(my_execute)
        return self.cur.fetchall()
    
    def new_out_pay(self,**data):
        my_execute = f"""
            INSERT INTO `outcomming_payments` (`user_id`, `value_of_payment`, `cooment`, `is_it_end`, `is_it_success` ) 
                VALUES ('{data['user_id']}', '{data['amount']}', '{data['comment']}', '1', '1');"""
        self.cur.execute(my_execute)
        self.conn.commit()

    def users_to_daily_pay(self):
        self.cur.execute("select * from users where balance > 0;")
        return self.cur.fetchall()

# db = DataBase()
# print(db.my_salary_db(1032707306))
