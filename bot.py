# -*- coding: utf-8 -*-
import telebot
import datetime
import sqlite3
from bitrix24 import *

def get_db(table, search):
	db = sqlite3.connect("/root/botbitrix/bot.db")
	cur = db.cursor()
	if table == 'bot':
		sql = "SELECT webhook FROM bot WHERE title=" + "'" + search + "'"
	if table == 'bots':
		sql = "SELECT token FROM bots WHERE name=" + "'" + search + "'"
	cur.execute(sql)
	result = cur.fetchone()
	db.close()
	for i in result:
		res_return = i
	return res_return

bitrix_webhook = get_db('bot','Dad')
bot = telebot.TeleBot(get_db('bots','Dad'))
botlog = telebot.TeleBot(get_db('bots','Log'))
logChatID = '270174742'
phone_parse = ['+','1','2','3','4','5','6','7','8','9','0']
name_parse = ['Ц','К','Е','Н','Г','Ш','Щ','З','Х','Ф','В','А','П','Р','О','Л','Д','Ж','Э','Я','Ч','С','М','И','Т','Б','Ю','Ё']

#Перевод даты и времени из dictionary в string
def data_time_str():
    dt = datetime.datetime.now()
    h = dt.hour
    mi = dt.minute
    s = dt.second
    d = dt.day
    mo = dt.month
    y = dt.year
    str_dt = '[' + str(h) + ':' + str(mi) + ':' + str(s) + ' ' + str(d) + '.' + str(mo) + '.' + str(y) + ']'
    return str_dt

#Добавление лида и вывод отладочной информации
def AddLead(title, chatID, name, phone):
    log_check = ''
    check_phone = []
    bx24 = Bitrix24(bitrix_webhook)
    check_phone = bx24.callMethod('crm.duplicate.findbycomm',TYPE='PHONE', VALUES=[phone])
    for i in check_phone:
        log_check = log_check + i + ' '
    if check_phone == []:
        bx24.callMethod('crm.lead.add', fields={'TITLE':title,'PHONE':[{'VALUE':('+'+phone)}]})
#        bx24.callMethod('crm.contact.add', fields={'NAME':name,'PHONE':[{'VALUE':('+'+phone)}]})
    else:
        if checkLEAD(check_phone) !='' and checkCONTACT(check_phone) !='':
            bot.send_message(chatID, 'Данный клиент (' + phone + ' ' + name + ') уже присутствует в базе. За лид ответственный: ' + findResponsible(phone, bx24, 'lead') + '. За контакт ответственный: ' + findResponsible(phone, bx24, 'contact') + '.')
        elif checkLEAD(check_phone) !='' and checkCONTACT(check_phone) =='':
            bot.send_message(chatID, 'Данный клиент (' + phone + ' ' + name + ') уже присутствует в базе. За лид ответственный: ' + findResponsible(phone, bx24, 'lead') + '.')
        elif checkLEAD(check_phone) =='' and checkCONTACT(check_phone) !='':
            bot.send_message(chatID, 'Данный клиент (' + phone + ' ' + name + ') уже присутствует в базе. За контакт ответственный: ' + findResponsible(phone, bx24, 'contact') + '.')
    botlog.send_message(logChatID, data_time_str() + ' ' + log_check)

#Парсер телефона и имени клиента
def Parser(data, parse):
    if parse == 'phone':
        phone = ''
        for i in data:
            for j in phone_parse:
                if i == j:
                    phone = phone + i
        return phone
    if parse == 'name':
        check = 'false'
        name = ''
        for i in data:
            if check == 'false':
                for j in name_parse:
                    if i == j:
                        check = 'true'
                        name = name + i
                        break
            elif check == 'true':
                name = name + i
        check = 'false'
        return name

#Проверка лида
def checkLEAD(data):
    led = ''
    key_exists ='LEAD' in data
    if key_exists == 1:
        led = data['LEAD']
    return led

#Проверка контакта
def checkCONTACT(data):
    CONTACT = ''
    key_exists ='CONTACT' in data
    if key_exists == 1:
        CONTACT = data['CONTACT']
    return CONTACT

#Функция поиска ответсвенного
def findResponsible(data, bx24, find):
    id_user = ''
    name = ''
    if find == 'contact':
        search = bx24.callMethod('crm.contact.list',filter={'PHONE': data}, select=["ASSIGNED_BY_ID"])
    elif find == 'lead':
        search = bx24.callMethod('crm.lead.list',filter={'PHONE': data}, select=["ASSIGNED_BY_ID"])   
    for i in search:
        for j in i:
            id_user = i['ASSIGNED_BY_ID']
            break
    if id_user == '':
        name = 'Не задан'
    else:
        buf = bx24.callMethod('user.get', filter={"ID": id_user});
        for i in buf:
            for j in i:
                name = i['NAME']
                key_exists = 'LAST_NAME' in i
                if key_exists == 1:
                    name = name + ' ' + i['LAST_NAME']
                break
    return name

#Обработка полученных сообщений
@bot.message_handler(content_types=['text'])
def readTextForLead(message):
    phone = Parser(message.text, 'phone')
    name = Parser(message.text, 'name')
    AddLead(message.text, message.chat.id, name, phone)
    
bot.polling()


