import pypyodbc  # импорт библиотеки


mySQLServer = 'DESKTOP-M15245Q\SQLEXPRESS'  # Имя сервера (в моем случае локального)
myDataBase = 'Aviakassa'  # Имя БД

connection = pypyodbc.connect('Driver={SQL Server};'  # подключение к БД, которая на MySqlServer
                              'Server=' + mySQLServer + ';'
                              'Database=' + myDataBase + ';')

cursor = connection.cursor()  # будет выполнять запросы на sql

# добавление
# mySQLQuery1 = ('''
# INSERT INTO Worker(ID_Sotr, About, FIO) VALUES (0012, 'Пилот', '111');
# ''')
# cursor.execute(mySQLQuery1)
# connection.commit()

# оздание и отображение запросов
mySQLQuery2 = ('''
SELECT * FROM Worker WHERE(Worker.About LIKE 'Пилот');
''')
cursor.execute(mySQLQuery2)
results = cursor.fetchall()
for i in results:
    print(i)

# закрытие курсора и конец подключения
cursor.close()
connection.close()