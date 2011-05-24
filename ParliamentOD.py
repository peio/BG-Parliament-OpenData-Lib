# -*- coding: utf-8 -*-
'Библиотека за работа с отворените данни от Народно събрание'

''' Copyright (C) 2011 Peio Popov <peio@peio.org>
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from xml.dom import minidom
from hashlib import sha1
import re, pickle, os, urllib, time, glob, MySQLdb

DATA_DIR = '../data/'
MP_DATA_DIR = DATA_DIR+'/mp/'
BILLS_DATA_DIR = DATA_DIR+'/bills/'

# Начало на 41 НС
NS41_Start = ( 2009, 6, 25, 0, 0, 0, 0, 0, 0)
NS41_Start = time.mktime(NS41_Start)

'MAIN FUNCTIONS'
def getAllMP():
    'Информация за Народните представители от 41 НС'
    
    url = 'http://parliament.yurukov.net/data/mp_list.xml'
    getData(url)
    
    'Списък на всички Народни представители от 41то НС'  
    
    # Parse xml data
    xmldoc = minidom.parse(DATA_DIR+'mp_list.xml')
    profiles = xmldoc.getElementsByTagName('Profile')       
    
    # Start MySQL
    conn = MySQLdb.connect('localhost', 'peio', 'opendata', 'Parliament', charset='utf8');
    cursor = conn.cursor()    
    cursor.execute('TRUNCATE table MP');
            
    for profile in profiles:        
        ID = int(profile.attributes['id'].value)
        FullName = profile.getElementsByTagName('FullName')[0].firstChild.data
        PoliticalForce = simplePoliticalForce( profile.getElementsByTagName('PoliticalForce')[0].firstChild.data )
        BirthDate = simplePoliticalForce( profile.getElementsByTagName('DateOfBirth')[0].firstChild.data )
        
        
        PlaceOfBirth = profile.getElementsByTagName('PlaceOfBirth')[0].firstChild.data
        MIR, Region = MPConstituency ( profile.getElementsByTagName('Constituency')[0].firstChild.data )
        DataUrl = profile.getElementsByTagName('DataUrl')[0].firstChild.data      
                
        cursor.execute("""INSERT INTO MP (ID, FullName, PoliticalForce, BirthDate, PlaceOfBirth, MIR, Region, DataUrl ) 
        values(%s,%s,%s,STR_TO_DATE(%s,'%%d/%%m/%%Y'),%s,%s,%s,%s)""",(ID, FullName, PoliticalForce, BirthDate, PlaceOfBirth, MIR, Region, DataUrl))
        
        getMP(ID) 

    # Close MySQL
    cursor.close()
    conn.close()       
      
    return True 

def getMP(ID):
    'Индивидуална (допълнителна) информация за народен представител'  
         
    # По ID може да извлечем пълната индивидуална информация      
    url = 'http://parliament.yurukov.net/data/mp/mp_'+str(ID)+'.xml'
    getData(url, MP_DATA_DIR)    

    xmldoc = minidom.parse(MP_DATA_DIR+'mp_'+str(ID)+'.xml' )
    
    # Start MySQL
    conn = MySQLdb.connect('localhost', 'peio', 'opendata', 'Parliament', charset='utf8');
    cursor = conn.cursor()    
              
    'Информация за внесените законопроекти'
    bills = xmldoc.getElementsByTagName('Bill')
    Bills = []              
    for bill in bills:    
        'Ще ползваме сигнатурата като идентификатор'
        try: Signature = bill.getElementsByTagName('Signature')[0].firstChild.data
        except: 
            print 'Bill Signature Problem'
            Signature = '000-00-000'
            pass
        

        #print 'Внася',ID, Signature
        try: cursor.execute('INSERT INTO MP2Signature (MPID, Signature) VALUES(%s, %s)',(ID,Signature))
        except: 
            #print ID, Signature,'exists'
            pass
                    
        Bills.append(Signature)          
    
    'Информация за актуалните въпроси и питания'
    questions = xmldoc.getElementsByTagName('Question')
    Questions = []
    for question in questions:
        try: About = question.getElementsByTagName('About')[0].firstChild.data
        except:
            print 'Problem with Question About'
            About = 'Problem with Question About'
            pass

        try: To = question.getElementsByTagName('To')[0].firstChild.data
        except:
            print 'Problem with Question To'
            To = 'Problem with Question To'
            pass
        
        try: Date = question.getElementsByTagName('Date')[0].firstChild.data
        except:
            print 'Problem with Question Date'
            Date = 'Problem with Question Date'
            pass
        
        #About = 'momo'
        QuestionSHA1 = sha1(str(ID)+To+Date+About).hexdigest()
        try: cursor.execute("INSERT INTO Questions (MPID, ToWhom, Date, About, QuestionSHA1 ) VALUES(%s, %s,STR_TO_DATE(%s,'%%d/%%m/%%Y'), %s, %s)",(int(ID), To, Date, About, QuestionSHA1))
        except:                     
            pass
        
        Questions.append( (Date, To, About) )                       
    
    # Close MySQL
    cursor.close()
    conn.close() 
    
    return Bills, Questions        

def getAllBills():
    'Списък на законопроектите на 41 НС'
    
    url = 'http://parliament.yurukov.net/data/bills_list_all.xml'
    getData(url)
      
    xmldoc = minidom.parse(DATA_DIR+'bills_list_all.xml')
    bills = xmldoc.getElementsByTagName('Bill')
    
    # Start MySQL
    conn = MySQLdb.connect('localhost', 'peio', 'opendata', 'Parliament', charset='utf8');
    cursor = conn.cursor()
    cursor.execute('TRUNCATE table Bills');

    for bill in bills:
        try: BillID = int(bill.attributes['id'].value)
        except: 
            print 'Problem with Bill ID - may get bad'
            BillID = 0        
        
        try: Signature = bill.getElementsByTagName('Signature')[0].firstChild.data
        except: 
            print 'Signature Problem with bill id',BillID
            Signature = '000-000'
            pass 
        
        try: BillName  =  bill.getElementsByTagName('BillName')[0].firstChild.data
        except: 
            print 'BillName Problem with bill id',BillID
            BillName = 'Bill for ID:'+str(BillID)
            pass 
        
        try: Date = bill.getElementsByTagName('Date')[0].firstChild.data 
        except: 
            Date = '25/06/2009'
            pass        
     
        (day,month,year) = Date.split('/')
        BillDate = time.mktime( (int(year), int(month), int(day),0,0,0,0,0,0) )
                          
        if ( BillDate - NS41_Start)  >= 0:                        
            Type = classifyBill(Signature, BillName)
            Status =  getBill(BillID)          
                                      
            try: cursor.execute("""INSERT  INTO Parliament.Bills (ID, Signature, Date, Type, BillName, Status ) 
                VALUES(%s,%s,STR_TO_DATE(%s,'%%d/%%m/%%Y'),%s,%s,%s)""",(BillID, Signature, Date, Type, BillName, Status))
            except:
                print 'Problems with:',BillID, Signature
                pass
                   
    
    # Close MySQL
    cursor.close()
    conn.close()
     
    
    return True         

def getBill(key):
    'Индивидуална (допълнителна) информация за законопроект'
    
    BillID = int(key)
        
    url = 'http://parliament.yurukov.net/data/bills/bill_'+str(BillID)+'.xml'
    getData(url, BILLS_DATA_DIR, 0)
    
    xmldoc = minidom.parse(BILLS_DATA_DIR+'bill_'+str(BillID)+'.xml')
    
    # Къде е законопроекта? Приет/обнародван ли е?
    BillStatus = ''
    SGIss = xmldoc.getElementsByTagName('SGIss')[0].firstChild

    try:
        SGIss   
        SGIss = SGIss.data
        SGYear = xmldoc.getElementsByTagName('SGYear')[0].firstChild.data
        LawName = xmldoc.getElementsByTagName('LawName')[0].firstChild.data        
        #print 'Приет и обнародван в ДВ бр.',SGIss,'от',SGYear
        #print 'Част от',LawName
        #BillStatus = 'Обнародван в ДВ бр.'+SGIss+' от '+SGYear+'г.'
        BillStatus = 'Обнародван'    
    except:                
        try:# В зала
            statuses = xmldoc.getElementsByTagName('Status')                        
            BillStatus = statuses[-1].firstChild.data
        except: 
            try:# В комисия 
                commitees = xmldoc.getElementsByTagName('Commitee')[0].firstChild.data
                BillStatus = 'Комисия'
            except: 
                BillStatus = 'Внесен'
                
    # Вносители    
    '''
    Importers = []
    mps = xmldoc.getElementsByTagName('Importer')
    for mp in mps:
        Importers.append(mp.firstChild.data)
        #print mp.firstChild.data 
    '''
    return BillStatus
   
'HELPER FUNCTIONS'
def getData(url, data_dir=DATA_DIR, verbose=False):    
    'Свали и запиши файл с данни'
   
    file_name = url.split('/')[-1]
    dl_path = data_dir+file_name

    '@todo: Implement conditional get'    
    if os.path.exists(dl_path):
        if verbose: print 'file there',dl_path 
    else:
        if verbose: print 'get',url
        try: 
            urllib.urlretrieve(url, dl_path)
            if verbose: print 'downloaded ok'
        except:
            print 'cannot download', url
            return False
    return True  

def simplePoliticalForce(PoliticalForce):
    '''По-ясни и кратки имена на политическите сили
    Отстранява дългите имена и данните за изборните резултати от името на партията'''
    
    PoliticalForce = re.sub('( *\d{1,2}\.\d{1,2}%)|(\")', '', PoliticalForce)
    PoliticalForce = PoliticalForce.replace('Коалиция за България', 'КБ')
    PoliticalForce = PoliticalForce.replace('Синята коалиция', 'СК')
    PoliticalForce = PoliticalForce.replace('Партия Атака', 'Атака')
    PoliticalForce = PoliticalForce.replace('ДПС Движение за права и свободи', 'ДПС')
    PoliticalForce = PoliticalForce.replace('Ред, законност и справедливост', 'РЗС')
    
    return PoliticalForce    

def MPConstituency(Constituency):   
    MIR, Region = Constituency.split('-')    
    return int(MIR), Region

def classifyBill(Signature, BillName):
    'Класифициране на Законопроекти, Решения, Закони за ратификация'
    
    Type = ''
    if '-' in Signature:            
        Type =  'Законопроект'
        if 'ратифициране' in BillName:
            Type = 'Ратификация'
            #print BillName
    else:
        Type = 'Решение'
        if 'ДЕКЛАРАЦИЯ' in BillName:                
            Type = 'Декларация'        
            #print BillName  
    
    return Type

if __name__ == '__main__':
    getAllMP()
    getAllBills()
