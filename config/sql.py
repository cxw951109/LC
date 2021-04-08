import json
import datetime
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String,Integer,create_engine,ForeignKey

# engine = create_engine('mysql+mysqlconnector://root:%s@localhost:3306/demo5' % 1111,pool_size=10)
engine = create_engine('mysql+pymysql://root:%s@localhost:3306/demo5' % 1111,pool_size=10)
dic = {"1": "类型1", "2": "类型2","3": "类型3", "4": "类型4","5": "类型5"}

Base = declarative_base()


def func(today, date_list=[], count=0):
    target = (today - datetime.timedelta(days=1))
    target_res = today.strftime("%Y-%m-%d")
    date_list.append(target_res)
    count += 1
    if count >= 7:
        pass
    else:
        func(target, date_list, count)
    return date_list

#折线图
def chart1(session,value,start,end):
    data = []
    data1 = []
    data2 = []
    data3 = []
    today = datetime.date.today()
    today_res = today.strftime("%Y")
    target = (today - datetime.timedelta(days=8))
    target_res = target.strftime("%Y-%m-%d")
    date_list = func(today, [])
    m_list =['01','02','03','04','05','06','07','08','09',10,11,12]
    if start !='':
        target_res =start.strftime("%Y-%m-%d")
        today =end.strftime("%Y-%m-%d")
    if value !='':
        query = session.query(Dailydata).filter(Dailydata.created_time.between(target_res, today),Dailydata.standard_name.like("%" + value + "%")).all()
        query1 = session.query(Dailydata).filter(Dailydata.created_time.contains(today_res),Dailydata.standard_name.like("%" + value + "%")).all()
    else:
        query = session.query(Dailydata).filter(Dailydata.created_time.between(target_res, today)).all()
        query1 = session.query(Dailydata).filter(Dailydata.created_time.contains(today_res)).all()
    for i in date_list:
        data.append(sum([x.goodNum for x in query if x.created_time == i]))
        data1.append(sum([x.badNum for x in query if x.created_time == i]))
    for n in m_list:
        data2.append(sum([x.goodNum for x in query1 if x.created_time.split('-')[1] ==str(n)]))
        data3.append(sum([x.badNum for x in query1 if x.created_time.split('-')[1] ==str(n)]))
    series = [
        {
            "name": '合格',
            "data": data,
            "type": 'line'
        },
        {
            "name": '劣质',
            "data": data1,
            "type": 'line'
        }
    ]
    series1 = [
        {
            "name": '合格',
            "data": data2,
            "type": 'line'
        },
        {
            "name": '劣质',
            "data": data3,
            "type": 'line'
        }
    ]
    return [series,date_list,series1]

#饼图
def chart2(session,value,start,end):
    if start !='':
        start =start.strftime("%Y-%m-%d")
        end =end.strftime("%Y-%m-%d")
        if value !='':
            query = session.query(Dailydata).filter(Dailydata.standard_name.like("%" + value + "%"),Dailydata.created_time.between(start, end)).all()
            query1 =session.query(Baddata).filter(Baddata.standard_name.like("%" + value + "%"),Baddata.created_time.between(start, end)).all()
        else:
            query = session.query(Dailydata).filter(Dailydata.created_time.between(start, end)).all()
            query1 =session.query(Baddata).filter(Baddata.created_time.between(start, end)).all()
    else:
        if value !='':
            query = session.query(Dailydata).filter(Dailydata.standard_name.like("%" + value + "%")).all()
            query1 =session.query(Baddata).filter(Baddata.standard_name.like("%" + value + "%")).all()
        else:
            query = session.query(Dailydata).all()
            query1 =session.query(Baddata).all()
    good =sum([x.goodNum for x in query])
    bad =sum([x.badNum for x in query])
    all =good+bad
    names =list(dic.values())
    series2 = []
    for i in names:
        series2.append({"value":sum([x.Num for x in query1 if x.types == i]),"name":i})
    if all !=0:
        all_pass_rate = '%.2f' % (good * 100 / (good+bad))
    else:
        all_pass_rate = '%.2f' % 0
    series3 =[
        {"value": good, "name": '合格'},
        {"value": bad, "name": '劣质'}
    ]
    series4=[all_pass_rate]
    return [series2,series3,series4]

#排名
def rank(session):
    today = datetime.date.today()
    query1 = session.query(Baddata).filter(Baddata.created_time == str(today)).all()
    all =sum([x.Num for x in query1])
    names = list(dic.values())
    series2 = []
    if all ==0:
        for i in names:
            series2.append({"value":0.00,"name":i})
    else:
        for i in names:
            series2.append({"value":'%.2f' % (sum([x.Num for x in query1 if x.types == i])*100/all),"name":i})
    return  series2

#今日数据
def get_today():
    session2 = MySession()
    query = session2.query(Dailydata2).first()
    session2.close()
    if query:
        all =query.goodNum+query.badNum
        return all,query.goodNum,query.badNum
    else:
        return 0,0,0


class Dailydata(Base):
    __tablename__ = 'daily_data'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    standard_name = Column(String(20))
    goodNum = Column(Integer)
    badNum = Column(Integer)
    created_time = Column(String(20))


class Dailydata2(Base):
    __tablename__ = 'daily_data2'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    goodNum = Column(Integer)
    badNum = Column(Integer)


class Baddata(Base):
    __tablename__ = 'bad_data'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    Num = Column(Integer)
    standard_name = Column(String(20))
    types =Column(String(20))
    created_time = Column(String(20))


class Alert(Base):
    __tablename__ = 'alert'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    mes =Column(String(100))
    created_time = Column(String(20))


    def __init__(self, mes,created_time):
        self.mes = mes
        self.created_time = created_time

    def to_dict(self):
        return {
            "id":self.id,
            "mes": self.mes,
            "created_time": self.created_time,
        }


class History(Base):
    __tablename__ = 'history'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    url = Column(String(100))
    types =Column(String(20))
    standard_name = Column(String(20))
    created_time = Column(String(20))


    def __init__(self, url, types,standard_name,created_time):
        self.types = types
        self.standard_name = standard_name
        self.url = url
        self.created_time = created_time

    def to_dict(self):
        return {
            "id":self.id,
            "standard_name": self.standard_name,
            "types": self.types,
            "url":self.url,
            "created_time": self.created_time,
        }


class Standard(Base):
    __tablename__ = 'standard'

    id = Column(Integer(), primary_key=True,autoincrement=True)
    name = Column(String(20))
    url = Column(String(100))
    flag = Column(Integer,default=0)
    created_time = Column(String(20))

    def __init__(self, name, url ,created_time,flag):
        self.name = name
        self.url = url
        self.created_time = created_time
        self.flag = flag

    def to_dict(self):
        return {
            "id":self.id,
            "name": self.name,
            "url": self.url,
            "created_time": self.created_time,
            "flag": self.flag
        }


class Item(BaseModel):
    msg: str


class Item1(BaseModel):
    key: int
    value: str


class Item2(BaseModel):
    total: int
    ng_count: int
    standard_name: str
    result: list =[]


Base.metadata.create_all(engine)

MySession = sessionmaker(bind=engine)
session = MySession()
try:
    res = session.query(Dailydata2).first()
    if not res:
        session.add(Dailydata2(goodNum=0, badNum=0))
    today = datetime.date.today()
    session.query(History).filter(History.created_time <= today - datetime.timedelta(days=30)).delete()
    session.commit()
except:
    session.close()
    session =MySession()
