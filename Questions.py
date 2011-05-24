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

#Законопроекти по депутат
Question = {}
Question['Human'] = 'Кои депутати са внесли най-много законопроекти?'
Question['Query'] = "SELECT FullName, PoliticalForce, count(*) as NumBills FROM Parliament.MP2Signature, Parliament.MP where MP2Signature.MPID=MP.ID group by FullName order by NumBills desc;"
Question['Headers'] = ['Име','Партия', 'Брой законопроекти']
Questions.append(Question)

#Законопроекти по партия
Question = {}
Question['Human'] = 'Коя партия колко законопроекта е внесла?'
Question['Query'] = "SELECT PoliticalForce, count(*) as NumBills FROM Parliament.MP2Signature, Parliament.MP where MP2Signature.MPID=MP.ID group by PoliticalForce order by NumBills desc;"
Question['Headers'] = ['Партия', 'Брой законопроекти']
Questions.append(Question)

def ask(Question):
    'Ask a question'
    print Question['Human']
    
    # Start MySQL
    conn = MySQLdb.connect('localhost', 'peio', 'opendata', 'Parliament', charset='utf8');
    cursor = conn.cursor()     
    
    cursor.execute(Question['Query'])
    rows = cursor.fetchall ()
    
    htmlAnswer = createTable(Question['Human'], rows, Question['Headers'])
    drawAnswer(Question['Human'], htmlAnswer)
    
    # Close MySQL
    cursor.close()
    conn.close()       

def createTable(Question, rows, headers):
    
    'Example from: https://code.google.com/apis/chart/interactive/docs/examples.html#table_example'
    HTML = ''
    Header = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>'''
        
    Header2 = '''  
    </title>
    <script type="text/javascript" src="http://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1', {packages: ['table']});
    </script>
    <script type="text/javascript">
    function drawVisualization() {
      // Create and populate the data table.
      var data = new google.visualization.DataTable(); '''
       
    HTML += Header+Question+Header2
      
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
    Footer = '''
          // Create and draw the visualization.
      visualization = new google.visualization.Table(document.getElementById('table'));
      visualization.draw(data, null);
    }
     
     
    google.setOnLoadCallback(drawVisualization);
    </script>
  </head>
  <body style="font-family: Arial;border: 0 none;">
    <div id="table"></div>
  </body>
  </html>
    '''  
    HTML += Footer
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
    ANSWERS_DIR = './answers/'
    from hashlib import sha1
    answer_file = sha1(Question).hexdigest()    
    fd = open(ANSWERS_DIR+answer_file+'.html', 'w+')
    fd.write(html)
    fd.close()
    
    print ANSWERS_DIR+answer_file+'.html'
    
for Question in Questions:
    ask(Question)