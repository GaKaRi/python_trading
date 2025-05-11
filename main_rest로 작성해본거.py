import requests
import json

# 접근토큰 발급
def fn_au10001(data):
	# 1. 요청할 API URL
	host = 'https://mockapi.kiwoom.com' # 모의투자
	#host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/oauth2/token'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
	}

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data)

	# 4. 응답 상태 코드와 데이터 출력
	print('Code:', response.status_code)
	print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
	print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력

	data = response.json()

	token = data.get("token")

	print('token 은', token)
	return token


# 계좌평가현황요청
def fn_kt00004(token, data, cont_yn='N', next_key=''):
	# 1. 요청할 API URL
	host = 'https://mockapi.kiwoom.com' # 모의투자
	#host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/api/dostk/acnt'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
		'authorization': f'Bearer {token}', # 접근토큰
		'cont-yn': cont_yn, # 연속조회여부
		'next-key': next_key, # 연속조회키
		'api-id': 'kt00004', # TR명
	}

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data)

	# 4. 응답 상태 코드와 데이터 출력
	print('Code:', response.status_code)
	print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
	print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력

# 예수금상세현황요청
def fn_kt00001(token, data, cont_yn='N', next_key=''):
	# 1. 요청할 API URL
	host = 'https://mockapi.kiwoom.com' # 모의투자
	#host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/api/dostk/acnt'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
		'authorization': f'Bearer {token}', # 접근토큰
		'cont-yn': cont_yn, # 연속조회여부
		'next-key': next_key, # 연속조회키
		'api-id': 'kt00001', # TR명
	}

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data)

	# 4. 응답 상태 코드와 데이터 출력
	print('Code:', response.status_code)
	print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
	print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력


# 실행 구간
if __name__ == '__main__':
	# 1. 요청 데이터
	params = {
		'grant_type': 'client_credentials',  # grant_type
		'appkey': 'TB75dlPZeT5U19i2traVD3Fgi_u8Zllm1i1ig9gRp0M',  # 앱키
		'secretkey': 'EqN3mNAFvh_K-QSkXZqCnT3RlFCdsjX4GyhAPiTOeh0',  # 시크릿키
	}

	# 2. API 실행
	token = fn_au10001(data=params)



	# 1. 토큰 설정
	MY_ACCESS_TOKEN = token

	# 2. 요청 데이터
	params = {
		'qry_tp': '0', # 상장폐지조회구분 0:전체, 1:상장폐지종목제외
		'dmst_stex_tp': 'KRX', # 국내거래소구분 KRX:한국거래소,NXT:넥스트트레이드
	}

	# 3. API 실행
	fn_kt00004(token=MY_ACCESS_TOKEN, data=params)

	#next-key, cont-yn 값이 있을 경우
	#fn_kt00004(token=MY_ACCESS_TOKEN, data=params, cont_yn='N', next_key='nextkey..')

######################################################################
	# 1. 토큰 설정
	#MY_ACCESS_TOKEN = '사용자 AccessToken'# 접근토큰

	# 2. 요청 데이터
	params = {
		'qry_tp': '3', # 조회구분 3:추정조회, 2:일반조회
	}

	# 3. API 실행
	fn_kt00001(token=MY_ACCESS_TOKEN, data=params)

	# next-key, cont-yn 값이 있을 경우
	# fn_kt00001(token=MY_ACCESS_TOKEN, data=params, cont_yn='N', next_key='nextkey..')
