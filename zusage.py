#!/usr/bin/env python3
"""
Z.AI API 配额查询工具
查询并显示 Z.AI API 的 token 使用情况和重置时间
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone


# ANSI 颜色代码
class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # 进度条颜色
    GREEN_BAR = '\033[92m'
    YELLOW_BAR = '\033[93m'
    RED_BAR = '\033[91m'
    GRAY_BAR = '\033[90m'


def get_env_token():
    """从环境变量读取 ZAI_TOKEN"""
    token = os.environ.get('ZAI_TOKEN')
    if not token:
        print(f"{Colors.FAIL}错误: 未找到 ZAI_TOKEN 环境变量{Colors.ENDC}")
        print(f"\n请设置环境变量:")
        print(f"  export ZAI_TOKEN=\"your-token-here\"")
        print(f"\n或者添加到 ~/.bashrc 或 ~/.zshrc:")
        print(f"  echo 'export ZAI_TOKEN=\"your-token-here\"' >> ~/.bashrc")
        sys.exit(1)
    return token


def fetch_quota_data(token):
    """从 API 获取配额数据"""
    url = 'https://api.z.ai/api/monitor/usage/quota/limit'

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en',
        'authorization': f'Bearer {token}',
        'origin': 'https://z.ai',
        'referer': 'https://z.ai/',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1'
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"{Colors.FAIL}错误: HTTP {e.code} - {e.reason}{Colors.ENDC}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"{Colors.FAIL}错误: 无法连接到服务器 - {e.reason}{Colors.ENDC}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{Colors.FAIL}错误: 无法解析 API 响应 - {e}{Colors.ENDC}")
        sys.exit(1)


def format_number(num):
    """格式化数字，添加千位分隔符"""
    return f"{num:,}"


def get_progress_bar_color(percentage):
    """根据百分比返回进度条颜色"""
    if percentage < 50:
        return Colors.GREEN_BAR
    elif percentage < 80:
        return Colors.YELLOW_BAR
    else:
        return Colors.RED_BAR


def get_percentage_color(percentage):
    """根据百分比返回文字颜色"""
    if percentage < 50:
        return Colors.OKGREEN
    elif percentage < 80:
        return Colors.WARNING
    else:
        return Colors.FAIL


def create_progress_bar(percentage, width=30):
    """创建进度条"""
    filled = int(width * percentage / 100)
    empty = width - filled
    color = get_progress_bar_color(percentage)

    bar = color + '█' * filled + Colors.GRAY_BAR + '░' * empty + Colors.ENDC
    return bar


def format_timestamp(ms_timestamp):
    """将 Unix 毫秒时间戳转换为可读时间"""
    # 将毫秒转换为秒
    timestamp = ms_timestamp / 1000
    # 转换为 datetime 对象（UTC）
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    # 转换为本地时间
    local_dt = dt.astimezone()
    # 格式化输出
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')


def calculate_time_remaining(reset_timestamp):
    """计算距离重置的剩余时间"""
    # 将毫秒转换为秒
    reset_time = reset_timestamp / 1000
    now = datetime.now(timezone.utc).timestamp()

    remaining_seconds = reset_time - now

    if remaining_seconds <= 0:
        return "即将重置"

    days = int(remaining_seconds // 86400)
    hours = int((remaining_seconds % 86400) // 3600)
    minutes = int((remaining_seconds % 3600) // 60)

    if days > 0:
        return f"还有 {days} 天 {hours} 小时"
    elif hours > 0:
        return f"还有 {hours} 小时 {minutes} 分钟"
    else:
        return f"还有 {minutes} 分钟"


def extract_token_data(data):
    """从 API 响应中提取 token 相关数据"""
    try:
        limits = data.get('data', {}).get('limits', [])
        for limit in limits:
            if limit.get('type') == 'TOKENS_LIMIT':
                return limit
        return None
    except (AttributeError, TypeError):
        return None


def extract_usage_details(data):
    """从 API 响应中提取各服务使用详情"""
    try:
        limits = data.get('data', {}).get('limits', [])
        for limit in limits:
            if limit.get('type') == 'TIME_LIMIT':
                return limit.get('usageDetails', [])
        return []
    except (AttributeError, TypeError):
        return []


def print_header():
    """打印标题"""
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}🤖 Z.AI API 配额使用情况{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'━' * 50}{Colors.ENDC}\n")


def print_token_usage(token_data):
    """打印 token 使用情况"""
    if not token_data:
        print(f"{Colors.WARNING}未找到 token 使用数据{Colors.ENDC}")
        return

    percentage = token_data.get('percentage', 0)
    current_value = token_data.get('currentValue', 0)
    total = token_data.get('usage', 0)
    remaining = token_data.get('remaining', 0)
    reset_time = token_data.get('nextResetTime', 0)

    # Token 使用情况标题
    print(f"{Colors.OKBLUE}{Colors.BOLD}📊 Token 使用情况:{Colors.ENDC}")

    # 进度条
    progress_bar = create_progress_bar(percentage)
    percentage_color = get_percentage_color(percentage)

    print(f"  已使用: {progress_bar} {percentage_color}{percentage}%{Colors.ENDC} "
          f"({format_number(current_value)} / {format_number(total)})")

    # 剩余量
    print(f"  剩余: {format_number(remaining)} tokens\n")

    # 重置时间
    if reset_time:
        formatted_time = format_timestamp(reset_time)
        time_remaining = calculate_time_remaining(reset_time)
        print(f"{Colors.OKBLUE}{Colors.BOLD}⏰ 下次重置:{Colors.ENDC} {formatted_time}")
        print(f"  {Colors.OKCYAN}({time_remaining}){Colors.ENDC}\n")


def print_service_usage(usage_details):
    """打印各服务使用详情"""
    if not usage_details:
        return

    print(f"{Colors.OKBLUE}{Colors.BOLD}📈 各服务使用详情:{Colors.ENDC}")
    for detail in usage_details:
        model = detail.get('modelCode', 'unknown')
        usage = detail.get('usage', 0)
        print(f"  • {model:<15} {format_number(usage)} tokens")
    print()


def print_footer():
    """打印底部"""
    print(f"{Colors.OKCYAN}{'━' * 50}{Colors.ENDC}\n")


def main():
    """主函数"""
    # 打印标题
    print_header()

    # 获取 token
    token = get_env_token()

    # 获取配额数据
    data = fetch_quota_data(token)

    # 检查响应是否成功
    if not data.get('success'):
        print(f"{Colors.FAIL}错误: API 返回失败{Colors.ENDC}")
        if 'msg' in data:
            print(f"消息: {data['msg']}")
        sys.exit(1)

    # 提取并显示 token 使用情况
    token_data = extract_token_data(data)
    print_token_usage(token_data)

    # 提取并显示各服务使用详情
    usage_details = extract_usage_details(data)
    print_service_usage(usage_details)

    # 打印底部
    print_footer()


if __name__ == '__main__':
    main()
