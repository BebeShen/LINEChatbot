import os
import sys
import datetime
import psycopg2
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", None)
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
def create_user_info(profile):
    if profile == None:
        return "Input insufficient"
    with conn.cursor() as cursor:
        command = "INSERT INTO public.user (state,line_id) VALUES(%s,%s)"
        cursor.execute(
                command,("initial",profile.user_id,)
            )
        conn.commit()
    return "Success"
def update_user_student_by_lineid(info):
    if "userId" not in info.keys():
        return "Need userId(line_id)" 
    with conn.cursor() as cursor:
        command = "UPDATE public.user SET student_number =  %s,student_password = %s,updated_at = %s WHERE line_id = %s"
        cursor.execute(
                command,(info['student_number'],info['student_password'],datetime.datetime.now(),info['userId'])
            )
        # print(datetime.datetime.now())
        conn.commit()
    return "Success"
def update_user_state_by_lineid(next_state,line_id):
    with conn.cursor() as cursor:
        command = "UPDATE public.user SET state =  %s,updated_at = %s WHERE line_id = %s"
        cursor.execute(
            command,(next_state,datetime.datetime.now(),line_id)
        )
        conn.commit()
def insert_url(classroom):
    with conn.cursor() as cursor:
        command = "INSERT INTO public.url (classroom) VALUES(%s)"
        cursor.execute(
            command,(classroom,)
        )
        conn.commit()
def update_url(classroom,url):
    with conn.cursor() as cursor:
        command = "UPDATE public.url SET url = %s WHERE classroom = %s"
        cursor.execute(
            command,(url,classroom,)
        )
        conn.commit()
def get_all_url():
    flex_msg = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents":  [
                {
                    "type": "text",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "text": "點名系統"
                },
                {
                    "type": "text",
                    "text": "請選擇要點名的教室",
                    "align": "center"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [],
            "flex": 0
        }
    }
    with conn.cursor() as cursor:
        command = "SELECT classroom FROM public.url"
        cursor.execute(
            command,
        )
        classrooms = cursor.fetchall()
        for classroom in classrooms:
            flex_msg['footer']['contents'].append(
               {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "postback",
                    "label": classroom[0],
                    "data": classroom[0],
                    "displayText": classroom[0]
                    }
                }
            )
        
        flex_msg['footer']['contents'].append(
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "postback",
                    "label": "上傳QRcode新增地點",
                    "data": "上傳QRcode新增地點",
                    "displayText": "上傳QRcode新增地點"
                }
            }
        )
        flex_msg['footer']['contents'].append(
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "postback",
                    "label": "取消",
                    "data": "取消",
                    "displayText": "取消"
                }
            }
        )
        flex_msg['footer']['contents'].append(
            {
                "type": "spacer",
                "size": "sm"
            }
        )
        return flex_msg
def get_url_by_room(classroom):
    with conn.cursor() as cursor:
        command = "SELECT url FROM public.url WHERE classroom = %s ORDER BY id ASC"
        cursor.execute(
            command,(classroom,)
        )
        result = cursor.fetchone()
        return result[0]
def get_all_classroom():
    with conn.cursor() as cursor:
        command = "SELECT classroom FROM public.url"
        cursor.execute(
            command,
        )
        result = cursor.fetchall()
        return result
def find_user_by_line_id(line_id):
    with conn.cursor() as cursor:
        command = "SELECT * FROM public.user WHERE line_id = %s ORDER BY id ASC"
        cursor.execute(
                command,(line_id,)
            )
        result = cursor.fetchone()
        # print(result)
        if result == None:
            return "Not found"
        keys = ['id', 'student_number', 'student_password','line_id','state','updated_at']
        return dict(zip(keys,result))
        # dict
        # ['id', 'student_number', 'student_password','line_id','state','fever','updated_at','symptoms']