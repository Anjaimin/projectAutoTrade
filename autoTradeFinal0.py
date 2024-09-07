import sys
import requests
import time
import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QTime
from pykiwoom.kiwoom import Kiwoom
from pykrx import stock
import datetime
import mysql.connector

form_class = uic.loadUiType(r'gui.ui')[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect(block=True)

        self.bought_list = {}

        # MySQL 데이터베이스에 연결
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",  # MySQL 사용자 이름
            password="root",  # MySQL 비밀번호
            database="test"  # 사용할 데이터베이스 이름
        )
        message = "DB 연결 성공"
        self.send_slack_message(message)
        self.cursor = self.conn.cursor()

        # 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_market_time)
        self.trade_timer = QTimer(self)
        self.trade_timer.timeout.connect(self.trade_stocks)

        self.button_start.clicked.connect(self.start_trading)
        self.button_stop.clicked.connect(self.stop_trading)

        self.send_slack_message("프로그램이 실행되었으며, 키움 API에 접속 성공했습니다.")

    def send_slack_message(self, message):
        webhook_url = "https://hooks.slack.com/services/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"
        headers = {'Content-type': 'application/json'}
        payload = {"text": message}
        requests.post(webhook_url, json=payload, headers=headers)

    def close_connection(self):
        # 커넥션 및 커서 닫기
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()

    def insert_trade_record(self, stockName, stock_code, order_price, order_quantity, sell_price=None,
                            sell_quantity=None, commission=None, profit_loss_amount=None, sell_amount=None,
                            buy_amount=None, return_rate=None, trade_type=None, strategy_name=None):
        trade_date = datetime.datetime.now().strftime('%Y-%m-%d')

        insert_query = '''
        INSERT INTO trade_data (stockName, stockCode, orderPrice, orderQuantity, sellPrice, sellQuantity, commission,
                                profitLossAmount, sellAmount, buyAmount, returnRate, tradeDate, tradeType, strategyName)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        values = (
            stockName, stock_code, order_price, order_quantity, sell_price, sell_quantity, commission,
            profit_loss_amount, sell_amount, buy_amount, return_rate, trade_date, trade_type, strategy_name
        )

        try:
            self.cursor.execute(insert_query, values)
            self.conn.commit()
        except Exception as e:
            self.textboard.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error in insert_trade_record: {e}")

    def start_trading(self):
        self.timer.start(1000 * 60)
        self.trade_timer.start(1000 * 17)
        today = datetime.datetime.now().strftime('%Y%m%d')
        self.bought_list = {code: today for code, buy_date in self.bought_list.items() if buy_date == today}

    def stop_trading(self):
        self.timer.stop()
        self.trade_timer.stop()
        self.close_connection()

    def check_market_time(self):
        now = QTime.currentTime()
        if now.toString("HHmm") >= "1108":  # 원하는 시간에 맞춰 수정 가능
            self.stop_trading()
            self.sell_all_stocks()

    def trade_stocks(self):
        try:
            today = datetime.datetime.now().strftime('%Y%m%d')
            yesterday = stock.get_nearest_business_day_in_a_week(today)
            if not yesterday:
                self.textboard.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: 유효한 영업일이 없습니다.")
                return

            self.textboard.append(
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Nearest business day found: {yesterday}")

            codes = self.code_list.text().split(',')
            k_value = float(self.k_value.text())

            for code in codes:
                if code.strip() and (code.strip() not in self.bought_list or self.bought_list[code.strip()] != today):
                    current_price_raw = self.kiwoom.block_request("opt10001",
                                                                  종목코드=code.strip(),
                                                                  output="주식기본정보",
                                                                  next=0)['현재가'][0].replace(",", "")
                    try:
                        if current_price_raw == '':
                            self.textboard.append(
                                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: 종목 {code}의 현재가 데이터가 없습니다.")
                            continue

                        current_price = int(current_price_raw)
                        if current_price < 0:
                            current_price = abs(current_price)

                        name = self.kiwoom.block_request("opt10001",
                                                         종목코드=code.strip(),
                                                         output="주식기본정보",
                                                         next=0)['종목명'][0]
                        self.textboard.append(
                            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] [{code}] [{name}] [현재가: {current_price}]")

                        yesterday_data = stock.get_market_ohlcv_by_date(yesterday, yesterday, code.strip())
                        if not yesterday_data.empty:
                            high = yesterday_data['고가'][0]
                            low = yesterday_data['저가'][0]
                            close = yesterday_data['종가'][0]
                            target_price = close + (high - low) * k_value

                            if current_price > target_price:
                                if self.buy_stock(code.strip(), current_price, 10, strategy_name="기본 전략"):
                                    self.bought_list[code.strip()] = today
                        else:
                            self.textboard.append(
                                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: 종목 {code}의 전일 데이터가 없습니다.")
                    except Exception as e:
                        self.textboard.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: {e}")
                        continue

        except Exception as e:
            self.textboard.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: {e}")

    def buy_stock(self, code, price, quantity, strategy_name):
        account_number = self.kiwoom.GetLoginInfo("ACCNO")[0]  # 전체 10자리 계좌번호 사용
        order_type = 1  # 매수
        order_result = self.kiwoom.SendOrder("매수주문", "0101", account_number, order_type, code, quantity, price, "03", "")

        if order_result == 0:
            stock_name = self.kiwoom.block_request("opt10001", 종목코드=code, output="주식기본정보", next=0)['종목명'][0]
            message = f"매수 주문 성공: [{code}] [가격: {price}] [수량: {quantity}]"
            self.send_slack_message(message)
            self.buysell_log.append(message)

            try:
                self.insert_trade_record(
                    stockName=stock_name,
                    stock_code=code,
                    order_price=price,
                    order_quantity=quantity,
                    sell_price=None,
                    sell_quantity=None,
                    commission=None,
                    profit_loss_amount=None,
                    sell_amount=None,
                    buy_amount=price * quantity,
                    return_rate=None,
                    trade_type="매수",
                    strategy_name=strategy_name
                )
            except Exception as e:
                self.textboard.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: {e}")
            return True
        else:
            error_message = f"매수 주문 실패: [{code}] 오류 코드: {order_result}"
            self.send_slack_message(error_message)
            self.buysell_log.append(error_message)
            return False

    def sell_all_stocks(self):
        account_number = self.kiwoom.GetLoginInfo("ACCNO")[0]
        stocks_info = self.kiwoom.block_request("opw00018",
                                                계좌번호=account_number,
                                                비밀번호="",
                                                비밀번호입력매체구분="00",
                                                조회구분=2,
                                                output="계좌평가잔고개별합산",
                                                next=0)
        # 재연결을 위한 커넥션 체크 및 재연결
        if not self.conn.is_connected():
            self.conn.reconnect(attempts=3, delay=2)
            self.cursor = self.conn.cursor()


        if '종목번호' in stocks_info:
            for idx, code in enumerate(stocks_info['종목번호']):
                code = code.strip()[1:]
                quantity_str = stocks_info['보유수량'][idx].strip()

                if not quantity_str.isdigit():
                    quantity_str = 0

                quantity = int(quantity_str)
                if quantity > 0:
                    order_type = 2
                    order_result = self.kiwoom.SendOrder("매도주문", "0101", account_number, order_type, code, quantity, 0, "03", "")
                    if order_result == 0:
                        stock_name = self.kiwoom.block_request("opt10001", 종목코드=code, output="주식기본정보", next=0)['종목명'][0]
                        sell_price_raw = self.kiwoom.block_request("opt10001", 종목코드=code, output="주식기본정보", next=0)['현재가'][0].replace(",", "")

                        if sell_price_raw == '':
                            self.textboard.append(
                                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: 종목 {code}의 현재가 데이터가 없습니다.")
                            continue

                        sell_price = int(sell_price_raw)

                        message = f"매도 주문 성공: [{code}] [수량: {quantity}]"
                        self.send_slack_message(message)
                        self.buysell_log.append(message)

                        try:
                            self.insert_trade_record(
                                stockName=stock_name,
                                stock_code=code,
                                order_price=None,
                                order_quantity=None,
                                sell_price=sell_price,
                                sell_quantity=quantity,
                                commission=None,
                                profit_loss_amount=None,
                                sell_amount=sell_price * quantity,
                                buy_amount=None,
                                return_rate=None,
                                trade_type="매도",
                                strategy_name="기본 전략"
                            )
                        except Exception as e:
                            self.textboard.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error: {e}")
                    else:
                        message = f"매도 주문 실패: [{code}]"
                        self.send_slack_message(message)
                        self.buysell_log.append(message)

                elif quantity == 0:
                    message = "매도 주문 실패: 보유한 주식 없음"
                    self.send_slack_message(message)
                    self.buysell_log.append(message)

        else:
            message = "매도 주문 실패: 보유 주식 데이터 확인 불가"
            self.send_slack_message(message)
            self.buysell_log.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())

