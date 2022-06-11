-- children lvl - count 
select t.lvl - sub.lvl 'floor' , count(t.lvl) 'c'
from tree t
join users u
	on t.user_id = u.user_id
join (select  lft,rgt,lvl from tree where user_id = '{int(user_id)}' ) sub
	on (sub.lft < t.lft and sub.rgt > t.rgt) 
where cast(t.lvl as signed) - cast(sub.lvl as signed) <= (select lvl from users where user_id ='{int(user_id)}') 
and u.lvl > 0
group by t.lvl
order by t.lvl;
-- find children
select t.id, t.user_id, t.parent_id , u.first_name, t.lft , t.rgt , t.lvl - sub.lvl 'floor',u.lvl
from tree t
join users u   
	on t.user_id = u.user_id
join (select lft,rgt,lvl from tree where user_id = '{int(user_id)}' ) sub
	on (sub.lft < t.lft and sub.rgt > t.rgt) 
where (t.lvl - sub.lvl) <= (select lvl from users where user_id = '{int(user_id)}') 
and (t.lvl - sub.lvl) = 1
order by t.id;
-- find parents
select t.user_id, t.parent_id , t.lft , t.rgt , t.lvl
from tree t , 
	(select * from tree where user_id = '{int(user_id)}') sub 
where sub.lft > t.lft and sub.rgt < t.rgt ;
-- second option
select t.id, t.user_id, u.first_name, t.parent_id , t.lft , t.rgt , t.lvl
from tree t 
join users u   
	on t.user_id = u.user_id
join (select * from tree where user_id = '{int(user_id)}' ) sub
	on sub.lft > t.lft and sub.rgt < t.rgt
order by t.id;