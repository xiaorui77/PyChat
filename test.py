
import pymysql
import time

conn = pymysql.connect(host="127.0.0.1", user="root",password="",database="python",charset="utf8")
cursor = conn.cursor()  

sql = "SELECT * FROM `message` WHERE target = '%d' AND status = 0" %(4)
try:
    cursor.execute(sql)
    a = cursor.fetchall()
    
    result=[]
    for b in a:
        c = {}
        c['from']= b[1]
        c['data']= b[3].strftime("%Y-%m-%d %H:%M:%S")
        c['text']= b[4]
        result.append(c)


    print(result)


except:
    print("cuowu ")
    pass