# -*- coding: utf-8 -*-
import MySQLdb

Questions = []
# Питания по депутат
Question = {}
Question['Human'] = 'Кои депутати са задали най-много актуални въпроси и питания?'
Question['Query'] = "select FullName, PoliticalForce, count(*) as NumQ from `Parliament`.`Questions`, `Parliament`.`MP` where Questions.MPID=MP.ID group by FullName order by NumQ desc"
Question['Headers'] = ['Име','Партия', 'Брой питания']
Questions.append(Question)

# Питания по Партия
Question = {}
Question['Human'] = 'Коя партия колко актуални въпроси и питания е задала?'
Question['Query'] = "select PoliticalForce, count(*) as NumQ from `Parliament`.`Questions`, `Parliament`.`MP` where Questions.MPID=MP.ID group by PoliticalForce order by NumQ desc;"
Question['Headers'] = ['Партия', 'Брой питания']
Questions.append(Question)

# Нито едно питане
Question = {}
Question['Human'] = 'Кои депутати не са отправили нито едно питане?'
Question['Query'] = "select distinct FullName, PoliticalForce from `Parliament`.`MP`, `Parliament`.`Questions` where MP.ID NOT IN (select distinct MPID from `Parliament`.`Questions`);" 
Question['Headers'] = ['Име', 'Партия']
Questions.append(Question)

#Законопроекти по депутат
Question = {}
Question['Human'] = 'Кои депутати са внесли най-много законопроекти?'
Question['Query'] = "SELECT FullName, PoliticalForce, count(*) as NumBills FROM Parliament.MP2Signature, Parliament.MP where MP2Signature.MPID=MP.ID group by FullName order by NumBills desc;"
Question['Headers'] = ['Име','Партия', 'Брой законопроекти']
Questions.append(Question)

# Кои депутати не са подали нито един законопроект?
Question = {}
Question['Human'] = 'Кои депутати не са внесли нито един законопроект?' 
Question['Query'] = "select distinct FullName, PoliticalForce from `Parliament`.`MP`, `Parliament`.`MP2Signature` where MP.ID NOT IN (select distinct MPID from `Parliament`.`MP2Signature`);"
Question['Headers'] = ['Име','Партия']
Questions.append(Question)

#Законопроекти по партия
Question = {}
Question['Human'] = 'Коя партия колко законопроекта е внесла?'
Question['Query'] = "SELECT PoliticalForce, count(*) as NumBills FROM Parliament.MP2Signature, Parliament.MP where MP2Signature.MPID=MP.ID group by PoliticalForce order by NumBills desc;"
Question['Headers'] = ['Партия', 'Брой законопроекти']
Questions.append(Question)

# На кой депутат, кои законопроекти са му приети
Question = {}
Question['Human'] = "На кой депутат, кои законопроекти са приети?"
Question['Query'] = "SELECT FullName, PoliticalForce, BillName from Parliament.MP, Parliament.Bills, Parliament.MP2Signature where MP.ID=MP2Signature.MPID and MP2Signature.Signature=Bills.Signature and Bills.Type='Законопроект' and Bills.Status='Обнародван';" 
Question['Headers'] = ['Име','Партия', 'Законопроект']
Questions.append(Question)

# На коя партия, кои законопроекти са приети
Question = {}
Question['Human'] = "На коя партия, кои законопроекти са приети?"
Question['Query'] = "SELECT distinct PoliticalForce, BillName from Parliament.MP, Parliament.Bills, Parliament.MP2Signature where MP.ID=MP2Signature.MPID and MP2Signature.Signature=Bills.Signature and Bills.Type='Законопроект' and Bills.Status='Обнародван';" 
Question['Headers'] = ['Партия', 'Законопроект']
Questions.append(Question)

# На коя партия колко законопроекта са приети?
Question = {}
Question['Human'] = "На коя партия колко законопроекта са приети?"
Question['Query'] = "SELECT PoliticalForce,  count(*) as Num from Parliament.MP, Parliament.Bills, Parliament.MP2Signature where MP.ID=MP2Signature.MPID and MP2Signature.Signature=Bills.Signature and Bills.Type='Законопроект' and Bills.Status='Обнародван' group by PoliticalForce order by Num desc;" 
Question['Headers'] = ['Партия', 'Брой приети законопроекти']
Questions.append(Question)

#Кои депутати са посочили село като родно място?
Question = {}
Question['Human'] = 'Кои депутати са посочили село като родно място?'
Question['Query'] = "select FullName, PoliticalForce, PlaceOfBirth from `Parliament`.`MP` where PlaceOfBirth LIKE 'с.%';"
Question['Headers'] = ['Име','Партия', 'Родно място']
Questions.append(Question)

# Кой откъде
Question = {}
Question['Human'] = 'От къде са народните представители?' 
Question['Query'] = "select PlaceOfBirth, count(*) as Num from `Parliament`.`MP` group by PlaceOfBirth order by Num desc;" 
Question['Headers'] = ['Родно място', 'Брой']
Questions.append(Question)


'''
# Question template
Question = {}
Question['Human'] = 
Question['Query'] = 
Question['Headers'] = [,]
Questions.append(Question)
'''

ANSWERS_DIR = './answers/'


def ask(Question):
    'Ask a question'
    print Question['Human']
    
    # Start MySQL
    conn = MySQLdb.connect('localhost', 'peio', 'opendata', 'Parliament', charset='utf8');
    cursor = conn.cursor()     
    
    cursor.execute(Question['Query'])
    rows = cursor.fetchall ()
    
    htmlAnswer = createTable(Question['Human'], rows, Question['Headers'])
    linkAnswer = drawAnswer(Question['Human'], htmlAnswer)
    
    # Close MySQL
    cursor.close()
    conn.close() 
    
    return '<a href="'+linkAnswer+'">'+Question['Human']+'</a>'      

def createTable(Question, rows, headers):
    
    'Example from: https://code.google.com/apis/chart/interactive/docs/examples.html#table_example'
    HTML = ''
    Header2Title = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>'''
        
    Header2Data = '''  
    </title>
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1', {packages: ['table']});
    </script>
    <script type="text/javascript">
    function drawVisualization() {
      // Create and populate the data table.
      var data = new google.visualization.DataTable(); '''
       
    HTML += Header2Title+Question+Header2Data
      
    table_row = 0 # Current table row
    table_cols = len(rows[0])    
    for c in range(table_cols):
        type = getType(rows[0][c])
        if not headers[c]: 
            HTML += "data.addColumn('"+type+"', '');\n"
        else:
            HTML += "data.addColumn('"+type+"', '"+headers[c]+"');\n"

    table_rows = len(rows)
    HTML += 'data.addRows('+str(table_rows)+');\n'
    
    for row in rows:
        table_column = 0
        for col in row:
            if getType(col) == "string": 
                HTML += 'data.setCell('+str(table_row)+', '+str(table_column)+', "'+str(col)+'");\n'
            else:
                HTML += 'data.setCell('+str(table_row)+', '+str(table_column)+', '+str(col)+');\n'
            table_column += 1
        table_row += 1
    Data2Body = '''
          // Create and draw the visualization.
      visualization = new google.visualization.Table(document.getElementById('table'));
      visualization.draw(data, null);
    }
     
     
    google.setOnLoadCallback(drawVisualization);
    </script>
  </head>
  '''
    HTML += Data2Body
    Body2Table = '''
  <body style="font-family: Arial;border: 0 none;">
    '''
    Body2End = '''
    <div style="width: 600px;" id="table"></div>
  </body>
  </html>
    '''  

    HTML += Body2Table+'<h3>'+Question+'</h3>'+Body2End
    return HTML  

def getType(data):
    'determine the data type'

    Type = ''
    if isinstance(data, basestring):
        Type = 'string'
        return Type
    elif (type(data) is int) or (type(data) is long):
        Type = 'number'
        return Type  
    else:
        print type(data)
        return False
        
def drawAnswer(Question, html):
    ''
    from hashlib import sha1
    answer_file = sha1(Question).hexdigest()    
    fd = open(ANSWERS_DIR+answer_file+'.html', 'w+')
    fd.write(html)
    fd.close()
    
    return answer_file+'.html'

# Списък с въпроси и отговори

def buildIndex(Questions):
    
    fd = open(ANSWERS_DIR+'index.html', 'w+')
    Header = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>Въпроси и отговори  
    </title>
  </head>
  
  <body style="font-family: Arial;border: 0 none;">    
    '''
    fd.write(Header)
    fd.write('<h3>Въпроси и отговори</h3><ul>')
    for Question in Questions:    
        answer = ask(Question)
        fd.write('<li>'+answer+'</li>')
    
    fd.write('</ul>')
    
    Footer = '''
    </body>
    </html>    
    '''
    
    fd.write(Footer)
    fd.close()
    
    return True

if __name__ == '__main__':
    buildIndex(Questions)