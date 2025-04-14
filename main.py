import os
import time
import requests
from urllib.parse import quote
from dotenv import load_dotenv

def get_gold_price_html():
    try:
        # 使用真实浏览器头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 请求数据
        response = requests.get(
            "https://www.5huangjin.com/data/jin.js",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        # 数据解析
        data_str = response.text.split('="')[1].split('"')[0]
        fields = data_str.split(',')
        
        # 类型转换处理
        def to_float(s):
            try:
                return float(s)
            except:
                return 0.0

        # 字段映射
        latest_price = to_float(fields[0])        # 最新价
        today_open = to_float(fields[8])          # 今开盘价
        today_high = to_float(fields[4])          # 最高价
        today_low = to_float(fields[5])           # 最低价
        yesterday_settle = to_float(fields[7])    # 昨日结算价
        
        # 计算涨跌
        increase_amount = latest_price - yesterday_settle
        increase_percent = round((increase_amount / yesterday_settle) * 100, 3) if yesterday_settle else 0

        return {
            "datetime": f"{fields[12]} {fields[6]}",   # 日期 + 时间
            "latest": latest_price,
            "open": today_open,
            "high": today_high,
            "low": today_low,
            "settlement": yesterday_settle,
            "change": {
                "amount": round(increase_amount, 2),
                "percent": increase_percent
            },
            "volume": int(fields[9])              # 成交量
        }
    
    except Exception as e:
        print(f"[ERROR] 数据获取失败: {str(e)}")
        return None  # 统一返回None

def bark_push(device_key: str, message: str, title: str = "金价监控", sound: bool = True):
    """
    Bark推送函数
    :param device_key: 设备密钥
    :param message: 推送内容（支持Markdown）
    :param title: 通知标题（默认"金价监控"）
    :param sound: 是否启用提示音（默认True）
    :return: 推送是否成功
    """
    try:
        # 构造请求URL
        base_url = f"https://api.day.app/{device_key.strip()}/"
        encoded_message = quote(message, safe='')  # 自动处理特殊字符
        
        # 添加可选参数
        params = {
            "group": title,  # 消息分组
            "level": "timeSensitive",  # 时效性通知(iOS15+)
            "url": "https://www.5huangjin.com/cn/",
        }
        if title:
            params["title"] = title
        if not sound:
            params["sound"] = "silent"
        
        # 发送请求
        response = requests.get(
            f"{base_url}{encoded_message}", 
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            print("推送成功")
            return True
        print(f"推送失败，状态码：{response.status_code}")
        return False
    
    except Exception as e:
        print(f"推送异常：{str(e)}")
        return False    

def monitor_gold_price(interval=3600):  # 单位：秒
    while True:
        start_time = time.time()
        
        data = get_gold_price_html()
        if data:
            msg = (
                f"[{data['datetime']}]\n"
                f"• 最新价: {data['latest']} 元/克\n"
                f"• 涨跌: {data['change']['amount']} 元 ({data['change']['percent']}%)\n"
                f"• 区间: {data['low']} ~ {data['high']} 元/克\n"
                f"• 昨收: {data['settlement']} 元/克\n"
                f"• 成交量: {data['volume']:,} 手"
            )
            
            # 本地打印
            print(msg)

            # 推送到手机
            barkKey = os.environ.get("BARK_KEY")
            if barkKey:
                bark_push(barkKey, msg, '中国上海黄金交易所')

        else:
            print("获取数据失败，等待重试...")
        
        # 精确间隔控制
        elapsed = time.time() - start_time
        sleep_time = max(interval - elapsed, 0)
        time.sleep(sleep_time)

if __name__ == "__main__":
    load_dotenv()
    monitor_gold_price()