import cv2
import face_recognition as fr
import numpy as np
import mysql.connector
import json
from io import StringIO
from datetime import date
import datetime
import pyperclip
import uuid
import os


#read image file
def read_file(path):
          images=os.listdir(path)
          return images
# images_of_users1=read_file('./images')
# print(images_of_users1)

#connect to myapp_db
def connect_db():
  mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="myapp_db"
  )
  return mydb

#convert encode array to json file for save in db
def save_as_json(content):
          b=content.tolist()
          a=json.dumps(b)
          return a

#insert into db: table log
def insert_db_log(user_id):
    id=get_last_id_from_db()[0]+1
    today = date.today()
    now = datetime.datetime.now()
    now=now.strftime("%X")
    uuid2=uuid.uuid1()
    uuid2=str(uuid2)
    print("Inserting into log table")
    try:
        connection = connect_db()

        cursor = connection.cursor()
        sql_insert_blob_query = """ INSERT INTO `logs`(`id`, `uuid`, `user_id`, `date`, `time`) 
                                     VALUES (%s,%s,%s,%s,%s)"""

        # Convert data into tuple format
        insert_blob_tuple = (id,uuid2,user_id,today,now)
        result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        connection.commit()
        print("Datas successfully into Log table", result)

    except mysql.connector.Error as error:
        print("Failed inserting data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            return uuid2
            # print("MySQL connection is closed")
            
#export last id from log table
def get_last_id_from_db():
    id=[]
    try:
            connection=connect_db()
            sql_select_Query = "SELECT id from `logs` order by date AND time desc limit 1"
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            # get all records
            record_id = cursor.fetchall()
            id.append(record_id[0][0])                  
            return id
                
    except mysql.connector.Error as error:
        print("Failed selecting last data into MySQL table {}".format(error))

print("_________________________")
#insert into db: table user
def insert_db(id,firstname,lastname,encode_face,job_title):
  
    print("Inserting into user table")
    try:
        connection = connect_db()

        cursor = connection.cursor()
        sql_insert_blob_query = """ INSERT INTO `user`(`id`, `first_name`, `last_name`,`face_encode`,`job_title`) 
                                     VALUES (%s,%s,%s,%s,%s)"""

        encode_face=save_as_json(encode_face)
        insert_blob_tuple = (id,firstname,lastname,encode_face,job_title)
        result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        connection.commit()
        print("Datas successfully into user table", result)

    except mysql.connector.Error as error:
        print("Failed inserting data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            
#encode faces
def encode_faces(img_path):
          image=fr.load_image_file(img_path)
          image_convert_color=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
          face_record=fr.face_encodings(image)[0]
          return face_record
      
# images_of_users=[]
# for image in images_of_users1:
#     images_of_users.append(encode_faces('./images/'+image))
# images_of_users=encode_faces('./images')
# print(images_of_users)
# a=encode_faces('./images/MinaIrv.jpg')

#load json as array
def save_as_arr(txtfile): 
          io = StringIO(txtfile)
          a=json.load(io)
          return a

#eport users from db
def get_data_from_db():
    images=[]
    data=[]
    try:
            connection=connect_db()
            sql_select_Query = "select * FROM `user`"
            cursor = connection.cursor()
            cursor.execute(sql_select_Query)
            # get all records
            records = cursor.fetchall()
            for row in records:
                data.append([row[0],row[1],row[2],row[4]])
                images.append(save_as_arr(row[3]))
                
            return images,data
                
    except mysql.connector.Error as error:
        print("Failed selecting BLOB data into MySQL table {}".format(error))

         
# insert_db(
#   3,
#   "DR_Ali",
#   "Azarpeivand",
#   images_of_users[0],
#   "Professor"
# )






user_images=get_data_from_db()[0]              
users=get_data_from_db()[1]


# colors
purple=(122,36,119)
light_blue=(229,208,75)
green=(126,229,75)
blue=(75,203,229)
red=(216,47,41)
pink=(204,0,127)

#open webcam
cap=cv2.VideoCapture(0)
while True:
    _,img=cap.read()
    img_copy=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    face_location=fr.face_locations(img_copy)
    color=red
    if len(face_location)>0:

        face_incode=fr.face_encodings(img_copy)[0]
        isSame=fr.compare_faces(user_images,face_incode)
        flag=False
        for same in range(0,len(isSame)):
          if(isSame[same]):
                    flag=True
                    color=light_blue
                    img=cv2.putText(img,
                              users[same][1]+"_"+users[same][2],
                              (face_location[0][3]-6,face_location[0][0]-6),
                              cv2.FONT_HERSHEY_SIMPLEX,
                              1.0,
                              color,
                              2
                              )  
                    # code=insert_db_log(temp,users[same][0]) 
                    break
        if(not flag):
                    cv2.putText(img,
                              'unknown',
                              (face_location[0][1]-6,face_location[0][2]-6),
                              cv2.FONT_HERSHEY_COMPLEX,
                              1.0,
                              color,
                              1
                              )
        img=cv2.rectangle(img,
            (face_location[0][3],face_location[0][0]),
            (face_location[0][1],face_location[0][2]),
            color,
            3)
    cv2.imshow('image',img)

    
    if cv2.waitKey(1) & 0xff== ord('q'):
        if(flag):
            code=insert_db_log(users[same][0]) 
        break
# web camera off
cap.release()
cv2.destroyAllWindows()


   