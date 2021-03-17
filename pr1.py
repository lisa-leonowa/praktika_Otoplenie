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
    fio_sobstv = StringField('ФИО Собственник:а', validators=[DataRequired()])
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
    app.run(port=8172, host='127.0.0.1')


def chek_number(slovo):
    for i in str(slovo):
        if i not in spisok:
            if i != '.':
                return False


def chek_bukv(slovo):
    for i in str(slovo).lower():
        if (i != ' ') and (i != '-'):
            if i not in spisok_buk:
                return False


@app.route("/itog", methods=['GET', 'POST'])
def itog():
    form = Pay()
    if form.validate_on_submit():
        if len(form.pasport.data) != 10:
            return render_template("itog.html", title='Создание квитанции', form=form,
                                   message="Неверное число символов в серии и номере старого паспорта!")
        else:
            if chek_number(str(form.pasport.data)) == False:
                return render_template("itog.html", title='Создание квитанции', form=form,
                                       message="В поле серия и номер старого паспорта присутствуют посторонние символы!")
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT ID_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info_sobstvinn_id = cursor.fetchall()
        if not info_sobstvinn_id:
            return render_template("itog.html", title='Создание квитанции', form=form,
                                   message="Клиент с такими паспортными данными не существует!")
        if len(form.data_pay.data) == 10:  # проверка длинны введенной даты
            vrem = form.data_pay.data.split('.')
            if len(vrem) == 3:  # проверка формата ввода
                if (len(vrem[0]) != 4) or (len(vrem[1]) != 2) or (len(vrem[2]) != 2):
                    return render_template("itog.html", title='Создание квитанции', form=form,
                                           message="Неверный формат, введите по формату ГГГГ.ММ.ДД")
                else:
                    if 0 > int(vrem[1]) or int(vrem[1]) > 12:  # проверка корректности введенного месяца
                        return render_template("itog.html", title='Создание квитанции', form=form,
                                               message="Неверно введен месяц, введите по формату ГГГГ.ММ.ДД")
                    else:  # проверка числа дней в месяце
                        mes = int(vrem[1])
                        day = int(vrem[2])
                        spisok_day_mes = [31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                        if mes == 2:
                            if int(vrem[0]) // 4 == 0:
                                if day > 29:
                                    return render_template("itog.html", title='Создание квитанции', form=form,
                                                           message="Количество дней превышает допустимое в месяце!")
                            else:
                                if day > 28:
                                    return render_template("itog.html", title='Создание квитанции', form=form,
                                                           message="Количество дней превышает допустимое в месяце!")
                        else:
                            if day > spisok_day_mes[mes - 1]:
                                return render_template("itog.html", title='Создание квитанции', form=form,
                                                       message="Количество дней превышает допустимое в месяце!")
                if chek_number(form.data_pay.data) == False:
                    return render_template("itog.html", title='Создание квитанции', form=form,
                                           message="В введенной дате имеются буквы!")
            else:
                return render_template("itog.html", title='Создание квитанции', form=form,
                                       message="Введите дату через точку! (ГГГГ.ММ.ДД)")
        else:
            return render_template("itog.html", title='Создание квитанции', form=form,
                                   message="Неверное число символов в дате рождения!")
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
    return render_template("itog.html", title='Создание квитанции', form=form)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("base.html", title='Учет платы за отопление')


@app.route("/new_client", methods=['GET', 'POST'])
def new_client():
    form = NewClient()
    if form.validate_on_submit():
        if len(form.pasport.data) != 10:
            return render_template("new_client.html", title='Удаление клиента', form=form,
                                   message="Неверное число символов в серии и номере паспорта!")
        else:
            if chek_number(str(form.pasport.data)) == False:
                return render_template("new_client.html", title='Удаление клиента', form=form,
                                       message="В поле серия и номер паспорта присутствуют посторонние символы!")
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT FIO_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()
        if info_sobstvinn:
            return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                   message="Клиент с такими паспортными данными существует!")
        if len(form.data_birthday.data) == 10:  # проверка длинны введенной даты
            vrem = form.data_birthday.data.split('.')
            if len(vrem) == 3:  # проверка формата ввода
                if (len(vrem[0]) != 4) or (len(vrem[1]) != 2) or (len(vrem[2]) != 2):
                    return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                           message="Неверный формат, введите по формату ГГГГ.ММ.ДД")
                else:
                    if 0 > int(vrem[1]) or int(vrem[1]) > 12:  # проверка корректности введенного месяца
                        return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                               message="Неверно введен месяц, введите по формату ГГГГ.ММ.ДД")
                    else:  # проверка числа дней в месяце
                        mes = int(vrem[1])
                        day = int(vrem[2])
                        spisok_day_mes = [31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                        if mes == 2:
                            if int(vrem[0]) // 4 == 0:
                                if day > 29:
                                    return render_template("new_client.html", title='Добавление нового клиента',
                                                           form=form,
                                                           message="Количество дней превышает допустимое в месяце!")
                            else:
                                if day > 28:
                                    return render_template("new_client.html", title='Добавление нового клиента',
                                                           form=form,
                                                           message="Количество дней превышает допустимое в месяце!")
                        else:
                            if day > spisok_day_mes[mes - 1]:
                                return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                                       message="Количество дней превышает допустимое в месяце!")
                if chek_number(form.data_birthday.data) == False:
                    return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                           message="В введенной дате имеются буквы!")
            else:
                return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                       message="Введите дату через точку! (ГГГГ.ММ.ДД)")
        else:
            return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                   message="Неверное число символов в дате рождения!")
        if form.phone.data[0] != '+':
            return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                   message="Номер телефона начинается с не с +7!")
        elif len(form.phone.data) == 12:
            if chek_number(form.phone.data[1::]) == False:
                return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                       message="В номере телефона присутствуют посторонние символы!")
        else:
            return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                   message="Неверное число символов в номере телефона!")
        sobstv = form.fio_sobstv.data.split()
        if 4 > len(sobstv) > 1:
            if chek_bukv(form.fio_sobstv.data) == False:
                return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                       message="В поле ФИО Собственника присутсвуют посторонние символы!")
        else:
            return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                   message="В поле ФИО Собственника указаны не все данные!")
        if (form.gender.data != 'м') and (form.gender.data != 'ж'):
            return render_template("new_client.html", title='Добавление нового клиента', form=form,
                                   message="Пол необходимо указать одной буквой: м/ж!")
        zapros = ('''WITH SRC AS (SELECT TOP (1) ID_Sobstv FROM Sobstv ORDER BY ID_Sobstv DESC)
                    SELECT ID_Sobstv FROM SRC ORDER BY ID_sobstv''')
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()
        id_for_new_sobstv = int(info_sobstvinn[0][0]) + 1
        fio_new_client = sobstv[0][0].upper() + sobstv[0][1::].lower() + ' ' + sobstv[1][0].upper() + sobstv[1][1::].lower()
        if len(sobstv) == 3:
            fio_new_client += ' ' + (sobstv[2][0].upper() + sobstv[2][1::].lower())
        zapros = ('''INSERT INTO Sobstv(ID_sobstv, Data_birthday, Phone, FIO_sobstv, Passport, Gender)
                    VALUES (%s, '%s', '%s', '%s', '%s', '%s')''' % (id_for_new_sobstv, str(form.data_birthday.data),
                                                                    str(form.phone.data), str(fio_new_client),
                                                                    str(form.pasport.data), str(form.gender.data).lower()))
        cursor.execute(zapros)
        connection.commit()
        return redirect("/new_flat")
    return render_template("new_client.html", title='Добавление нового клиента', form=form)


@app.route("/new_flat", methods=['GET', 'POST'])
def new_flat():
    form = NewFlat()
    if form.validate_on_submit():
        if chek_bukv(form.gorod.data) == False:
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="В поле Город присутсвуют посторонние символы!")
        if chek_bukv(form.street.data) == False:
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="В поле Улица присутсвуют посторонние символы!")
        if chek_number(form.dom.data) == False:
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="В поле Номер дома присутсвуют посторонние символы!")
        if chek_number(form.id_flat.data) == False:
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="В поле Номер квартиры присутсвуют посторонние символы!")
        if chek_number(form.other_info.data) == False:
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="В поле Площадь квартиры присутсвуют посторонние символы!")
        if (str(form.schetchik.data).lower() != 'да') and (str(form.schetchik.data).lower() != 'нет'):
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="В поле Наличие счетчика необходимо написать да/нет!")
        if str(form.temperatura.data)[0] != '+' or str(form.temperatura.data)[0] != '+':
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="В поле Температура необходимо указать +/- перед значением температуры!")
        if int(form.temperatura.data) >= 100 or int(form.temperatura.data) <= -100:
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="Недопустимое значение температуры!")
        zapros = ('''SELECT ID_company FROM Company WHERE(Company.Nazv=%s)''' % ("'" + form.company.data + "'"))
        cursor.execute(zapros)
        info_id_company = cursor.fetchall()
        if not info_id_company:
            return render_template("new_flat.html", title='Добавление новой квартиры', form=form,
                                   message="Ошибка в названии обслуживающей компании!")
        zapros = ('''WITH SRC AS (SELECT TOP (1) ID_Sobstv FROM Sobstv ORDER BY ID_Sobstv DESC)
                            SELECT ID_Sobstv FROM SRC ORDER BY ID_sobstv''')
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()
        new_adress = 'г. ' + str(form.gorod.data)[0].upper() + str(form.gorod.data)[1::].lower() + ' ул. ' +\
                     str(form.street.data)[0].upper() + str(form.street.data)[1::].lower() + ' ' + str(form.dom.data) \
                     + ' кв. ' + str(form.id_flat.data)
        zapros = ('''INSERT INTO Flat(ID_flat, Adress, Other_info, Temperatura, ID_sobstv, ID_company)  
        VALUES (%s, '%s', '%s', '%s', %s, %s)''' % (info_sobstvinn[0][0], str(new_adress), str(form.other_info.data),
                                                      form.temperatura.data, info_sobstvinn[0][0], info_id_company[0][0]))
        print(zapros)
        cursor.execute(zapros)
        connection.commit()
        print(zapros)
        if int(form.temperatura.data) < 18:
            zapros = ('''INSERT INTO Lgot(ID_lgot, ID_sobstv, Discount) VALUES (%s, %s, %s);''' %
                      (info_sobstvinn[0][0], info_sobstvinn[0][0], "'10%'"))
            cursor.execute(zapros)
            connection.commit()
        if form.schetchik.data.lower() == 'нет':
            return redirect('/')
        elif form.schetchik.data.lower() == 'да':
            return redirect('/new_schetchik')
    return render_template("new_flat.html", title='Добавление новой квартиры', form=form)


@app.route("/new_schetchik", methods=['GET', 'POST'])
def new_schetchik():
    form = NewSchetchik()
    if form.validate_on_submit():
        if len(form.date_ustanovk.data) == 10:  # проверка длинны введенной даты
            vrem = form.date_ustanovk.data.split('.')
            if len(vrem) == 3:  # проверка формата ввода
                if (len(vrem[0]) != 4) or (len(vrem[1]) != 2) or (len(vrem[2]) != 2):
                    return render_template("new_schetchik.html", title='Добавление нового счетчика', form=form,
                                           message="Неверный формат, введите по формату ГГГГ.ММ.ДД")
                else:
                    if 0 > int(vrem[1]) or int(vrem[1]) > 12:  # проверка корректности введенного месяца
                        return render_template("new_schetchik.html", title='Добавление нового счетчика', form=form,
                                               message="Неверно введен месяц, введите по формату ГГГГ.ММ.ДД")
                    else:  # проверка числа дней в месяце
                        mes = int(vrem[1])
                        day = int(vrem[2])
                        spisok_day_mes = [31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                        if mes == 2:
                            if int(vrem[0]) // 4 == 0:
                                if day > 29:
                                    return render_template("new_schetchik.html", title='Добавление нового счетчика',
                                                           form=form,
                                                           message="Количество дней превышает допустимое в месяце!")
                            else:
                                if day > 28:
                                    return render_template("new_schetchik.html", title='Добавление нового счетчика',
                                                           form=form,
                                                           message="Количество дней превышает допустимое в месяце!")
                        else:
                            if day > spisok_day_mes[mes - 1]:
                                return render_template("new_schetchik.html", title='Добавление нового счетчика',
                                                       form=form,
                                                       message="Количество дней превышает допустимое в месяце!")
                if chek_number(form.date_ustanovk.data) == False:
                    return render_template("new_schetchik.html", title='Добавление нового счетчика', form=form,
                                           message="В введенной дате имеются буквы!")
            else:
                return render_template("new_schetchik.html", title='Добавление нового счетчика', form=form,
                                       message="Введите дату через точку! (ГГГГ.ММ.ДД)")
        else:
            return render_template("new_schetchik.html", title='Добавление нового счетчика', form=form,
                                   message="Неверное число символов в дате рождения!")
        zapros = ('''WITH SRC AS (SELECT TOP (1) ID_flat FROM Flat ORDER BY ID_sobstv DESC)
                            SELECT ID_flat FROM SRC ORDER BY ID_flat''')
        cursor.execute(zapros)
        info_about_flat = int(cursor.fetchall()[0][0])
        zapros = ('''INSERT INTO Schetchik(ID_schetchik, ID_flat, Date_ustanovk, Firma) VALUES (%s, '%s', '%s', '%s')'''
                  % (info_about_flat, info_about_flat, str(form.date_ustanovk.data), str(form.firma.data)))
        cursor.execute(zapros)
        connection.commit()
        return redirect('/add_pokaz')
    return render_template("new_schetchik.html", title='Добавление нового счетчика', form=form)


@app.route("/add_pokaz", methods=['GET', 'POST'])
def add_pokaz():
    form = AddPokaz()
    if form.validate_on_submit():
        if len(form.pasport.data) != 10:
            return render_template("add_pokaz.html", title='Добавление показаний счетчика', form=form,
                                   message="Неверное число символов в серии и номере паспорта!")
        else:
            if chek_number(str(form.pasport.data)) == False:
                return render_template("add_pokaz.html", title='Добавление показаний счетчика', form=form,
                                       message="В поле серия и номер паспорта присутствуют посторонние символы!")
        if chek_number(form.pokaz.data) == False:
            return render_template("add_pokaz.html", title='Добавление показаний счетчика', form=form,
                                   message="В поле Показания счетчика присутствуют посторонние символы!")
        all_month = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь',
                     'октябрь', 'ноябрь', 'декабрь']
        month_pokaz = 13
        for i in range(12):
            if form.month_pokaz.data.lower() == all_month[i]:
                month_pokaz = i+1
                break
        if month_pokaz == 13:
            return render_template("add_pokaz.html", title='Добавление показаний счетчика', form=form,
                                   message="Месяц показаний указан неверно!")
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT ID_flat FROM Flat WHERE Flat.ID_sobstv = 
        (SELECT ID_sobstv FROM Sobstv WHERE(%s))''' % for_zapros)
        cursor.execute(zapros)
        id_schetchik = cursor.fetchall()[0][0]

        zapros = ('''SELECT ID_schetchik FROM Schetchik WHERE Schetchik.ID_flat = %s''' % id_schetchik)
        cursor.execute(zapros)
        uslovie = cursor.fetchall()

        if uslovie:
            id_pokaz = int(str(id_schetchik) + '0' + str(month_pokaz))
            zapros = ('''INSERT INTO Pokaz(ID_pokaz, Adout_pokaz, ID_schetchik, Month_pokaz) VALUES (%s, '%s', '%s', '%s')'''
                      % (id_pokaz, str(form.pokaz.data), id_schetchik, (str(form.month_pokaz.data)[0].upper() + str(form.month_pokaz.data)[1::].lower())))
            cursor.execute(zapros)
            connection.commit()
            return redirect('/')
        else:
            return render_template("add_pokaz.html", title='Добавление показаний счетчика', form=form,
                                   message="Информация о счетчике в данной квартире не имеется!")
    return render_template("add_pokaz.html", title='Добавление показаний счетчика', form=form)


@app.route("/change_info_client", methods=['GET', 'POST'])
def change_info_client():
    form = ChangeInfoClient()
    if form.validate_on_submit():
        if len(form.pasport_old.data) != 10:
            return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                   message="Неверное число символов в серии и номере старого паспорта!")
        else:
            if chek_number(str(form.pasport_old.data)) == False:
                return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                       message="В поле серия и номер старого паспорта присутствуют посторонние символы!")
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport_old.data + "%'"
        zapros = ('''SELECT ID_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info_sobstvinn_id = cursor.fetchall()
        if not info_sobstvinn_id:
            return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                   message="Клиент с такими паспортными данными не существует!")
        if len(form.data_birthday.data) == 10:  # проверка длинны введенной даты
            vrem = form.data_birthday.data.split('.')
            if len(vrem) == 3:  # проверка формата ввода
                if (len(vrem[0]) != 4) or (len(vrem[1]) != 2) or (len(vrem[2]) != 2):
                    return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                           message="Неверный формат, введите по формату ГГГГ.ММ.ДД")
                else:
                    if 0 > int(vrem[1]) or int(vrem[1]) > 12:  # проверка корректности введенного месяца
                        return render_template("change_info_client.html", title='Изменение информации о клиенте',
                                               form=form, message="Неверно введен месяц, введите по формату ГГГГ.ММ.ДД")
                    else:  # проверка числа дней в месяце
                        mes = int(vrem[1])
                        day = int(vrem[2])
                        spisok_day_mes = [31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                        if mes == 2:
                            if int(vrem[0]) // 4 == 0:
                                if day > 29:
                                    return render_template("change_info_client.html", title='Изменение информации о клиенте',
                                                           form=form, message="Количество дней превышает допустимое в месяце!")
                            else:
                                if day > 28:
                                    return render_template("change_info_client.html", title='Изменение информации о клиенте',
                                                           form=form, message="Количество дней превышает допустимое в месяце!")
                        else:
                            if day > spisok_day_mes[mes - 1]:
                                return render_template("change_info_client.html", title='Изменение информации о клиенте',
                                                       form=form, message="Количество дней превышает допустимое в месяце!")
                if chek_number(form.data_birthday.data) == False:
                    return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                           message="В введенной дате имеются буквы!")
            else:
                return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                       message="Введите дату через точку! (ГГГГ.ММ.ДД)")
        else:
            return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                   message="Неверное число символов в дате рождения!")
        if form.phone.data[0] != '+':
            return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                   message="Номер телефона начинается с не с +7!")
        elif len(form.phone.data) == 12:
            if chek_number(form.phone.data[1::]) == False:
                return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                       message="В номере телефона присутствуют посторонние символы!")
        else:
            return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                   message="Неверное число символов в номере телефона!")
        if len(form.pasport.data) != 10:
            return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                   message="Неверное число символов в серии и номере паспорта!")
        else:
            if chek_number(str(form.pasport.data)) == False:
                return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                       message="В поле серия и номер паспорта присутствуют посторонние символы!")
        if (form.gender.data != 'м') and (form.gender.data != 'ж'):
            return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form,
                                   message="Пол необходимо указать одной буквой: м/ж!")

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
    return render_template("change_info_client.html", title='Изменение информации о клиенте', form=form)


@app.route("/delete_client", methods=['GET', 'POST'])
def delete_client():
    form = DeleteClient()
    if form.validate_on_submit():
        if len(form.pasport.data) != 10:
            return render_template("delete_client.html", title='Удаление клиента', form=form,
                                   message="Неверное число символов в серии и номере паспорта!")
        else:
            if chek_number(str(form.pasport.data)) == False:
                return render_template("delete_client.html", title='Удаление клиента', form=form,
                                       message="В поле серия и номер паспорта присутствуют посторонние символы!")
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT ID_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()
        if info_sobstvinn:  # удаление существуещего в БД клиента
            zapros1 = ('''SELECT ID_flat FROM Flat WHERE Flat.ID_sobstv = %s''' % info_sobstvinn[0][0])
            cursor.execute(zapros1)
            id_flat_schetchik = cursor.fetchall()

            if id_flat_schetchik:
                for_zapros = "'" + str(id_flat_schetchik[0][0]) + "'"
                zapros = ('''DELETE FROM Pokaz WHERE ID_schetchik = %s''' % for_zapros)  # удаление показаний счетчика
                cursor.execute(zapros)
                connection.commit()

                zapros = ('''DELETE FROM Schetchik WHERE ID_flat = %s''' % for_zapros)  # удаление информации о счетчике
                cursor.execute(zapros)
                connection.commit()
            zapros = ('''DELETE FROM Flat WHERE ID_flat = %s''' % info_sobstvinn[0][0])  # удаление информации о квартире
            cursor.execute(zapros)
            connection.commit()

            zapros1 = ('''SELECT ID_lgot FROM Lgot WHERE Lgot.ID_sobstv = %s''' % info_sobstvinn[0][0])
            cursor.execute(zapros1)
            id_lgot = cursor.fetchall()
            if id_lgot:
                zapros = ('''DELETE FROM Lgot WHERE ID_sobstv = %s''' % id_lgot[0][0])
                cursor.execute(zapros)
                connection.commit()

            for_zapros = "'" + form.pasport.data + "'"
            zapros = ('''DELETE FROM Sobstv WHERE Passport = %s''' % for_zapros)  # удаление собственника (клиента)
            cursor.execute(zapros)
            connection.commit()
            return redirect('/')
        else:
            return render_template("delete_client.html", title='Удаление клиента', form=form,
                                   message="Клиент с такими паспортными данными не существует!")
    return render_template("delete_client.html", title='Удаление клиента', form=form)


@app.route("/about_client", methods=['GET', 'POST'])
def about_client():
    form = AboutClient()
    if form.validate_on_submit():
        if len(form.pasport.data) != 10:
            return render_template("about_client.html", title='Данные клиента', form=form,
                                   message="Неверное число символов в серии и номере старого паспорта!")
        else:
            if chek_number(str(form.pasport.data)) == False:
                return render_template("about_client.html", title='Данные клиента', form=form,
                                       message="В поле серия и номер старого паспорта присутствуют посторонние символы!")
        for_zapros = "Sobstv.Passport LIKE'%" + form.pasport.data + "%'"
        zapros = ('''SELECT FIO_sobstv FROM Sobstv WHERE(%s);''' % for_zapros)
        cursor.execute(zapros)
        info_sobstvinn = cursor.fetchall()
        if not info_sobstvinn:
            return render_template("about_client.html", title='Данные клиента', form=form,
                                   message="Клиент с такими паспортными данными не существует!")
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
    return render_template("about_client.html", title='Данные клиента', form=form)


@app.route("/about_company")
def about_company():
    zapros = '''SELECT * FROM Company'''
    cursor.execute(zapros)
    info_all_company = cursor.fetchall()
    return render_template("about_company.html", title='Данные компании', all_company=info_all_company)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
