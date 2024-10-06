import requests

API_ENDPOINT = "https://api.runpod.ai/v2/ak569nedzstoz2/runsync"
API_KEY = "07SQGVMUUV7GMN6V4JC7GLEF7290ZA8T0BPT61GZ"

# 헤더 설정
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"  # 필요에 따라 다른 Content-Type을 설정할 수 있습니다.
}

# 요청 보내기
response = requests.get(API_ENDPOINT, headers=headers)

# 응답 확인
if response.status_code == 200:
    print("응답 데이터:", response.json())
else:
    print("요청 실패:", response.status_code, response.text)
