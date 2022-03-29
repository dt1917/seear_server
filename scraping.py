from urllib.request import urlopen
from bs4 import BeautifulSoup
import urllib.request


for index in range(108,110):#50,700
    try:
        req = urlopen('https://media.naver.com/press/'+str(index)+'/ranking?type=popular')
        soup = BeautifulSoup(req,"lxml",from_encoding='utf-8')
        name = soup.find("a",{"class":"press_hd_name_link"})#언론사명
        title = soup.select(".list_title");  # 기사제목
        url = soup.select("._es_pc_link");  # 기사링크
        print(index,name.text.strip())

        for tmp in range(len(title)):
            print(title[tmp].text)
            print(url[tmp]['href'])

            headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'}
            req = urllib.request.Request(url[tmp]['href'],headers=headers)
            subREQ = urlopen(req)
            subSoup = BeautifulSoup(subREQ, "lxml", from_encoding='utf-8')
            print(subSoup)
            subText = subSoup.select(".article_p") ##dic_area
            print(subText)
    except:
        pass


'''
스타뉴스 108
OSEN 109
헤럴드POP 112
마이데일리 117
데일리안 119
조세일보 123
기자협회보 127
디지털데일리 138
스포탈코리아 139
스포츠경향 144
레이디경향 145
TV리포트 213
MBC 214
한국경제TV 215
골닷컴 216
이코노미스트 243
신동아 262
아시아경제 277
블로터 293
코메디닷컴 296
시사IN 308
여성신문 310
엑스포츠뉴스 311
텐아시아 312
베스트일레븐 343
헬스조선 346
바스켓코리아 351
중앙SUNDAY 353
조선비즈 366
SBS Biz 374
스포츠동아 382
스포츠월드 396
루키 398
MBC연예 408
몬스터짐 409
MK스포츠 410
포포투 411
인터풋볼 413
앳스타일 415
SBS연예뉴스 416
머니S 417
뉴스1 421
연합뉴스TV 422
마니아타임즈 425
OBS TV 427
디스패치 433
골프다이제스트 435
풋볼리스트 436
JTBC 437
KBS 연예 438
티브이데일리 440
MHN스포츠 445
TV조선 448
채널A 449
STN 스포츠 450
아이즈 ize 465
한국일보 469
JTBC GOLF 470
스포츠타임스 472
스포티비뉴스 477
테니스코리아 481
스포츠춘추 529
동아사이언스 584
시사저널 586
뉴스타파 607
뉴스엔 609
더팩트 629
코리아중앙데일리 640
비즈니스워치 648
강원도민일보 654
CJB청주방송 655
대전일보 656
대구MBC 657
국제신문 658
전주MBC 659
kbc광주방송 660
JIBS 661
'''