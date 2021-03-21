from flask import Flask, render_template, make_response, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import redirect
from docxtpl import DocxTemplate
import pypyodbc  # импорт библиотеки sql


app = Flask(__name__)  # создание приложения
app.config['SECRET_KEY'] = 'test'

mySQLServer = 'DESKTOP-M15245Q\SQLEXPRESS'  # Имя сервера (в моем случае локального)
myDataBase = 'Otoplenie'  # Имя БД

connection = pypyodbc.connect('Driver={SQL Server};'  # подключение к БД, которая на MySqlServer
                              'Server=' + mySQLServer + ';'
                              'Database=' + myDataBase + ';')

cursor = connection.cursor()  # будет выполнять запросы на sql

spisok = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
spisok_buk = ['ё', 'й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ', 'ф', 'ы', 'в', 'а', 'п', 'р', 'о',
              'о', 'л', 'д', 'ж', 'э', 'я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю']


class NewClient(FlaskForm):
    data_birthday = StringField('Дата рождения (по форме ГГГГ.ММ.ДД):', validators=[DataRequired()])
    phone = StringField('Номер телефона (по форме +7**********):', validators=[DataRequired()])
    fio_sobstv = StringField('ФИО Собственника:', validators=[DataRequired()])
    pasport = StringField('Серия и номер паспорта (ввод без пробела):', validators=[DataRequired()])
    gender = StringField('Пол (м/ж):', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class NewFlat(FlaskForm):
    gorod = StringField('Город:', validators=[DataRequired()])
    street = StringField('Улица:', validators=[DataRequired()])
    dom = StringField('Номер дома:', validators=[DataRequired()])
    id_flat = StringField('Номер квартиры:', validators=[DataRequired()])
    other_info = StringField('Площадь квартиры (кв.м.):', validators=[DataRequired()])
    temperatura = StringField('Средняя температура в квартире (от -100 до +100 градусов):', validators=[DataRequired()])
    schetchik = StringField('Наличие счетчика (да/нет):', validators=[DataRequired()])
    company = StringField('Обслуживающая компания:', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class NewSchetchik(FlaskForm):
    date_ustanovk = StringField('Дата установки счетчика (в формате ГГГГ.ММ.ДД):', validators=[DataRequired()])
    firma = StringField('Фирма производства:', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class DeleteClient(FlaskForm):
    pasport = StringField('Серия и номер паспорта (ввод без пробела):', validators=[DataRequired()])
    submit = SubmitField('Удалить')


class AddPokaz(FlaskForm):
    pasport = StringField('Серия и номер паспорта (ввод без пробела):', validators=[DataRequired()])
    pokaz = StringField('Показания счетчика:', validators=[DataRequired()])
    month_pokaz = StringField('Месяц:', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class ChangePokaz(FlaskForm):
    pasport = StringField('Серия и номер паспорта (ввод без пробела):', validators=[DataRequired()])
    pokaz = StringField('Новын показания счетчика:', validators=[DataRequired()])
    month_pokaz = StringField('Месяц:', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class ChangeInfoCompany(FlaskForm):
    nazv_old = StringField('Название:', validators=[DataRequired()])
    tariff = StringField('Тариф (стоимость за 1 кв.м.):', validators=[DataRequired()])
    recvizit = StringField('Реквизиты:', validators=[DataRequired()])
    fio_ruck = StringField('ФИО Руководителя:', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class ChangeInfoClient(FlaskForm):
    pasport_old = StringField('Серия и номер паспорта(ввод без пробела):', validators=[DataRequired()])
    data_birthday = StringField('Дата рождения (по форме ГГГГ.ММ.ДД):', validators=[DataRequired()])
    phone = StringField('Номер телефона (по форме +7**********):', validators=[DataRequired()])
    fio_sobstv = StringField('ФИО Собственника:', validators=[DataRequired()])
    pasport = StringField('Серия и номер паспорта (ввод без пробела):', validators=[DataRequired()])
    gender = StringField('Пол (м/ж):', validators=[DataRequired()])
    submit = SubmitField('Изменить')


class Pay(FlaskForm):
    data_pay = StringField('Дата:', validators=[DataRequired()])
    pasport = StringField('Серия и номер паспорта (ввод без пробела):', validators=[DataRequired()])
    submit = SubmitField('Создать')


class AboutClient(FlaskForm):
    pasport = StringField('Серия и номер паспорта (ввод без пробела):', validators=[DataRequired()])
    submit = SubmitField('Найти')


def main():
    app.run(port=8048, host='127.0.0.1')


# проерка только на наличие цифр
def chek_number(slovo):
    for i in str(slovo):
        if i not in spisok:
            if i != '.':
                return False


# проверка только на наличие букв
def chek_bukv(slovo):
    for i in str(slovo).lower():
        if (i != ' ') and (i != '-'):
            if i not in spisok_buk:
                return False


# проверка корректности ввода паспорта
def chek_pasport(pasport):
    if len(str(pasport)) != 10:
        return 'Неверное число символов в серии и номере паспорта!'
    else:
        if '.' in pasport:
            return 'В поле паспорт присутствуют посторонние символы (уберите ".")'
        if chek_number(pasport) == False:
            return 'В поле серия и номер присутствуют посторонние символы!'
    return ''


# проверка корректности ввода даты
def chek_data(znach_data):
    if len(znach_data) == 10:  # проверка длинны введенной даты
        vrem = znach_data.split('.')
        if len(vrem) == 3:  # проверка формата ввода
            if (len(vrem[0]) != 4) or (len(vrem[1]) != 2) or (len(vrem[2]) != 2):
                return "Неверный формат, введите по формату ГГГГ.ММ.ДД"
            else:
                message = chek_number(znach_data)
                if message == False:
                    return 'В поле дата присутсвуют посторонние символы'
                if int(vrem[0]) > 2021:
                    return 'Год указан неверно!'
                if '00' == vrem[1]:
                    return 'Введите месяц больше 0!'
                if '00' == vrem[2]:
                    return 'Введите число больше 0!'
                if 0 > int(vrem[1]) or int(vrem[1]) > 12:  # проверка корректности введенного месяца
                    return "Неверно введен месяц, введите по формату ГГГГ.ММ.ДД"
                else:  # проверка числа дней в месяце
                    mes = int(vrem[1])
                    day = int(vrem[2])
                    spisok_day_mes = [31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    if mes == 2:
                        if int(vrem[0]) // 4 == 0:
                            if 0 < day > 29:
                                return "Количество дней не допустимое в месяце!"
                        else:
                            if 0 < day > 28:
                                return "Количество дней не допустимое в месяце!"
                    else:
                        if 0 < day > spisok_day_mes[mes - 1]:
                            return "Количество дней не допустимое в месяце!"
            if chek_number(znach_data) == False:
                return "В введенной дате имеются буквы!"
        else:
            return "Введите дату через точку! (ГГГГ.ММ.ДД)"
    else:
        return "Неверное число символов в дате рождения!"
    return ''


# проверка корректности ввода телефона
def chek_phone(phone):
    if phone[0] != '+':  # проверка корректности введенного телефона
        return "Номер телефона начинается с не с +7!"
    elif len(phone) == 12:
        if chek_number(phone[1::]) == False:
            return "В номере телефона присутствуют посторонние символы!"
    else:
        return "Неверное число символов в номере телефона!"
    return ''


# проверка ФИО человека
def chek_fio(fio):
    sobstv = fio.split()
    print(fio)
    print(sobstv)
    if 4 > len(sobstv) > 1:
        if chek_bukv(fio) == False:
            return "В поле ФИО Собственника присутсвуют посторонние символы!"
    else:
        return "В поле ФИО Собственника укажите ФИО!"
    return ''


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("base.html", title='Учет платы за отопление')


@app.route("/client", methods=['GET', 'POST'])
def client():
    return render_template("client.html", title='Работа с клиентами (Добавление, изменение, просмотр, удаление информации)')


@app.route("/company", methods=['GET', 'POST'])
def company():
    return render_template("company.html", title='Работа с команиями (Изменение, просомтр информации)')


@app.route("/schetchik", methods=['GET', 'POST'])
def schetchik():
    return render_template("schetchik.html", title='Работа с счетчиками (Изменение, просомтр информации)')


@app.route("/itog", methods=['GET', 'POST'])
def itog():
    form = Pay()  # обращениек классу формы
    temp = 'itog.html'  # имя шаблона
    title = 'Создание квитанции'  # заголовок страницы
    if form.validate_on_submit():
        message = chek_pasport(form.pasport.data)  # проверка корректности паспорта
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT ID_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info_sobstvinn_id = cursor.fetchall()
        if not info_sobstvinn_id:
            return render_template(temp, title=title, form=form,
                                   message="Клиент с такими паспортными данными не существует!")
        message = chek_data(form.data_pay.data)  # проверка корректности паспорта
        if message != '':
            return render_template(temp, title=title, form=form, message=message)

        for_zapros = "Sobstv.ID_sobstv LIKE'%" + str(info_sobstvinn_id[0][0]) + "%'"
        zapros = ('''SELECT FIO_sobstv, Phone FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info1_sobstvinn = cursor.fetchall()

        for_zapros = "Flat.ID_sobstv='" + str(info_sobstvinn_id[0][0]) + "'"
        zapros = ('''SELECT * FROM Flat WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info2_sobstvinn = cursor.fetchall()

        passport_pay = form.pasport.data
        fio_pay, phone_pay = info1_sobstvinn[0]
        id_flat, adres_pay, plosh_pay, tempa_pay, info_sobstvinn_id, id_company = info2_sobstvinn[0]

        for_zapros = "Company.ID_company='" + str(id_company) + "'"
        zapros = ('''SELECT * FROM Company WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info3_sobstvinn = cursor.fetchall()
        id_company, nazv_pay, tarif, recvizit_pay, fio_ruc = info3_sobstvinn[0]

        for_zapros = "Schetchik.ID_flat='" + str(id_flat) + "'"
        zapros = ('''SELECT * FROM Schetchik WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info2_sobstvinn = cursor.fetchall()
        if info2_sobstvinn:
            id_shetchik, id_flat, ust_pay, firma_pay = info2_sobstvinn[0]
            shetchik_status_pay = 'есть'
            for_zapros = "Pokaz.ID_schetchik='" + str(id_flat) + "'"
            zapros = ('''SELECT Adout_pokaz, Month_pokaz FROM Pokaz WHERE(%s);''' % for_zapros)
            cursor.execute(zapros)
            info4_sobstvinn = cursor.fetchall()
            about_pokaz_pay, month_pokaz_pay = info4_sobstvinn[0]
            itog_pay = int(about_pokaz_pay) * int(tarif)
        else:
            shetchik_status_pay = 'нет'
            about_pokaz_pay, month_pokaz_pay, ust_pay, firma_pay = ('-', '', '-', '-')
            itog_pay = int(plosh_pay) * int(tarif)
        for_zapros = "Lgot.ID_sobstv LIKE'%" + str(info_sobstvinn_id) + "%'"
        zapros = ('''SELECT Discount FROM Lgot WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info5_sobstvinn = cursor.fetchall()
        if info5_sobstvinn:
            discount_pay = info5_sobstvinn[0][0]
            itog_discount_pay = itog_pay * 10 // 100
        else:
            discount_pay = 'нет'
            itog_discount_pay = 0
        oplata = itog_pay - itog_discount_pay
        data_pay = form.data_pay.data

        doc = DocxTemplate('C:/Users/79299/PycharmProjects/Praktika/shablon_kvit.docx')
        znach = {'nazv_pay': str(nazv_pay),
                  'fio_ruc': str(fio_ruc),
                  'recvizit_pay': str(recvizit_pay),
                  'fio_pay': str(fio_pay),
                  'passport_pay': str(passport_pay),
                  'adres_pay': str(adres_pay),
                  'phone_pay': str(phone_pay),
                  'month_pokaz_pay': str(month_pokaz_pay),
                  'plosh_pay': str(plosh_pay),
                  'tempa_pay': str(tempa_pay),
                  'shetchik_status_pay': str(shetchik_status_pay),
                  'ust_pay_data': str(ust_pay),
                  'firma_pay': str(firma_pay),
                  'about_pokaz_pay': str(about_pokaz_pay),
                  'discount_pay': str(discount_pay),
                  'itog_pay': str(itog_pay),
                  'itog_discount_pay': str(itog_discount_pay),
                  'oplata': str(oplata),
                  'data_pay': str(data_pay)}
        doc.render(context=znach)
        doc.save('C:/Users/79299/PycharmProjects/Praktika/otchet/kvit%s.docx' % info_sobstvinn_id)
        return redirect('/')
    return render_template(temp, title=title, form=form)


@app.route("/new_client", methods=['GET', 'POST'])  # Добавление клиента(собственника)
def new_client():
    form = NewClient()  # обращениек классу формы
    temp = 'new_client.html'  # имя шаблона
    title = 'Добавление клиента'  # заголовок страницы
    if form.validate_on_submit():
        message = chek_pasport(form.pasport.data)  # проверка корректности паспорта
        if message != '':
            return render_template(temp, title=title, form=form, message=message)

        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT FIO_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)  # запрос на наличие собственника в БД
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()

        if info_sobstvinn:
            return render_template(temp, title=title, form=form, message="Клиент с такими паспортными данными существует!")
        message = chek_data(form.data_birthday.data)  # проверка корректности введенной даты
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        message = chek_phone(form.phone.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        message = chek_fio(form.fio_sobstv.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        if len(form.fio_sobstv.data) > 40:
            return render_template(temp, title=title, form=form,
                                   message="В поле ФИО Собственника может быть не больше 40 символов! Просьба сократить инициалы!")
        if (form.gender.data.lower() != 'м') and (form.gender.data.lower() != 'ж'):
            return render_template(temp, title=title, form=form, message="Пол необходимо указать одной буквой: м/ж!")

        zapros = ('''WITH SRC AS (SELECT TOP (1) ID_Sobstv FROM Sobstv ORDER BY ID_Sobstv DESC)
                    SELECT ID_Sobstv FROM SRC ORDER BY ID_sobstv''')
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()
        id_for_new_sobstv = int(info_sobstvinn[0][0]) + 1
        sobstv = (form.fio_sobstv.data.strip()).split()
        fio_new_client = sobstv[0][0].upper() + sobstv[0][1::].lower() + ' ' + sobstv[1][0].upper() + sobstv[1][1::].lower()
        if len(sobstv) == 3:
            fio_new_client += ' ' + (sobstv[2][0].upper() + sobstv[2][1::].lower())
        zapros = ('''INSERT INTO Sobstv(ID_sobstv, Data_birthday, Phone, FIO_sobstv, Passport, Gender)
                    VALUES (%s, '%s', '%s', '%s', '%s', '%s')''' %
                  (id_for_new_sobstv, str(form.data_birthday.data), str(form.phone.data), str(fio_new_client),
                   str(form.pasport.data), str(form.gender.data).lower()))
        cursor.execute(zapros)
        connection.commit()
        return redirect("/new_flat")
    return render_template(temp, title=title, form=form)


@app.route("/new_flat", methods=['GET', 'POST'])  # Добавление квартиры
def new_flat():
    form = NewFlat()  # обращениек классу формы
    temp = 'new_flat.html'  # имя шаблона
    title = 'Добавление квартиры'  # заголовок страницы
    if form.validate_on_submit():
        if chek_bukv(form.gorod.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Город присутсвуют посторонние символы!")
        if chek_bukv(form.street.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Улица присутсвуют посторонние символы!")

        if chek_number(form.dom.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Номер дома присутсвуют посторонние символы!")
        if chek_number(str(form.dom.data)[0]) == False:
            return render_template(temp, title=title, form=form,
                                   message='В поле Номер дома присутствуют посторонние символы!')
        if str(form.dom.data)[0] == '.':
            return render_template(temp, title=title, form=form,
                                   message='В поле Номер дома присутствуют посторонние символы!')
        if str(form.dom.data)[0] == '0':
            render_template(temp, title=title, form=form,
                            message='Номер дома не может начинаться с 0!')

        if chek_number(form.id_flat.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Номер квартиры присутсвуют посторонние символы!")
        if chek_number(str(form.id_flat.data)[0]) == False:
            return render_template(temp, title=title, form=form,
                                   message='В поле Номер квартиры присутствуют посторонние символы!')
        if str(form.id_flat.data)[0] == '.':
            return render_template(temp, title=title, form=form,
                                   message='В поле Номер квартиры присутствуют посторонние символы!')
        if str(form.id_flat.data)[0] == '0':
            return render_template(temp, title=title, form=form, message='Номер квартиры не может начинаться с 0!')

        if chek_number(form.other_info.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Площадь квартиры присутсвуют посторонние символы!")
        if chek_number(str(form.other_info.data)[0]) == False:
            return render_template(temp, title=title, form=form,
                                   message='В поле Площадь квартиры присутствуют посторонние символы!')
        if str(form.other_info.data)[0] == '0':
            return render_template(temp, title=title, form=form, message='Площадь квартиры не может быть 0!')
        if len(form.other_info.data) > 4:
            return render_template(temp, title=title, form=form,
                                   message="В поле Площадь можно указать 4 символа!")
        if '.' in str(form.other_info.data):
            flat_sqr = (form.other_info.data).split('.')
            if len(flat_sqr) == 2:
                flat_sqr = '.'.join(flat_sqr)
            else:
                return render_template(temp, title=title, form=form,
                                       message='В поле Площадь можно использовать одну "."!')
        else:
            flat_sqr = form.other_info.data
        if (str(form.schetchik.data).lower() != 'да') and (str(form.schetchik.data).lower() != 'нет'):
            return render_template(temp, title=title, form=form,
                                   message="В поле Наличие счетчика необходимо написать да/нет!")
        if str(form.temperatura.data)[0] != '+' and str(form.temperatura.data)[0] != '-':
            return render_template(temp, title=title, form=form,
                                   message="В поле Температура необходимо указать +/- перед значением температуры!")
        if '.' in str(form.temperatura.data):
            temperatura = (form.temperatura.data).split('.')
            if len(temperatura) == 2:
                temperatura = '.'.join(temperatura)
            else:
                return render_template(temp, title=title, form=form,
                                       message='В поле Температура можно использовать одну "."!')
        else:
            temperatura = form.temperatura.data
        if len(temperatura.split('+')) > 2:
            return render_template(temp, title=title, form=form, message="Недопустимое значение температуры!")
        if len(temperatura.split('-')) > 2:
            return render_template(temp, title=title, form=form, message="Недопустимое значение температуры!")
        if len(temperatura) > 3:
            return render_template(temp, title=title, form=form, message="В поле температура можно писать не более 3 символов!")
        if '+' in temperatura:
            if '-' in temperatura:
                return render_template(temp, title=title, form=form, message="Недопустимое значение температуры!")
        if '-' in temperatura:
            if '+' in temperatura:
                return render_template(temp, title=title, form=form, message="Недопустимое значение температуры!")
        if float(temperatura) >= 100 or float(temperatura) <= -100:
            return render_template(temp, title=title, form=form, message="Недопустимое значение температуры!")
        zapros = ('''SELECT ID_company FROM Company WHERE(Company.Nazv=%s)''' % ("'" + form.company.data + "'"))
        cursor.execute(zapros)
        info_id_company = cursor.fetchall()
        if not info_id_company:
            return render_template(temp, title=title, form=form, message="Ошибка в названии обслуживающей компании!")
        zapros = ('''WITH SRC AS (SELECT TOP (1) ID_Sobstv FROM Sobstv ORDER BY ID_Sobstv DESC)
                            SELECT ID_Sobstv FROM SRC ORDER BY ID_sobstv''')
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()
        gorod = str(form.gorod.data).strip()
        street = str(form.street.data).strip()
        new_adress = 'г. ' + gorod[0].upper() + gorod[1::].lower() + ' ул. ' + street[0].upper() + street[1::].lower()
        + ' ' + str(form.dom.data) + ' кв. ' + str(form.id_flat.data)
        if len(new_adress) > 40:
            return render_template(temp, title=title, form=form, message="Число символов в адресе не должно привышать 40!"
                                                                         " Введите сокращенно поле город, улица!")
        zapros = ('''INSERT INTO Flat(ID_flat, Adress, Other_info, Temperatura, ID_sobstv, ID_company) 
        VALUES (%s, '%s', '%s', '%s', %s, %s)''' % (info_sobstvinn[0][0], str(new_adress), str(flat_sqr),
                                                    str(temperatura), info_sobstvinn[0][0], info_id_company[0][0]))
        cursor.execute(zapros)
        connection.commit()
        if int(form.temperatura.data) < 18:
            zapros = ('''INSERT INTO Lgot(ID_lgot, ID_sobstv, Discount) VALUES (%s, %s, %s);''' %
                      (info_sobstvinn[0][0], info_sobstvinn[0][0], "'10%'"))
            cursor.execute(zapros)
            connection.commit()
        if form.schetchik.data.lower() == 'нет':
            return redirect('/')
        elif form.schetchik.data.lower() == 'да':
            return redirect('/new_schetchik')
    return render_template(temp, title=title, form=form)


@app.route("/new_schetchik", methods=['GET', 'POST'])  # Добавление счетчика
def new_schetchik():
    form = NewSchetchik()  # обращениек классу формы
    temp = 'new_schetchik.html'  # имя шаблона
    title = 'Добавление счетчика'  # заголовок страницы
    if form.validate_on_submit():
        message = chek_data(form.date_ustanovk.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        if chek_bukv(form.firma.data) == False:
            return render_template(temp, title=title, form=form, message='В поле Фирма присутствуют посторонние символы!')
        if len(form.firma.data) == 25:
            return render_template(temp, title=title, form=form,
                                   message='В поле Фирма не может быть больше 25 символов! Введите с сокращением!')
        zapros = ('''WITH SRC AS (SELECT TOP (1) ID_flat FROM Flat ORDER BY ID_sobstv DESC)
                            SELECT ID_flat FROM SRC ORDER BY ID_flat''')
        cursor.execute(zapros)
        info_about_flat = int(cursor.fetchall()[0][0])
        zapros = ('''INSERT INTO Schetchik(ID_schetchik, ID_flat, Date_ustanovk, Firma) VALUES (%s, '%s', '%s', '%s')'''
                  % (info_about_flat, info_about_flat, str(form.date_ustanovk.data), str(form.firma.data)))
        cursor.execute(zapros)
        connection.commit()
        return redirect('/add_pokaz')
    return render_template(temp, title=title, form=form)


@app.route("/add_pokaz", methods=['GET', 'POST'])  # Добавление показаний счетчика
def add_pokaz():
    form = AddPokaz()  # обращениек классу формы
    temp = 'add_pokaz.html'  # имя шаблона
    title = 'Добавление показаний счетчик'  # заголовок страницы
    all_month = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь',
                 'октябрь', 'ноябрь', 'декабрь']
    if form.validate_on_submit():
        message = chek_pasport(form.pasport.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        if chek_number(form.pokaz.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Показания счетчика присутствуют посторонние символы!")
        if chek_number(str(form.pokaz.data)[0]) == False:
            return render_template(temp, title=title, form=form,
                                   message='В поле Показания счетчика посторонние символы!')
        if str(form.pokaz.data)[0] == '.':
            return render_template(temp, title=title, form=form,
                                   message='В поле Показания счетчика посторонние символы!')
        if str(form.pokaz.data)[0] == '0':
            render_template(temp, title=title, form=form,
                            message='Показания счетчика не могут начинаться с 0!')
        if len(form.pokaz.data) > 10:
            return render_template(temp, title=title, form=form,
                                   message='В поле Показания счетчика введено большое значение!')
        month_pokaz = 13
        for i in range(12):
            if form.month_pokaz.data.lower() == all_month[i]:
                month_pokaz = i+1
                break
        if month_pokaz == 13:
            return render_template(temp, title=title, form=form, message="Месяц показаний указан неверно!")

        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT ID_flat FROM Flat WHERE Flat.ID_sobstv = 
        (SELECT ID_sobstv FROM Sobstv WHERE(%s))''' % for_zapros)
        cursor.execute(zapros)
        about_client = cursor.fetchall()
        if about_client == []:
            return render_template(temp, title=title, form=form, message="Информация о данном собственнике не имеется!")

        zapros = ('''SELECT ID_schetchik FROM Schetchik WHERE Schetchik.ID_flat = %s''' % about_client[0][0])
        cursor.execute(zapros)
        id_schetchik = cursor.fetchall()
        if id_schetchik != []:
            zapros = ('''SELECT Month_pokaz FROM Pokaz WHERE Pokaz.ID_schetchik=%s''' % id_schetchik[0][0])
            cursor.execute(zapros)
            about_month = cursor.fetchall()
            if form.month_pokaz.data.lower() == str(about_month[0][0]).lower():
                return render_template(temp, title=title, form=form,
                                       message="Информация о показаниях за данный месяц имеются!!")

            id_pokaz = int(str(id_schetchik[0][0]) + '0' + str(month_pokaz))
            zapros = ('''INSERT INTO Pokaz(ID_pokaz, Adout_pokaz, ID_schetchik, Month_pokaz) VALUES (%s, '%s', '%s', '%s')'''
                      % (id_pokaz, str(form.pokaz.data), id_schetchik[0][0],
                         (str(form.month_pokaz.data)[0].upper() + str(form.month_pokaz.data)[1::].lower())))
            cursor.execute(zapros)
            connection.commit()
            return redirect('/')
        else:
            return render_template(temp, title=title, form=form,
                                   message="Информация о счетчике в данной квартире не имеется!")
    return render_template(temp, title=title, form=form)


@app.route("/change_pokaz", methods=['GET', 'POST'])  # Изменение показаний счетчика
def change_pokaz():
    form = ChangePokaz()
    temp = "change_pokaz.html"
    title = 'Изменение показаний счетчика'
    if form.validate_on_submit():
        message = chek_pasport(form.pasport.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)

        if chek_number(form.pokaz.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Показания счетчика присутствуют посторонние символы!")
        if chek_number(str(form.pokaz.data)[0]) == False:
            return render_template(temp, title=title, form=form,
                                   message='В поле Показания счетчика посторонние символы!')
        if str(form.pokaz.data)[0] == '.':
            return render_template(temp, title=title, form=form,
                                   message='В поле Показания счетчика посторонние символы!')
        if str(form.pokaz.data)[0] == '0':
            render_template(temp, title=title, form=form,
                            message='Показания счетчика не могут начинаться с 0!')
        if len(form.pokaz.data) > 10:
            return render_template(temp, title=title, form=form,
                                   message='В поле Показания счетчика введено большое значение!')

        all_month = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь',
                     'октябрь', 'ноябрь', 'декабрь']
        month_pokaz = 13
        for i in range(12):
            if form.month_pokaz.data.lower() == all_month[i]:
                month_pokaz = i + 1
                break
        if month_pokaz == 13:
            return render_template(temp, title=title, form=form, message="Месяц показаний указан неверно!")

        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT ID_flat FROM Flat WHERE Flat.ID_sobstv = 
        (SELECT ID_sobstv FROM Sobstv WHERE(%s))''' % for_zapros)
        cursor.execute(zapros)
        about_client = cursor.fetchall()
        if about_client == []:
            return render_template(temp, title=title, form=form, message="Информация о данном собственнике не имеется!")

        zapros = ('''SELECT ID_schetchik FROM Schetchik WHERE Schetchik.ID_flat = %s''' % about_client[0][0])
        cursor.execute(zapros)
        id_schetchik = cursor.fetchall()
        if id_schetchik != []:
            zapros = ('''SELECT Month_pokaz FROM Pokaz WHERE Pokaz.ID_schetchik=%s''' % id_schetchik[0][0])
            cursor.execute(zapros)
            about_month = cursor.fetchall()
            if form.month_pokaz.data.lower() != str(about_month[0][0]).lower():
                return render_template(temp, title=title, form=form,
                                       message="Информация о показаниях за данный месяц не имеются!")
            id_pokaz = int(str(id_schetchik[0][0]) + '0' + str(form.month_pokaz.data))
            zapros = ('''UPDATE Pokaz SET Adout_pokaz=%s WHERE (ID_schetchik=%s AND ID_pokaz=%s)'''
                      % (str(form.pokaz.data), id_schetchik[0][0], id_pokaz))
            cursor.execute(zapros)
            connection.commit()
            return redirect('/')
        else:
            return render_template(temp, title=title, form=form,
                                   message="Информация о счетчике в данной квартире не имеется!")
    return render_template(temp, title=title, form=form)


@app.route("/about_company")  # Информация о компании
def about_company():
    zapros = '''SELECT * FROM Company'''
    cursor.execute(zapros)
    info_all_company = cursor.fetchall()
    return render_template("about_company.html", title='Данные компании', all_company=info_all_company)


@app.route("/change_info_company", methods=['GET', 'POST'])  # Изменение информации о компании
def change_info_company():
    form = ChangeInfoCompany()  # обращениек классу формы
    temp = 'change_info_company.html'  # имя шаблона
    title = 'Изменение информации о компании'  # заголовок страницы
    if form.validate_on_submit():
        message = chek_bukv(form.nazv_old.data)
        if message == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Название присутсвуют посторонние символы!")
        for_zapros = "'" + str(form.nazv_old.data) + "'"
        zapros = ('''SELECT ID_company FROM Company WHERE Company.Nazv=%s''' % for_zapros)
        cursor.execute(zapros)
        company_id = cursor.fetchall()
        if company_id == []:
            return render_template(temp, title=title, form=form, message='Не найдена компания с таким названием!')
        if chek_number(form.tariff.data) == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Тариф присутсвуют посторонние символы!")
        if chek_number(str(form.tariff.data)[0]) == False:
            return render_template(temp, title=title, form=form,
                                   message='В поле Тариф присутствуют посторонние символы!')
        if str(form.tariff.data)[0] == '.':
            return render_template(temp, title=title, form=form,
                                   message='В поле Тариф присутствуют посторонние символы!')
        if str(form.tariff.data)[0] == '0':
            render_template(temp, title=title, form=form,
                            message='Тариф не может быть 0р.!')
        if float(form.tariff.data) > 70:
            render_template(temp, title=title, form=form,
                            message='Тариф не может быть дороже 70р.!')
        if '.' in str(form.tariff.data):
            company_tarif = (form.tariff.data).split('.')
            if len(company_tarif) == 2:
                company_tarif = '.'.join(company_tarif)
            else:
                return render_template(temp, title=title, form=form,
                                       message='В поле Тариф можно использовать одну "."!')
        else:
            company_tarif = form.tariff.data
        if '.' in form.recvizit.data:
            return render_template(temp, title=title, form=form, message='В поле Реквизиты присутсвуют посторонние символы!')
        if len(form.recvizit.data) != 20:
            return render_template(temp, title=title, form=form, message='В поле Реквизиты должно быть 20 цифра!')
        message = chek_number(form.recvizit.data)
        if message == False:
            return render_template(temp, title=title, form=form,
                                   message="В поле Название присутсвуют посторонние символы!")
        message = chek_fio(form.fio_ruck.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        if len(form.fio_ruck.data) > 40:
            return render_template(temp, title=title, form=form,
                                   message='В поле ФИО Руководителя может быть не больше 40 символов! Просьба сократить инициалы!')
        zapros = ('''UPDATE Company SET Tariff=%s, Recvizit='%s', FIO_Ruck='%s' WHERE Nazv=%s'''
                    % (company_tarif, form.recvizit.data, form.fio_ruck.data.strip(), for_zapros))
        cursor.execute(zapros)
        connection.commit()
        return redirect('/')
    return render_template(temp, title=title, form=form)


@app.route("/change_info_client", methods=['GET', 'POST'])  # Изменение информации о клиенте(собственнике)
def change_info_client():
    form = ChangeInfoClient()  # обращениек классу формы
    temp = 'change_info_client.html'  # имя шаблона
    title = 'Изменение информации о клиенте'  # заголовок страницы
    if form.validate_on_submit():
        message = chek_pasport(form.pasport_old.data)
        if message != '':
           return render_template(temp, title=title, form=form, message=message)
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport_old.data + "%'"
        zapros = ('''SELECT ID_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info_sobstvinn_id = cursor.fetchall()
        if not info_sobstvinn_id:
            return render_template(temp, title=title, form=form,
                                   message="Клиент с такими паспортными данными не существует!")
        message = chek_data(form.data_birthday.data)  # проверка корректности введенной даты
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        message = chek_phone(form.phone.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        message = chek_fio(form.fio_sobstv.data)
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        if len(form.fio_sobstv.data) > 40:
            return render_template(temp, title=title, form=form,
                                   message="В поле ФИО Собственника может быть не больше 40 символов! Просьба сократить инициалы!")
        if (form.gender.data.lower() != 'м') and (form.gender.data.lower() != 'ж'):
            return render_template(temp, title=title, form=form, message="Пол необходимо указать одной буквой: м/ж!")

        new_data_birthday = "'" + form.data_birthday.data + "'"
        new_phone = "'" + form.phone.data + "'"
        new_fio_sobstv = "'" + form.fio_sobstv.data + "'"
        new_pasport = "'" + form.pasport.data + "'"
        new_gender = "'" + form.gender.data + "'"
        zapros = ('''UPDATE Sobstv SET Data_birthday=%s, Phone=%s, FIO_sobstv=%s, Passport=%s, Gender=%s WHERE ID_sobstv=%s'''
                  % (new_data_birthday, new_phone, new_fio_sobstv, new_pasport, new_gender, str(info_sobstvinn_id[0][0])))
        cursor.execute(zapros)
        connection.commit()
        return redirect('/')
    return render_template(temp, title=title, form=form)


@app.route("/delete_client", methods=['GET', 'POST'])  # Удаление клиента(собственника)
def delete_client():
    form = DeleteClient()  # обращениек классу формы
    temp = 'delete_client.html'  # имя шаблона
    title = 'Удаление клиента'  # заголовок страницы
    if form.validate_on_submit():
        message = chek_pasport(form.pasport.data)  # проверка корректности паспорта
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT ID_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)  # запрос на наличие собственника в БД
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()

        if info_sobstvinn:
            # проверка наличия счетчиков
            zapros1 = ('''SELECT ID_flat FROM Flat WHERE Flat.ID_sobstv = %s''' % info_sobstvinn[0][0])
            cursor.execute(zapros1)
            id_flat_schetchik = cursor.fetchall()
            # удаление информации о счетчиках
            if id_flat_schetchik:
                for_zapros = "'" + str(id_flat_schetchik[0][0]) + "'"
                zapros = ('''DELETE FROM Pokaz WHERE ID_schetchik = %s''' % for_zapros)  # удаление показаний счетчика
                cursor.execute(zapros)
                connection.commit()

                zapros = ('''DELETE FROM Schetchik WHERE ID_flat = %s''' % for_zapros)  # удаление информации о счетчике
                cursor.execute(zapros)
                connection.commit()
            # удаление информаци о квартире
            zapros = ('''DELETE FROM Flat WHERE ID_flat = %s''' % info_sobstvinn[0][0])  # удаление инф-ции о квартире
            cursor.execute(zapros)
            connection.commit()

            zapros1 = ('''SELECT ID_lgot FROM Lgot WHERE Lgot.ID_sobstv = %s''' % info_sobstvinn[0][0])
            cursor.execute(zapros1)
            id_lgot = cursor.fetchall()
            # удаление информации о льготах
            if id_lgot:
                zapros = ('''DELETE FROM Lgot WHERE ID_sobstv = %s''' % id_lgot[0][0])
                cursor.execute(zapros)
                connection.commit()
            # удаление клиента(собственника)
            for_zapros = "'" + form.pasport.data + "'"
            zapros = ('''DELETE FROM Sobstv WHERE Passport = %s''' % for_zapros)  # удаление собственника (клиента)
            cursor.execute(zapros)
            connection.commit()
            return redirect('/')  # переход на основную страницу
        else:
            return render_template(temp, title=title, form=form,
                                   message='Клиент с такими паспортными данными не существует!')
    return render_template(temp, title=title, form=form)


@app.route("/about_client", methods=['GET', 'POST'])  # Информация о клиенте(собственнике)
def about_client():
    form = AboutClient()  # обращениек классу формы
    temp = 'about_client.html'  # имя шаблона
    title = 'Данные клиента'  # заголовок страницы
    if form.validate_on_submit():
        message = chek_pasport(form.pasport.data)  # проверка корректности паспорта
        if message != '':
            return render_template(temp, title=title, form=form, message=message)
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT FIO_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)  # запрос на наличие собственника в БД
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()

        if info_sobstvinn == []:  # проверка наличия собственника в БД
            message = "Клиент с такими паспортными данными не существует!"
            return render_template(temp, title=title, form=form, message=message)
        # запросы для получения информации о собственнике
        for_zapros = "'" + form.pasport.data + "'"
        zapros = ('''SELECT FIO_sobstv, Data_birthday, Phone, Passport, Gender FROM Sobstv WHERE Sobstv.Passport=%s'''
                  % for_zapros)
        cursor.execute(zapros)
        info = cursor.fetchall()[0]

        zapros = ('''SELECT ID_sobstv FROM Sobstv WHERE Sobstv.Passport=%s''' % for_zapros)
        cursor.execute(zapros)
        id_sobstv = cursor.fetchall()[0][0]

        for_zapros = "'" + str(id_sobstv) + "'"
        zapros = ('''SELECT Adress, Other_info FROM Flat WHERE Flat.ID_sobstv=%s''' % for_zapros)
        cursor.execute(zapros)
        info += cursor.fetchall()[0]

        zapros = ('''SELECT ID_flat FROM Flat WHERE Flat.ID_sobstv=%s''' % for_zapros)
        cursor.execute(zapros)
        id_flat = cursor.fetchall()[0][0]

        for_zapros = "'" + str(id_flat) + "'"
        zapros = ('''SELECT Date_ustanovk, Firma FROM Schetchik WHERE Schetchik.ID_flat=%s''' % for_zapros)
        cursor.execute(zapros)
        vrem = cursor.fetchall()
        if vrem:
            info += vrem[0]
        return render_template('info_client.html', title=info_sobstvinn[0][0], item=info, dlina=len(info))
    return render_template(temp, title=title, form=form)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
