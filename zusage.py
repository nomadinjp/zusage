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
import urllib.parse
import argparse
from datetime import datetime, timezone, timedelta


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

    # 进度条和百分比
    progress_bar = create_progress_bar(percentage)
    percentage_color = get_percentage_color(percentage)

    # 检查是否有具体的数值数据
    if current_value > 0 or total > 0:
        print(f"  已使用: {progress_bar} {percentage_color}{percentage}%{Colors.ENDC} "
              f"({format_number(current_value)} / {format_number(total)})")
    else:
        # 新 API 格式：只有百分比，没有具体数值
        print(f"  使用率: {progress_bar} {percentage_color}{percentage}%{Colors.ENDC}")

    # 剩余量（如果有）
    if remaining > 0:
        print(f"  剩余: {format_number(remaining)} tokens")
    else:
        print()

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


def fetch_usage_data(token, start_time, end_time):
    """从 API 获取使用统计数据"""
    # URL 编码参数
    params = urllib.parse.urlencode({
        'startTime': start_time,
        'endTime': end_time
    })
    url = f'https://api.z.ai/api/monitor/usage/model-usage?{params}'

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
        return None
    except urllib.error.URLError as e:
        print(f"{Colors.FAIL}错误: 无法连接到服务器 - {e.reason}{Colors.ENDC}")
        return None
    except json.JSONDecodeError as e:
        print(f"{Colors.FAIL}错误: 无法解析 API 响应 - {e}{Colors.ENDC}")
        return None


def aggregate_daily_usage(data):
    """将按小时的使用数据聚合为按天"""
    if not data or not data.get('success'):
        return None

    try:
        x_times = data.get('data', {}).get('x_time', [])
        tokens_usage = data.get('data', {}).get('tokensUsage', [])
        total_usage = data.get('data', {}).get('totalUsage', {})

        # 按日期聚合
        daily_totals = {}
        for i, time_str in enumerate(x_times):
            # 提取日期部分 (YYYY-MM-DD)
            date_str = time_str.split(' ')[0]
            token_value = tokens_usage[i]

            if token_value is not None:
                if date_str not in daily_totals:
                    daily_totals[date_str] = 0
                daily_totals[date_str] += token_value

        return {
            'daily': daily_totals,
            'total': total_usage.get('totalTokensUsage', 0)
        }
    except (AttributeError, TypeError):
        return None


def get_today_date():
    """获取今天的日期字符串（本地时间）"""
    return datetime.now().strftime('%Y-%m-%d')


def get_display_width(text):
    """计算字符串在终端中的实际显示宽度（中文=2，英文=1）"""
    width = 0
    for char in text:
        # 中文字符、中文标点等占用2个宽度
        if '\u4e00' <= char <= '\u9fff' or char in '（）：，。、；''""【】《》':
            width += 2
        else:
            width += 1
    return width


def print_daily_usage_summary(usage_data):
    """打印今日和历史总计使用量"""
    if not usage_data:
        print(f"{Colors.WARNING}📈 消耗统计: 暂无数据{Colors.ENDC}\n")
        return

    today = get_today_date()
    daily = usage_data.get('daily', {})
    total = usage_data.get('total', 0)

    today_usage = daily.get(today, 0)

    print(f"{Colors.OKBLUE}{Colors.BOLD}📈 消耗统计:{Colors.ENDC}")
    print(f"  今日已用: {format_number(today_usage)} tokens")
    print(f"  历史总计: {format_number(total)} tokens\n")


def print_weekly_usage(usage_data, days=7):
    """打印最近 N 天的使用情况"""
    if not usage_data:
        return

    daily = usage_data.get('daily', {})
    if not daily:
        return

    # 获取最近 N 天的日期列表（倒序）
    today = datetime.now()
    date_list = []
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        date_list.append((date_str, date))

    # 找出最大值用于进度条比例
    max_usage = max(daily.values()) if daily else 1
    if max_usage == 0:
        max_usage = 1

    print(f"{Colors.OKBLUE}{Colors.BOLD}📅 最近 {days} 天消耗:{Colors.ENDC}")

    for i, (date_str, date) in enumerate(date_list):
        usage = daily.get(date_str, 0)

        # 生成日期标签
        if i == 0:
            label = f"{date_str} (今天)"
        elif i == 1:
            label = f"{date_str} (昨天)"
        else:
            weekday = date.strftime('%a')
            label = f"{date_str} ({weekday})"

        # 创建进度条（相对最大值）
        if max_usage > 0:
            bar_width = int(30 * usage / max_usage)
        else:
            bar_width = 0

        progress_bar = Colors.OKGREEN + '█' * bar_width + Colors.GRAY_BAR + '░' * (30 - bar_width) + Colors.ENDC

        # 格式化使用量（带千位分隔符）
        usage_str = format_number(usage)

        # 计算需要的空格数来对齐（目标宽度24）
        label_width = get_display_width(label)
        padding = 24 - label_width
        padding_str = ' ' * max(0, padding)

        print(f"  {label}{padding_str} {progress_bar} {usage_str}")
    print()


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Z.AI API 配额查询工具')
    parser.add_argument('-w', '--show-weekly', action='store_true',
                        help='显示最近 7 天的 token 消耗详情')
    parser.add_argument('-d', '--days', type=int, default=7,
                        help='显示最近 N 天的消耗数据（默认: 7）')
    args = parser.parse_args()

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

    # 获取使用统计数据（最近 N 天）
    days_to_fetch = args.days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_to_fetch - 1)

    start_time_str = start_date.strftime('%Y-%m-%d') + ' 00:00:00'
    end_time_str = end_date.strftime('%Y-%m-%d') + ' 23:59:59'

    usage_data_response = fetch_usage_data(token, start_time_str, end_time_str)
    aggregated_usage = aggregate_daily_usage(usage_data_response)

    # 显示今日和总计
    print_daily_usage_summary(aggregated_usage)

    # 如果指定了 --show-weekly，显示最近 N 天详情
    if args.show_weekly and aggregated_usage:
        print_weekly_usage(aggregated_usage, days=args.days)

    # 打印底部
    print_footer()


if __name__ == '__main__':
    main()
