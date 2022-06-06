import pymysql
import os

rds_host = os.environ.get("rds_host")
rds_password = os.environ.get("rds_password")
rds_id = os.environ.get("rds_id")


class Repository:
    def getPress(self):
        ret = []
        db = pymysql.connect(host=rds_host, user=rds_id, db='seear', password=rds_password, charset='utf8')
        curs = db.cursor()
        sql = "select * from press";
        curs.execute(sql)
        rows = curs.fetchall()
        cnt=0
        for e in rows:
            ret.append(e[2])
            cnt=cnt+1
        db.commit()
        db.close()
        return ret

    def getArticles(self):
        ret = []
        db = pymysql.connect(host=rds_host, user=rds_id, db='seear', password=rds_password, charset='utf8')
        curs = db.cursor()
        sql = "select * from articles ORDER BY id DESC LIMIT 1";
        curs.execute(sql)
        rows = curs.fetchall()
        db.commit()
        db.close()
        return rows[0][1]

    def insertPress(self,name,number):
        db = pymysql.connect(host=rds_host, user=rds_id, db='seear', password=rds_password, charset='utf8')
        curs = db.cursor()
        sql = '''insert into press (name, number) values(%s,%s)'''
        curs.execute(sql, (name,number))
        db.commit()
        db.close()

    def insertArticles(self,jsonData):
        db = pymysql.connect(host=rds_host, user=rds_id, db='seear', password=rds_password, charset='utf8')
        curs = db.cursor()
        sql = '''insert into articles (jsonData) values(%s)'''
        curs.execute(sql, (jsonData))
        db.commit()
        db.close()
        print("업데이트 성공")