# -*- coding: utf-8 -*-

import ParliamentOD as NSOD

# Обобщена информация за законопроектите
Bills = NSOD.deserializeData('Bills')[0]

def totalBills(Bills):
    'Общо внесени актове на НС'
    total = len(Bills)
    print 'Общо законопроекти:',total
    return total
    
def typeBills(Bills):
    'Актове на НС по видове'
    Types = {}
    for Signature in Bills.keys():    
        Type = Bills[Signature]['Type'] 
        try:  Types[Type] += 1
        except KeyError:
            Types[Type] = 0
            Types[Type] += 1           
    
    #for type in Types.keys():
    #    print type,Types[type]
    return Types

def statusBills(Bills):
    'Актове на НС по статус'
    Statuses = {}
    
    for Signature in Bills.keys():
        Status =    Bills[Signature]['Status']
        if 'Обнародван' in Status:            
            Status = 'Обнародван'
            
        try:  Statuses[Status] += 1
        except KeyError:
            Statuses[Status] = 0
            Statuses[Status] += 1           
    
    #for status in Statuses.keys():
    #    print status, Statuses[status]
    
    return Statuses
'''
оттеглен от вносителя(оттеглен) 9
Обнародван 275
приет(зала първо четене) 69
приет(приет в зала) 209
внесен(зала второ четене) 1
отхвърлен(зала първо четене) 42
приет(зала второ четене) 9
Внесен 72
'''


def statusesByType(Bills):
    'Статус на акта по тип'
    statusByType = {}      
       
    for Signature in Bills.keys():
        Type = Bills[Signature]['Type']
        Status = Bills[Signature]['Status']
        if 'Обнародван' in Status:            
            Status = 'Обнародван'
        try: statusByType[Type][Status]
        except KeyError:
            try: statusByType[Type][Status] = 0
            except KeyError:
                statusByType[Type] = {}
                statusByType[Type][Status] = 0
        statusByType[Type][Status] += 1                
    del(Type)
    
    Types = typeBills(Bills) 
    Statuses = statusBills(Bills)
                
    for Type in Types.keys():       
        for Status in Statuses.keys():            
            try: statusByType[Type][Status]
            except: statusByType[Type][Status] = 0
            print Type,Status,statusByType[Type][Status]
        print '---'
    
    return statusByType


#typeBills(Bills)
#statusBills(Bills)
statusesByType(Bills)
