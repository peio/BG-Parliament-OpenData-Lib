# -*- coding: utf-8 -*-

# Питания по депутат
select FullName, PoliticalForce, count(*) as NumQ from `Parliament`.`Questions`, `Parliament`.`MP` where Questions.MPID=MP.ID group by FullName order by NumQ desc;

# Питания по Партия
select PoliticalForce, count(*) as NumQ from `Parliament`.`Questions`, `Parliament`.`MP` where Questions.MPID=MP.ID group by PoliticalForce order by NumQ desc;

#Законопроекти по депутат
SELECT FullName, PoliticalForce, count(*) as NumBills FROM Parliament.MP2Signature, Parliament.MP where MP2Signature.MPID=MP.ID group by FullName order by NumBills desc;

#Законопроекти по партия
SELECT PoliticalForce, count(*) as NumBills FROM Parliament.MP2Signature, Parliament.MP where MP2Signature.MPID=MP.ID group by PoliticalForce order by NumBills desc;

