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

    def insertArticles(self,jsonData):
        db = pymysql.connect(host=rds_host, user=rds_id, db='seear', password=rds_password, charset='utf8')
        curs = db.cursor()
        sql = '''insert into articles (jsonData) values(%s)'''
        curs.execute(sql, (jsonData))
        db.commit()
        db.close()
        print("업데이트 성공")

    def insertPress(self):
        pressData='''데일리안 119 종합
        조세일보 123 경제
        디지털데일리 138 IT
        MBC 214 종합
        한국경제TV 215 경제
        이코노미스트 243 경제
        신동아 262 종합
        아시아경제 277 종합
        코메디닷컴 296 건강
        시사IN 308 시사
        헬스조선 346 건강
        중앙SUNDAY 353 시사
        조선비즈 366 경제
        SBS Biz 374 경제
        뉴스1 421 (종합)
        연합뉴스TV 422 (종합)
        JTBC 437 (종합)
        TV조선 448 (종합)
        채널A 449 (종합)
        한국일보 469 (종합)
        시사저널 586 (종합)
        뉴스타파 607 (종합)
        더팩트 629 (종합)
        비즈니스워치 648 (경제)'''
        presses=pressData.split('\n')
        for press in presses:
            press=press.strip()
            print(press)
            pressInfo = press.split(" ")
            print(pressInfo)
            db = pymysql.connect(host=rds_host, user=rds_id, db='seear', password=rds_password, charset='utf8')
            curs = db.cursor()
            sql = '''insert into press (name, number) values(%s,%s)'''
            curs.execute(sql, (pressInfo[0],pressInfo[1]))
            db.commit()
            db.close()