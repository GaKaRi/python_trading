from api.Kiwoom import *
import sys

app = QApplication(sys.argv)
kiwoom = Kiwoom()

#kiwoom.get_account_number()

#df = kiwoom.get_price_data("005930_AL")
#print(df)

deposit = kiwoom.get_deposit()

order_result = kiwoom.send_order('send_buy_order', '1001', 1, '005930', 1, 60000, '00')

print(order_result)

'''kospi_code_list = kiwoom.get_code_list_by_market("0")
print(len(kospi_code_list))

for code in kospi_code_list:
    code_name = kiwoom.get_master_code_name(code)
    print(code, code_name)

kosdaq_code_list = kiwoom.get_code_list_by_market("10")
print(kosdaq_code_list)
for code in kosdaq_code_list:
    code_name = kiwoom.get_master_code_name(code)
    print(code, code_name)'''

app.exec_()

