# -*- coding: utf-8 -*- 
import telebot
import datetime
from bitrix24 import *

bitrix = 'https://b24-n58f892e05b44f.bitrix24.ru/rest/1/aq26z15x07t0jhox/profile/'

bot = telebot.TeleBot('1094315027:AAFR4nbVhTO5XUCCFXccZcKZzTVvKzSv_tg')
botlog = telebot.TeleBot('1115207301:AAHyP7JM3LLjltBgyDnZfIDloG5bKOimWOk')
logChatID = '270174742'
link = ''

def data_time():
    dt = datetime.datetime.now()
    h = dt.hour
    mi = dt.minute
    s = dt.second
    d = dt.day
    mo = dt.month
    y = dt.year
    str_dt = '[' + str(h) + ':' + str(mi) + ':' + str(s) + ' ' + str(d) + '.' + str(mo) + '.' + str(y) + ']'
    return str_dt

def AddLead(title, chatID, name, phone):
    log_check = ''
    check_phone = []
    bx24 = Bitrix24(bitrix)
    check_phone = bx24.callMethod('crm.duplicate.findbycomm',TYPE='PHONE', VALUES=[phone])
    str_dt = data_time()
    for i in check_phone:
        log_check = log_check + i
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
    botlog.send_message(logChatID, str_dt + ' ' + log_check)


def Parser(data, parse):
    if parse == 'phone':
        phone = ''
        for i in data:
            if i == '+':
                phone = phone + i
            elif i == '1':
                phone = phone + i
            elif i == '2':
                phone = phone + i
            elif i == '3':
                phone = phone + i
            elif i == '4':
                phone = phone + i
            elif i == '5':
                phone = phone + i
            elif i == '6':
                phone = phone + i
            elif i == '7':
                phone = phone + i
            elif i == '8':
                phone = phone + i
            elif i == '9':
                phone = phone + i
            elif i == '0':
                phone = phone + i
        return phone
    if parse == 'name':
        name = ''
        for i in data:
            if i != '+' and i != ' ' and i != '(' and i != ')' and i != '-' and i != '1' and i != '2' and i != '3' and i != '4' and i != '5' and i != '6' and i != '7' and i != '8' and i != '9'  and i != '0':
                name = name + i        
        return name

def checkLEAD(data):
    led = ''
    key_exists ='LEAD' in data
    if key_exists == 1:
        led = data['LEAD']
    return led

    
def checkCONTACT(data):
    CONTACT = ''
    key_exists ='CONTACT' in data
    if key_exists == 1:
        CONTACT = data['CONTACT']
    return CONTACT


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


@bot.message_handler(content_types=['text'])
def readTextForLead(message):
    phone = Parser(message.text, 'phone')
    name = Parser(message.text, 'name')
    if name == '':
        name = phone
    AddLead(message.text, message.chat.id, name, phone)
    
bot.polling()
