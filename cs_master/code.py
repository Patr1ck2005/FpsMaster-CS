from datetime import datetime
import hashlib


def generate_daily_security_key():
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")  # 将日期转换为字符串形式，例如 "2024-03-11"
    date_string += 'daily'
    # 使用SHA-256哈希函数生成密钥
    sha256 = hashlib.sha256()
    sha256.update(date_string.encode('utf-8'))
    security_key = sha256.hexdigest()
    return security_key


def generate_monthly_security_key():
    now = datetime.now()
    date_string = now.strftime("%Y-%m")  # 将日期转换为字符串形式，例如 "2024-03"
    date_string += 'monthly'
    # 使用SHA-256哈希函数生成密钥
    sha256 = hashlib.sha256()
    sha256.update(date_string.encode('utf-8'))
    security_key = sha256.hexdigest()
    return security_key


# 生成安全密钥
daily_key = generate_daily_security_key()
monthly_key = generate_monthly_security_key()

# 打印生成的安全密钥
print("Daily Security Key:", daily_key)
print("Monthly Security Key:", monthly_key)