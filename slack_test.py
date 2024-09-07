import requests

def send_slack_message(webhook_url, message):
    payload = {'text': message}
    response = requests.post(webhook_url, json=payload)
    return response.text

# 슬랙 웹훅 URL
webhook_url = 'https://hooks.slack.com/services/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'

# 보낼 메시지
message = '안녕하세요, 대멋잼이 슬랙 채널에 메시지를 보냅니다!'

# 메시지 보내기
send_slack_message(webhook_url, message)