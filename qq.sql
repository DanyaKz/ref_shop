create database siyp;
use siyp;

SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

CREATE TABLE `actions` (
  `act_id` int NOT NULL,
  `act_name` varchar(100) DEFAULT NULL
) ;
ALTER TABLE `actions`
  ADD PRIMARY KEY (`act_id`);


INSERT INTO `actions` (`act_id`, `act_name`) VALUES
(1, 'phone_num'),
(2, 'add_title'),
(3, 'add_decs'),
(4, 'add_link'),
(5, 'add_pic'),
(6, 'upd_title'),
(7, 'upd_desc'),
(8, 'upd_link'),
(9, 'upd_picture'),
(10, 'del'),
(11, 'send_message'),
(12, 'find'),
(13,'send_message_pic'),
(14, 'send_message_btn'),
(111, 'free');

CREATE TABLE `admin_response` (
  `id_admin` int NOT NULL AUTO_INCREMENT,
  `yes_users` int DEFAULT NULL,
  `all_users` int DEFAULT NULL,
  `yes_earn` int DEFAULT NULL,
  `all_earn` int DEFAULT NULL,
  `resp_date` date DEFAULT ((date_format(date_sub(now(), interval 1 day), '%y-%m-%d'))),
  PRIMARY KEY (`id_admin`)
) ;

CREATE TABLE `courses` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `title` text,
  `descriptionn` text,
  `link` text,
  `image` text,
  `msg_id` int DEFAULT NULL,
  PRIMARY KEY (`course_id`)
) ;

CREATE TABLE `sent_messages` (
  `id_sent_messages` int NOT NULL AUTO_INCREMENT,
  `msg_text` text,
  `datetime_of_msg` datetime DEFAULT CURRENT_TIMESTAMP,
  `confirm` tinyint DEFAULT '0',
  `was_it_sent` tinyint DEFAULT '0',
  PRIMARY KEY (`id_sent_messages`)
) ;
ALTER TABLE `sent_messages` 
ADD COLUMN `img` TEXT NULL AFTER `msg_text`,
ADD COLUMN `btn_title` TEXT NULL AFTER `img`,
ADD COLUMN `btn_link` TEXT NULL AFTER `btn_title`;


CREATE TABLE `queue_to_update` (
  `idqueue_to_update` int NOT NULL AUTO_INCREMENT,
  `course_id` int DEFAULT NULL,
  `title` text,
  `descriptionn` text,
  `link` text,
  `image` text,
  PRIMARY KEY (`idqueue_to_update`),
  FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE
) ;

CREATE TABLE `users` (
  `user_id` bigint NOT NULL UNIQUE,
  `first_name` varchar(250) DEFAULT NULL,
  `username` varchar(250) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `act` int DEFAULT '111',
  `parent` bigint DEFAULT NULL,
  `lvl` int DEFAULT '0',
  `balance` int DEFAULT '0',
  `personal_link` text,
  `when_joined` date DEFAULT NULL,
  `registration` tinyint DEFAULT '0',
  PRIMARY KEY (`user_id`),
  FOREIGN KEY (`act`) REFERENCES `actions` (`act_id`) ON DELETE SET NULL
);


delimiter $$
create trigger personal_link
before insert on users
for each row
begin 
	set new.personal_link =  concat('https://t.me/siyp_bot?start=', convert(new.user_id,char)) ;
end $$ delimiter; 

DELIMITER $$
CREATE TRIGGER `when_1_lvl` BEFORE UPDATE ON `users` FOR EACH ROW begin
	if new.lvl = 1
		then
			set new.when_joined = now();
	end if;
end $$ DELIMITER ;

CREATE TABLE `tree` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint DEFAULT NULL,
  `parent_id` bigint DEFAULT NULL,
  `lft` int UNSIGNED DEFAULT NULL,
  `rgt` int UNSIGNED DEFAULT NULL,
  `lvl` int UNSIGNED DEFAULT '0',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ;

delimiter $$
create trigger lvl
before insert on tree
for each row
begin 
	if new.parent_id is null then
		set new.lvl = 1 ; 
	end if;
    if new.parent_id is not null then
		set @i := (select lvl from tree t where t.id = new.parent_id );
		set new.lvl = @i + 1 ; 
	end if;
end $$ delimiter ;


CREATE TABLE `incoming_payments` (
  `inc_pay_id` bigint UNSIGNED NOT NULL UNIQUE,
  `user_id` bigint DEFAULT NULL,
  `value_of_payment` int DEFAULT NULL,
  `cooment` text,
  `is_it_end` tinyint(1) DEFAULT '0',
  `is_it_success` tinyint(1) DEFAULT '0',
  `time_of_payment` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`inc_pay_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ;

CREATE TABLE `daily_response` (
  `id_daily` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `user_lvl` int NOT NULL,
  `children_first_lvl` int NOT NULL,
  `all_children` int NOT NULL,
  `new_first_lvl` int NOT NULL,
  `earned_yesterday` int NOT NULL,
  `erned_all` int NOT NULL,
  `balance` int NOT NULL,
  `children_nex_lvl` int NOT NULL,
  `daily_date` date DEFAULT (date_format(date_sub(now(), interval 1 day), '%y-%m-%d')),
  PRIMARY KEY (`id_daily`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ;

CREATE TABLE `outcomming_payments` (
  `out_com_id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` bigint DEFAULT NULL,
  `value_of_payment` int DEFAULT NULL,
  `is_it_end` tinyint(1) DEFAULT NULL,
  `is_it_success` tinyint(1) DEFAULT NULL,
  `cooment` text,
  `time_of_act` datetime DEFAULT (now()),
  PRIMARY KEY (`out_com_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
);

CREATE TABLE `shopping_cart` (
  `shop_id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,
  `buyer` bigint DEFAULT NULL,
  `course_id` int NOT NULL,
  PRIMARY KEY (`shop_id`),
  FOREIGN KEY (`buyer`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) 
);


DELIMITER $$
CREATE procedure tree () 
BEGIN 
    UPDATE tree t SET lft = NULL, rgt = NULL;
    
    SET @i := 0;
    UPDATE tree t SET lft = (@i := @i + 1), rgt = (@i := @i + 1)
    WHERE t.parent_id IS NULL;

    forever: LOOP
        SET @parent_id := NULL;
        SELECT t.id, t.rgt FROM tree t, tree tc
        WHERE t.id = tc.parent_id AND tc.lft IS NULL AND t.rgt IS NOT NULL
        ORDER BY t.rgt LIMIT 1 INTO @parent_id, @parent_right;

        IF @parent_id IS NULL THEN LEAVE forever; END IF;

        SET @current_left := @parent_right;

        SELECT @current_left + COUNT(*) * 2 FROM tree
        WHERE parent_id = @parent_id INTO @parent_right;

        SET @current_length := @parent_right - @current_left;

        UPDATE tree t SET rgt = rgt + @current_length
        WHERE rgt >= @current_left ORDER BY rgt;

        UPDATE tree t SET lft = lft + @current_length
        WHERE lft > @current_left ORDER BY lft;

        SET @i := (@current_left - 1);
        UPDATE tree t SET lft = (@i := @i + 1), rgt = (@i := @i + 1)
        WHERE parent_id = @parent_id ORDER BY id;
    END LOOP;
END $$ DELIMITER ;

DELIMITER $$
CREATE function my_salary (u_id bigint) 
RETURNS INT DETERMINISTIC MODIFIES SQL DATA
DETERMINISTIC
BEGIN 
	set @val = (select sum(value_of_payment) from outcomming_payments o
	where o.user_id = u_id and 
	is_it_end = 1 and
	is_it_success = 1);
	if @val is null then
		return (0);
    end if;
	return (@val);
END $$ DELIMITER ;



delimiter $$
CREATE procedure daily_users (us_id bigint) 
BEGIN 
	set @us_id = us_id;
     set @u_lvl = (select lvl from users where user_id = @us_id);
     set @children_first_lvl = (select count(1)
            from tree t
            join users u   
                on t.user_id = u.user_id
            join (select lft,rgt,lvl from tree where user_id = @us_id) sub
                on (sub.lft < t.lft and sub.rgt > t.rgt) 
            where cast(t.lvl as signed) - cast(sub.lvl as signed) = 1 and u.lvl > 0);
	set @all_children = (select count(1)
			from tree t
			join users u   
				on t.user_id = u.user_id
			join (select lft,rgt,lvl from tree where user_id = @us_id ) sub
				on (sub.lft < t.lft and sub.rgt > t.rgt) 
                where cast(t.lvl as signed) - cast(sub.lvl as signed) <= (select lvl from users where user_id = @us_id) 
            and u.lvl > 0);
	set @new_first_lvl = (select count(1)
			from tree t
			join users u   
				on t.user_id = u.user_id
			join (select lft,rgt,lvl from tree where user_id = @us_id ) sub
				on (sub.lft < t.lft and sub.rgt > t.rgt) 
                where u.when_joined = date_format(date_sub(now(), interval 1 day), '%y-%m-%d' ));
	set @earned_yesterday = (select ifnull(sum(value_of_payment),0) from outcomming_payments 
                where date_format(time_of_act, '%y-%m-%d') = date_format(date_sub(now(), interval 1 day), '%y-%m-%d') 
                and user_id = @us_id
                and (is_it_end = 1 and is_it_success = 1));
	set @erned_all = (select ifnull(sum(value_of_payment),0) from outcomming_payments 
                where user_id = @us_id 
                and (is_it_end = 1 and is_it_success = 1));
	set @balance = (select balance from users where user_id = @us_id );
    set @children_nex_lvl = (select count(1)
            from tree t
            join users u   
                on t.user_id = u.user_id
            join (select lft,rgt,lvl from tree where user_id = @us_id  ) sub
                on (sub.lft < t.lft and sub.rgt > t.rgt) 
            where cast(t.lvl as signed) - cast(sub.lvl as signed) = (select lvl from users where user_id = @us_id ) + 1 );
            
	 insert into daily_response(user_id, user_lvl, children_first_lvl, all_children, new_first_lvl, earned_yesterday, erned_all, balance, children_nex_lvl)
 						value (@us_id , @u_lvl, @children_first_lvl, @all_children, @new_first_lvl, @earned_yesterday, @erned_all, @balance, @children_nex_lvl);
end $$ delimiter ;


delimiter $$
CREATE procedure daily_admin () 
BEGIN 
     set @yes_users = (select count(1) from users 
		where when_joined = ((date_format(date_sub(now(), interval 1 day), '%y-%m-%d')))
		and lvl > 0);
     set @all_users = (select count(1) from users 
		where lvl > 0);
	set @yes_earned = (select ifnull(sum(value_of_payment),0) 
		from incoming_payments 
		where date_format(time_of_payment, '%y-%m-%d') = ((date_format(date_sub(now(), interval 1 day), '%y-%m-%d')))
        and (is_it_end = 1 and is_it_success = 1));
	set @all_earned = (select ifnull(sum(value_of_payment),0)
			from incoming_payments
            where is_it_end = 1 and is_it_success = 1 );
	insert into admin_response(yes_users, all_users, yes_earn, all_earn)
    values (@yes_users , @all_users , @yes_earned , @all_earned);
end$$ delimiter ;

INSERT INTO `courses` (`title`, `descriptionn`, `link`, `image`) VALUES 
	('Автоворонка продаж', 
	'Как настроить автоворонку без продаж?
 Как на пассиве увеличивать свой доход?
 Ты получишь доступ к каналу с подробным описанием заработка.
 - Пошаговая инструкция.
 - Материалы для работы.', 
 'https://t.me/+q6shxvXPtZZiNjli',
 '1.png');
 
INSERT INTO `users` (`user_id`, `first_name`, `username`, `phone_number`, `act`, `parent`, `lvl`, `balance`, `personal_link`, `when_joined`, `registration`) VALUES ('1299800437', 'Dante', 'dante_999', NULL, '111', NULL, '1', '0', 'https://t.me/siyp_bot', '2022-06-07', '1')