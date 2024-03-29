import requests
import time
import os
import importlib.util
import subprocess
import re
import sys

# API 헤더
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
useragent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

#경로지정
path = f"/recordings/"

#채널ID
print("채널 ID를 입력해주세요.\n ex) 75cbf189b3bb8f9f687d2aca0d0a382b\n")
channel_id = input().strip()

# API 엔드포인트 URL
naver_api_url = f'https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail'

# Naver API에서 상태 확인 함수
def check_naver_status():
    response = requests.get(naver_api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('content', {}).get('status')
    else:
        print(f'Error Status code: {response.status_code}\nResponse: {response.text}')
        return None

# 특수문자 제거 함수 정의
def remove_special_characters(text):
    # 정규 표현식을 사용하여 특수문자를 제거하고 반환
    return re.sub(r'[^\w\s]', '', text)

# 파일 이름 중복 확인 및 변경 함수 정의
def check_and_rename_file(file_name_recieve):
    file_path_chk = f"{path}{file_name_recieve}"
    base, ext = os.path.splitext(file_name_recieve)
    index = 1
    while os.path.exists(file_path_chk):
        new_file_name = f"{base}_{index}{ext}"
        file_path_chk = f"{path}{new_file_name}"
        index += 1
    return new_file_name if index > 1 else file_name_recieve  # 파일이 존재하지 않을 때 처리 추가

# 주기적으로 Naver API 호출하여 상태 확인 및 녹화 시작
def check_and_record_periodically():
    while True:
        naver_status = check_naver_status()
        print(naver_status)
        
        if naver_status == 'OPEN':
            response = requests.get(naver_api_url, headers=headers)
            title = response.json().get('content', {}).get('liveTitle')
            channel = response.json().get('content', {}).get('channel').get('channelName')
            time_value = response.json().get('content', {}).get('openDate')

            print("Open Detect!")

            # 특수문자 제거
            title_removed = remove_special_characters(title)
            channel_removed = remove_special_characters(channel)
            time_value_removed = remove_special_characters(time_value)

            # 파일 이름 설정
            file_name = f"{channel_removed}_{time_value_removed}_{title_removed}.ts"
            file_name = check_and_rename_file(file_name)
            file_path = f"{path}{file_name}"
            
            # 실시간 녹화 시작
            record_command = f'streamlink --loglevel none --http-header "User-Agent={useragent}" https://chzzk.naver.com/live/{channel_id} 1080p --output "{file_path}"'
            subprocess.run(record_command, shell=True)
            
            # CLOSE 상태가 될 때까지 대기
            while check_naver_status() == 'OPEN':
                print("Checking for Close status")
                time.sleep(10)  # 10초마다 확인 (조절 가능)
        else:
            print("Not Open Status. Checking again in 10 seconds.")
            time.sleep(10)  # CLOSE 상태인 경우 10초마다 확인 (조절 가능)

if __name__ == "__main__":
    check_and_record_periodically()
