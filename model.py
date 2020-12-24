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
        command = "INSERT INTO public.user (state,line_id, symptoms_check) VALUES(%s,%s,%s)"
        cursor.execute(
                command,("initial",profile.user_id,"0",)
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
def insert_url(classroom,url):
    with conn.cursor() as cursor:
        command = "INSERT INTO public.url (classroom, url) VALUES(%s,%s)"
        cursor.execute(
            command,(classroom,url,)
        )
        conn.commit()
def get_url_by_room(classroom):
    with conn.cursor() as cursor:
        command = "SELECT url FROM public.url WHERE classroom = %s ORDER BY id ASC"
        cursor.execute(
            command,(classroom,)
        )
        result = cursor.fetchone()[0]
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
        keys = ['id', 'student_number', 'student_passwod','line_id','state','symptoms_check']
        return dict(zip(keys,result))
        # dict
        # ['id', 'student_number', 'student_password','line_id','state','symptoms_check']
