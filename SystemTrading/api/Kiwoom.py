from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import pandas as pd

import sys
import os

from SystemTrading.util.const import FID_CODES

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._make_kiwoom_instance()
        self._set_signal_slots()
        self._comm_connect()#로그인 요청하는 메소드 시작

        self.account_number = self.get_account_number()#계좌번호 가져옴

        self.tr_event_loop = QEventLoop()#TR 요청에 대한 응답 대기를 위한 변수 데이터가 올 때까지 기다렸다가 처리해!" 하는 용도로 사용하는 이벤트 루프
        
        self.order = {} #종목 코드를 키 값으로 해당 종목의 주문 정보를 담은 딕셔너리
        self.balance = {} #종목 코드를 키 값으로 해당 종목의 매수 정보를 담은 딕셔너리
        
    def _make_kiwoom_instance(self): #키움 클래스가 API를 사용할 수 있도록 등록하는 함수
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        print("Available signals:")
        print(dir(self))  # 여기에 OnEventConnect가 나와야 정상

    #로그인 슬롯을 등록하는 함수임
    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._login_slot)

        #TR의 응답결과를 받도록 설정
        self.OnReceiveTrData.connect(self._on_receive_tr_data)
        
        #TR/주문 메시지를 _on_receive_msg로 받도록 설정
        self.OnReceiveMsg.connect(self._on_receive_msg)
        
        #주문 접수/체결 결과를 _on_chejan_slot으로 받도록 설정
        self.OnReceiveChejanData.connect(self._on_chejan_slot)

    #로그인 성공시 0 실패시 다른값이 나옴 100, 101, 102 등
    def _login_slot(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("not connected")
        self.login_event_loop.exit()

    #로그인 함수: 로그인 요청 신호를 보낸 이후 응답 대기를 설정하는 함수
    def _comm_connect(self):
        self.dynamicCall("CommConnect()") #API서버로 로그인 요청을 보냄

        #로그인 시도 후 응답을 대기하는 상태로 만듬 아래 두코드임
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    #계좌번호 불러오는 함수
    def get_account_number(self, tag="ACCNO"):
        account_list = self.dynamicCall("GetLoginInfo(QString)", tag)
        account_number = account_list.split(';')[0] #계좌만 분리해서 가져옴 [1]은 공백임
        print(account_number)
        return account_number

    #코스피, 코스닥에 상장된 모든종목 불러오는 함수
    def get_code_list_by_market(self, market_type):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_type)
        code_list = code_list.split(';')[:-1] #[:-1] 는 마지막 문자를 제거하고 모두 가져오라는 의미 파이썬에서 list[-1]은 리스트의 마지막 요소를 의미
        #[0]은 첫번째 요소 [-1]은 마지막 요소임
        return code_list

    #종목 코드를 받아 종목명을 받환하는 함수
    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString", code)
        return code_name

    def get_price_data(self, code):
        #종목의 상장일부터 가장 최근 일자까지 일봉정보를 가져오는 함수
        self.dynamicCall("SetInputValue(QString, QString", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString", "수정주가구분", 1)#1이면 수정주가 적용함
        self.dynamicCall("CommRqData(QString, QString, int, QString", "opt10081_req", "opt10081", 0, "0001")

        self.tr_event_loop.exec_()#TR요청 보낸후 응답 대기상태로 만드는 코드임 이후 코드는 TR에 대한 응답이 도착한 후 실행됨

        ohlcv = self.tr_data#응답 slot함수 _on_receive_tr_data에서 수신한 일봉 데이터 저장되어있어서 사용 가능함

        while self.has_next_tr_data: #다음 데이터가 있다면 실행
            self.dynamicCall("SetInputValue(QString, QString", "종목코드", code)
            self.dynamicCall("SetInputValue(QString, QString", "수정주가구분", 1)  # 1이면 수정주가 적용함
            self.dynamicCall("CommRqData(QString, QString, int, QString", "opt10081_req", "opt10081", 2, "0001")#2인 이유는 연속조회이므로
            self.tr_event_loop.exec_()#TR요청 보낸후 응답 대기상태로 만드는 코드임 이후 코드는 TR에 대한 응답이 도착한 후 실행됨

            #최초로 얻어온 가격 데이터를 담은 ohlcv에 데이터를 이어 붙이는 작업을 함
            for key, val in self.tr_data.items():
                ohlcv[key] += val


        df = pd.DataFrame(ohlcv, columns=['open', 'high', 'low', 'close', 'volume'], index=ohlcv['date'])

        return df[::-1]



    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        print("[Kiwoon _on_receive_tr_data is called {} / {} / {}".format(screen_no, rqname, trcode))
        tr_data_cnt = self.dynamicCall("GetRepeatCnt(QString, QString", trcode, rqname) #가져온 TR의 응답갯수 즉 600일치면 600이 저장됨

        #만약 600일치가 넘은 일본데이터를 필요하면 next를 2로 설정해서 _on_receive_tr_data를 한번더 호출할 수 있게 함
        if next == '2':
            self.has_next_tr_data = True
        else:
            self.has_next_tr_data = False

        if rqname == "opt10081_req":
            ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}#ohlcv는 지역변수임

            for i in range(tr_data_cnt):
                date = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "일자")
                open = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "시가")
                high = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "고가")
                low = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "저가")
                close = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "현재가")
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString", trcode, rqname, i, "거래량")

                ohlcv['date'].append(date.strip())
                ohlcv['open'].append(int(open))
                ohlcv['high'].append(int(high))
                ohlcv['low'].append(int(low))
                ohlcv['close'].append(int(close))
                ohlcv['volume'].append(int(volume))

            self.tr_data = ohlcv#글로벌 변수로 편입시킴

        #예수금 얻어오기 받는 부분
        elif rqname == "opw00001_req":
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "주문가능금액")
            self.tr_data = int(deposit)
            print(self.tr_data)

        self.tr_event_loop.exit()#tr 요청을 보내고 응답을 대기시키는데 사용하는 self.tr_event_loop 를 종료 시킴
        time.sleep(0.5)#0.5초만듬 쉼

    #조회 대상 계좌의 예수금을 얻어 오는 함수
    def get_deposit(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00001_req", "opw00001", 0, "0002")

        self.tr_event_loop.exec_()
        return self.tr_data

    def send_order(self, rqname, screen_no, order_type, code, order_quantity, order_price, order_classification, origin_order_number=""):
        order_result = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)"
                                        , [rqname, screen_no, self.account_number, order_type, code,
                                           order_quantity, order_price, order_classification, origin_order_number])
        return order_result

    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        print("[Kiwoom] _on_receive_msg is called {} / {} / {} / {}".format(screen_no, rqname, trcode, msg))

    def _on_chejan_slot(self, s_gubun, n_item_cnt, s_fid_list):
        print("[Kiwoom] _on_chejan_slot is called {} / {} / {}".format(s_gubun, n_item_cnt, s_fid_list))

        for fid in s_fid_list.split(";"): # ;로 구분되는 fid 리스트를 ;를 기준으로 구분함
            if fid in FID_CODES:
                code = self.dynamicCall("GetChejanData(int)", '9001')[1:] #종목코드의 앞자리 A를 제거함 9001은 FID가 종목코드임
                data = self.dynamicCall("GetChejanData(int)", fid) #fid를 사용하여 데이터 얻어오기 9203이면 주문번호를 수신하여 data를 저장

                data = data.strip().lstrip('+').lstrip('-') #데이터에 +가 붙어있으면 매수 -면 매도인데 제거함

                if data.isdigit():#수신된 문자형 데이터 중 숫자인 항목을 숫자로 바꿈
                    data = int(data)

                item_name = FID_CODES[fid]#fid 코드에 해당하는 항목(item_name)을 찾음
                print("{}: {}".format(item_name, data))#얻어온 데이터 출력(주문가격 30000)

                if int(s_gubun) == 0: #s_gubun이 0이면 접수/체결 시

                    if code not in self.order.keys():#아직 order 종목 코드가 없다면 신규 생성하는 과정
                        self.order[code] = {} #빈딕셔너리 생성

                        #예를들어 {'00700' : {'주문상태' : '체결'}} 이런식으로 저장하게됨
                        #접근시 ['00700']['주문상태']로 접근하면 됨
                    self.order[code].update({item_name: data})#order 딕셔너리에 데이터 저장

                elif int(s_gubun) == 1:#s_gubun이 1이면 국내 주식 잔고 변경을 함
                    #아직 balance에 종목 코드가 없다면 신규 생성하는 과정 
                    if code not in self.balance.keys():
                        self.balance[code] = {}

                    self.balance[code].update({item_name: data})

        if int(s_gubun) == 0:
            print("* 주문 출력(self.order)")
            print(self.order)
        elif int(s_gubun) == 1:
            print("* 잔고 출력(self.balance)")
            print(self.balance)


