# -*- coding: utf-8 -*-

from xml.dom import minidom
import re, pickle, os, urllib, time, glob

DATA_DIR = '../data/'
MP_DATA_DIR = DATA_DIR+'/mp/'
BILLS_DATA_DIR = DATA_DIR+'/bills/'
SERIALIZE_DIR = '../serialized/'

# Да стане на хеш
MP_DataStruc_file = SERIALIZE_DIR+'MP_FullName-ID-PoliticalForce.pkl'
ID2MP_DataStruct_file = SERIALIZE_DIR+'ID2MP_ID-FullName.pkl'
PG_DataStruct_file = SERIALIZE_DIR+'PG_PoliticalForce-ID.pkl'
Bills_DataStruct_file = SERIALIZE_DIR+'Bills_Signature-PoliticalForce-BillID-BillName-BillDate-Type.pkl'
BillID2Signature_DataStruct_file = SERIALIZE_DIR+'BillID2Signature_Signature-BillID.pkl'

DataFile = {}
DataFile['MP'] = SERIALIZE_DIR+'MP_FullName-ID-PoliticalForce.pkl'
DataFile['ID2MP'] = SERIALIZE_DIR+'ID2MP_ID-FullName.pkl'
DataFile['PG'] = SERIALIZE_DIR+'PG_PoliticalForce-ID.pkl'
DataFile['Bills'] = SERIALIZE_DIR+'Bills_Signature-PoliticalForce-BillID-BillName-BillDate-Type.pkl'
DataFile['BillID2Signature'] = SERIALIZE_DIR+'BillID2Signature_BillID-Signature.pkl'

# Начало на 41 НС
NS41_Start = ( 2009, 6, 25, 0, 0, 0, 0, 0, 0)
NS41_Start = time.mktime(NS41_Start)

'MAIN FUNCTIONS'
def getAllMP():
    'Списък на всички Народни представители от 41то НС'

    # Members of Parliament 
    MP = {}
    # ID to MP name mapping
    ID2MP = {}        
    
    # Parse xml data
    xmldoc = minidom.parse(DATA_DIR+'mp_list.xml')
    profiles = xmldoc.getElementsByTagName('Profile')       
    
    for profile in profiles:
        # Get the vars we need
        ID = int(profile.attributes['id'].value)
        PoliticalForce = profile.getElementsByTagName('PoliticalForce')[0].firstChild.data
        FullName = profile.getElementsByTagName('FullName')[0].firstChild.data
        
        # Form a data structure with the data we need        
        MP[FullName] = {}
        MP[FullName]['ID'] = ID
        MP[FullName]['PoliticalForce'] = simplePoliticalForce(PoliticalForce)
        
        ID2MP[ID] = FullName
    
    return MP, ID2MP

def getMP(key):
    'Допълваме информацията за народен представител'
    
    'Като идентификатор може да ползваме id на депутата или трите му имена'
    try: key = int(key) # По-добре да не си вярваме особено много
    except ValueError:
        pass 
        
    'Разчитаме на вече създадена структура за всички депутати'
    try: MP
    except: 
        try: MP,ID2MP = deserializeData('MP', 'ID2MP')       
        except:
            (MP, ID2MP) = getAllMP()
            serializeData(MP, MP_DataStruc_file)
            serializeData(ID2MP, ID2MP_DataStruct_file) 
    
    if type(key) is int:
        #FullName = ID2MP[key]
        FullName = autoCorrectFullName(ID2MP[key], MP, ID2MP)
        ID = key
    elif (type(key) is str) or (type(key) is unicode):
        key = key.upper()
        FullName = autoCorrectFullName(key, MP, ID2MP )
        ID = MP[FullName]['ID']        
    else: 
        return False          
           
    # По ID може да извлечем пълната индивидуална информация      
    url = 'http://parliament.yurukov.net/data/mp/mp_'+str(ID)+'.xml'
    getData(url, MP_DATA_DIR)    

    xmldoc = minidom.parse(MP_DATA_DIR+'mp_'+str(ID)+'.xml' )      

    'Информация за внесените законопроекти'
    bills = xmldoc.getElementsByTagName('Bill')
    MP[FullName]['Bills'] = []                
    for bill in bills:
        'Няма ID на законопроекта - ще ни трябва Signature2ID mapping'            
        '''try: BillID = bill.attributes['id'].value
        except: 
            print 'Problem with Bill ID - may get bad'
            BillID = 0'''        
        
        'Ще ползваме сигнатурата като идентификатор'
        try: Signature = bill.getElementsByTagName('Signature')[0].firstChild.data
        except: 
            print 'Bill Signature Problem'
            Signature = '000-00-000'
            pass 
        
        'Тази информация по-добре да я вземем от индивидуалните данни за законопроекта'
        '''
        try: BillName  =  bill.getElementsByTagName('Name')[0].firstChild.data
        except: 
            print 'BillName Problem'
            BillName = Signature
            pass 
        
        try: Date = bill.getElementsByTagName('Date')[0].firstChild.data 
        except: 
            print 'Bill Date Problem'
            Date = '25/6/2009' # Началото на работата на 41 НС
            pass
        '''
        
        MP[FullName]['Bills'].append(Signature)          
    
    'Информация за актуалните въпроси и питания'
    questions = xmldoc.getElementsByTagName('Question')
    MP[FullName]['Questions'] = []
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
         
        MP[FullName]['Questions'].append( (Date, To, About) )                       
    
    return MP[FullName]        

def getPG(*Party):
    'Данни за парламентарните групи'
   
    'Разчитаме на вече създадена структура за всички депутати'
    try: MP
    except: 
        try: (MP, ID2MP) = deserializeData('MP', 'ID2MP')       
        except:
            (MP, ID2MP) = getAllMP()
            serializeData(MP, MP_DataStruc_file)
            serializeData(ID2MP, ID2MP_DataStruct_file)     
    
    PG = {}
    for name in MP.keys():
        PoliticalForce = MP[name]['PoliticalForce']
        if (PoliticalForce in Party) or (not Party):
            try: PG[PoliticalForce].append(MP[name]['ID'])
            except:
                PG[PoliticalForce] = []
                PG[PoliticalForce].append(MP[name]['ID'])
        else:
            continue
    
    return PG

def getAllBills(Serialize=True):
    'Списък на законопроектите на 41 НС'
    
    Bills = {}
    BillID2Signature = {}
    
    xmldoc = minidom.parse(DATA_DIR+'bills_list_all.xml')
    bills = xmldoc.getElementsByTagName('Bill')

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
            BillName = 'Bill for ID:',BillID
            pass 
        
        try: Date = bill.getElementsByTagName('Date')[0].firstChild.data 
        except: 
            Date = '25/06/2009'
            pass        
     
        (day,month,year) = Date.split('/')
        BillDate = time.mktime( (int(year), int(month), int(day),0,0,0,0,0,0) )
                          
        if ( BillDate - NS41_Start)  >= 0:                        
            Bills[Signature] = {}
            Bills[Signature]['BillDate'] = BillDate            
            Bills[Signature]['BillID'] = BillID
            Bills[Signature]['BillName'] = BillName
            Bills[Signature]['Type'] = classifyBill(Signature, BillName)      
                   
            BillID2Signature[BillID] = Signature            

    if Serialize:
        serializeData(Bills, DataFile['Bills'])
        serializeData(BillID2Signature, DataFile['BillID2Signature'])        
    
    return Bills, BillID2Signature         

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

def getBill(key):
    'Информация за законопроект'
    
    #Тези данни пак ни трябват. Може би е добре да си ги има и иначе 
    try: Bills    
    except:        
        (Bills,BillID2Signature) = deserializeData('Bills', 'BillID2Signature' )
    
    'Трябва да може да работим с (int)ID  или със (str)Сигнатура'
    if type(key) is int:
        BillID = key
        Signature = BillID2Signature[key]
        print Bills[Signature]['BillName']
    elif  type(key) is str:
        Signature = key
        BillID = Bills[Signature]['BillID']
        print Bills[Signature]['BillName']  
    
    url = 'http://parliament.yurukov.net/data/bills/bill_'+str(BillID)+'.xml'
    getData(url, BILLS_DATA_DIR, 0)
    
    xmldoc = minidom.parse(BILLS_DATA_DIR+'bill_'+str(BillID)+'.xml')
    
    # Приет/обнародван ли е?
    BillStatus = ''
    SGIss = xmldoc.getElementsByTagName('SGIss')[0].firstChild.data
    if SGIss != '0':
        SGYear = xmldoc.getElementsByTagName('SGYear')[0].firstChild.data
        LawName = xmldoc.getElementsByTagName('LawName')[0].firstChild.data        
        print 'Приет и обнародван в ДВ бр.',SGIss,'от',SGYear
        print 'Част от',LawName
        BillStatus = 'Обнародван в ДВ бр.'+SGIss+' от '+SGYear+'г.'    
    else:                
        statuses = xmldoc.getElementsByTagName('Status')
        print statuses[-1].firstChild.data            
        BillStatus = statuses[-1].firstChild.data
    Bills[Signature]['Status'] = BillStatus
            
    # Вносители    
    Importers = []
    mps = xmldoc.getElementsByTagName('Importer')
    for mp in mps:
        Importers.append(mp.firstChild.data)
        print mp.firstChild.data
    
    Bills[Signature]['Importers'] = Importers
          
    return Bill
   
'HELPER FUNCTIONS'
def getData(url, data_dir=DATA_DIR, verbose=False):    
    'Свали и запиши файл с данни'
   
    file_name = url.split('/')[-1]
    dl_path = data_dir+file_name

    '@todo: Implement conditional get'    
    if os.path.exists(dl_path):
        if verbose: print 'file there'
    else:
        if verbose: print 'get',url
        try: 
            urllib.urlretrieve(url, dl_path)
            if verbose: print 'downloaded ok'
        except:
            print 'cannot download', url
            return False
    return True  

def serializeData(DataStruct, file):
    'Сериализация на структурa от данни'
      
    output = open(SERIALIZE_DIR+file, 'wb')
    pickle.dump(DataStruct, output)
    output.close()    
    return True

def deserializeData( *deserializeVars ):
    'Десериализация на структурa от данни'
    
    '@todo: по-малко ужасни имена на променливи'
    serialized_files =  glob.glob(SERIALIZE_DIR+'*pkl')
    serialized_vars = {}
    
    for file in serialized_files:
        varname = file.replace(SERIALIZE_DIR, '')
        varname = varname.split('_')[0]
        serialized_vars[varname] = file                
    
    deserialized_vars = []
    for deserialize_var in deserializeVars:
        try: 
            serialized_vars[deserialize_var]
            pkl_file = open(serialized_vars[deserialize_var], 'rb')
            deserialize_var = pickle.load(pkl_file)
            pkl_file.close()
            deserialized_vars.append(deserialize_var)
        except:
            #print deserialize_var, 'variable is not found'
            return False
            
    return deserialized_vars 

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

def autoCorrectFullName(FullName, MP, ID2MP ):    
    'Опит за автоматична поправка на несъвпадащи три имена'   
    try: MP
    except: print 'autoCorrect Needs MP and ID2MP structures'
       
    # Test errors with  FullName = u'ИВАН ЙОРДАНОВ КОСТОф' # can be autocorrected
    # Test errors with  FullName = u'ДИЕГО АРМАНДО МАРАДОНА' # can not be autocorrected
    try: 
        MP[FullName]
        return FullName
    except KeyError: # Тоя го няма       
        import difflib
        
        # Опитваме автоматична корекция
        mp_dictionary = []
        for mp_name in ID2MP.values():
            mp_dictionary.append(mp_name) 
        
        try: 
            FullName = difflib.get_close_matches(FullName, mp_dictionary, 1)[0]
            print 'FullName autocorrected to', FullName
            del(mp_dictionary)
            return FullName            
        except:
            print 'Къв си ти, бе', FullName
            return False   

'TESTING FUNCTIONS'
def test_getAllMP(limit=10):
    'Проверка на съдържанието на структурата за Народните представители'
    '''Input: (int) limit - брой записи
       Returns: Структура от данни с  
    '''
    (mps,id2mp) = getAllMP()
    print 'size:',len(mps)
   
    i = 0
    for name in mps.keys():
        if i < limit:
            print name, mps[name]['ID'], mps[name]['PoliticalForce']
            #print mps[name]
        else: 
            break
        i += 1

def test_getMP(key=1005): # Get Костов u'ИВАН ЙОРДАНОВ КОСТОВ'      
    mp = getMP(key)
    
    print 'Законопроекти:'
    for signature in mp['Bills']:
        print signature, 
    
    print 'Питания:'
    for (date, to, question) in mp['Questions']:
        print date, to, question
    return True         

def test_getAllBills(limit=10):
    'Проверка на съдържанието на структурата на законопроектите'
    
    bills = getAllBills()
    print 'size', len(bills)
    
    i = 0
    for signature in bills.keys():
                
        if i < limit:
            print signature, bills[signature]['BillID'], bills[signature]['BillName'], bills[signature]['BillDate']
            print bills[signature]
        else:             
            break
        i += 1

def test_getPG():
    pg = getPG('РЗС', 'СК') 
    print len (pg)
    for party in pg.keys():
        for mp in pg[party]:
            print party,'-',mp

