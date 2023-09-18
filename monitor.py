# -*- coding: UTF-8 –*-
"""
@Author: LennonChin
@Contact: i@coderap.com
@Date: 2021-10-19
"""

import sys
import os
import random
import datetime
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse


class Utils:

    @staticmethod
    def time_title(message):
        return "[{}] {}".format(datetime.datetime.now().strftime('%H:%M:%S'), message)

    @staticmethod
    def log(message):
        print(Utils.time_title(message))

    @staticmethod
    def send_message(notification_configs, message, **kwargs):
        if len(message) == 0:
            return

        # Wrapper for exception caught
        def invoke(func, configs):
            try:
                func(configs, message, **kwargs)
            except Exception as err:
                Utils.log(err)

        # DingTalk message
        invoke(Utils.send_pushdeer_message, notification_configs["pushdeer"])


    @staticmethod
    def send_pushdeer_message(pushdeer_configs, message, **kwargs):

        if len(pushdeer_configs["access_key"]) == 0:
            return
        __SendKey=pushdeer_configs["access_key"]
        url = "https://api2.pushdeer.com/message/push?pushkey=" + __SendKey + "&text=" + message

        payload = {}
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload)
        Utils.log("Pushdeer发送消息状态码：{}".format(response.status_code))


class AppleStoreMonitor:
    headers = {
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'Referer': 'https://www.apple.com.cn/shop/buy-iphone/',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
    }

    def __init__(self):
        self.count = 1
        self.timeout = 10

    @staticmethod
    def config():
        """
        进行各类配置操作
        """
        products = json.load(open('products.json', encoding='utf-8'))

        configs = {
            "selected_products": {},
            "selected_area": "",
            "exclude_stores": [],
            "notification_configs": {
                "pushdeer": {
                    "access_key": ""
                }
            },
            "scan_interval": 30,
            "alert_exception": False
        }

        while True:
            # chose product type
            print('--------------------')
            for index, item in enumerate(products):
                print('[{}] {}'.format(index, item))
            product_type = list(products)[int(input('选择要监控的产品：'))]

            # chose product classification
            print('--------------------')
            for index, (key, value) in enumerate(products[product_type].items()):
                print('[{}] {}'.format(index, key))
            product_classification = list(products[product_type])[int(input('选择要监控的产品子类：'))]

            # chose product classification
            print('--------------------')
            for index, (key, value) in enumerate(products[product_type][product_classification].items()):
                print('[{}] {}'.format(index, value))
            product_model = list(products[product_type][product_classification])[int(input('选择要监控的产品型号：'))]

            configs["selected_products"][product_model] = (
                product_classification, products[product_type][product_classification][product_model])

            print('--------------------')
            if len(input('是否添加更多产品[Enter继续添加，非Enter键退出]：')) != 0:
                break

        # config area
        print('选择计划预约的地址：')
        url_param = ['state', 'city', 'district']
        choice_params = {}
        param_dict = {}
        for step, param in enumerate(url_param):
            print('请稍后...{}/{}'.format(step + 1, len(url_param)))
            response = requests.get("https://www.apple.com.cn/shop/address-lookup", headers=AppleStoreMonitor.headers,
                                    params=choice_params)
            result_param = json.loads(response.text)['body'][param]
            if type(result_param) is dict:
                result_data = result_param['data']
                print('--------------------')
                for index, item in enumerate(result_data):
                    print('[{}] {}'.format(index, item['value']))
                input_index = int(input('请选择地区序号：'))
                choice_result = result_data[input_index]['value']
                param_dict[param] = choice_result
                choice_params[param] = param_dict[param]
            else:
                choice_params[param] = result_param

        print('正在加载网络资源...')
        response = requests.get("https://www.apple.com.cn/shop/address-lookup", headers=AppleStoreMonitor.headers,
                                params=choice_params)
        selected_area = json.loads(response.text)['body']['provinceCityDistrict']
        configs["selected_area"] = selected_area

        print('--------------------')
        print("选择的计划预约的地址是：{}，加载预约地址周围的直营店...".format(selected_area))

        store_params = {
            "location": selected_area,
            "parts.0": list(configs["selected_products"].keys())[0]
        }
        response = requests.get("https://www.apple.com.cn/shop/fulfillment-messages",
                                headers=AppleStoreMonitor.headers, params=store_params)

        stores = json.loads(response.text)['body']["content"]["pickupMessage"]["stores"]
        for index, store in enumerate(stores):
            print("[{}] {}，地址：{}".format(index, store["storeName"], store["retailStore"]["address"]["street"]))

        exclude_stores_indexes = input('排除无需监测的直营店，输入序号[直接回车代表全部监测，多个店的序号以空格分隔]：').strip().split()
        if len(exclude_stores_indexes) != 0:
            print("已选择的无需监测的直营店：{}".format("，".join(list(map(lambda i: stores[int(i)]["storeName"], exclude_stores_indexes)))))
            configs["exclude_stores"] = list(map(lambda i: stores[int(i)]["storeNumber"], exclude_stores_indexes))

        print('--------------------')
        # config notification configurations
        notification_configs = configs["notification_configs"]

        # config dingtalk notification
        pushdeer_access_key = input('输入pushdeer推送 Access Key[如不配置直接回车即可]：')


        # write pushdeer configs
        notification_configs["pushdeer"]["access_key"] = pushdeer_access_key



        # 输入扫描间隔时间
        print('--------------------')
        configs["scan_interval"] = int(input('输入扫描间隔时间[以秒为单位，默认为30秒，如不配置直接回车即可]：') or 30)

        # 是否对异常进行告警
        print('--------------------')
        configs["alert_exception"] = (input('是否在程序异常时发送通知[Y/n，默认为n]：').lower().strip() or "n") == "y"

        with open('apple_store_monitor_configs.json', 'w') as file:
            json.dump(configs, file, indent=2)
            print('--------------------')
            print("扫描配置已生成，并已写入到{}文件中\n请使用 python {} start 命令启动监控".format(file.name, os.path.abspath(__file__)))

    def start(self):
        """
        开始监控
        """
        configs = json.load(open('apple_store_monitor_configs.json', encoding='utf-8'))
        selected_products = configs["selected_products"]
        selected_area = configs["selected_area"]
        exclude_stores = configs["exclude_stores"]
        notification_configs = configs["notification_configs"]
        scan_interval = configs["scan_interval"]
        alert_exception = configs["alert_exception"]

        products_info = []
        for index, product_info in enumerate(selected_products.items()):
            products_info.append("【{}】{}".format(index, " ".join(product_info[1])))
        message = "准备开始监测，商品信息如下：\n{}\n取货区域：{}\n扫描频次：{}秒/次".format("\n".join(products_info), selected_area,
                                                                   scan_interval)
        Utils.log(message)
        # Utils.send_message(notification_configs, message)

        params = {
            "location": selected_area,
            "mt": "regular",
        }

        code_index = 0
        product_codes = selected_products.keys()
        for product_code in product_codes:
            params["parts.{}".format(code_index)] = product_code
            code_index += 1

        # 上次整点通知时间
        last_exactly_time = -1
        while True:
            available_list = []
            tm_hour = time.localtime(time.time()).tm_hour
            try:
                # 更新请求时间
                params["_"] = int(time.time() * 1000)

                response = requests.get("https://www.apple.com.cn/shop/fulfillment-messages",
                                        headers=AppleStoreMonitor.headers,
                                        params=params,
                                        timeout=self.timeout)

                json_result = json.loads(response.text)
                stores = json_result['body']['content']['pickupMessage']['stores']
                Utils.log(
                    '-------------------- 第{}次扫描 --------------------'.format(
                        self.count + 1))
                for item in stores:
                    store_name = item['storeName']
                    if item["storeNumber"] in exclude_stores:
                        print("【{}：已排除】".format(store_name))
                        continue
                    print("{:-<100}".format("【{}】".format(store_name)))
                    for product_code in product_codes:
                        pickup_search_quote = item['partsAvailability'][product_code]['pickupSearchQuote']
                        pickup_display = item['partsAvailability'][product_code]['pickupDisplay']
                        store_pickup_product_title = item['partsAvailability'][product_code]['messageTypes']['regular']['storePickupProductTitle']
                        print('\t【{}】{}'.format(pickup_search_quote, store_pickup_product_title))
                        if pickup_search_quote == '今天可取货' or pickup_display != 'unavailable':
                            available_list.append((store_name, product_code, store_pickup_product_title))

                if len(available_list) > 0:
                    messages = []
                    print("命中货源，请注意 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    Utils.log("以下直营店预约可用：")
                    for item in available_list:
                        messages.append("【{}】 {}".format(item[0], item[2]))
                        print("【{}】{}".format(item[0], item[2]))
                    print("命中货源，请注意 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

                    Utils.send_message(notification_configs,
                                       Utils.time_title(
                                           "第{}次扫描到直营店有货，信息如下：\n{}".format(self.count, "\n".join(messages))))

            except Exception as err:
                Utils.log(err)
                # 6:00 ~ 23:00才发送异常消息
                if alert_exception and 6 <= tm_hour <= 23:
                    Utils.send_message(notification_configs,
                                       Utils.time_title("第{}次扫描出现异常：{}".format(self.count, repr(err))))

            if len(available_list) == 0:
                interval = max(random.randint(int(scan_interval / 2), scan_interval * 2), 5)
                Utils.log('{}秒后进行第{}次尝试...'.format(interval, self.count))

                # 整点通知，用于阶段性检测应用是否正常
                if last_exactly_time != tm_hour and (6 <= tm_hour <= 23):
                    Utils.send_message(notification_configs,
                                       Utils.time_title("已扫描{}次，扫描程序运行正常".format(self.count)))
                    last_exactly_time = tm_hour
                time.sleep(interval)
            else:
                time.sleep(5)

            # 次数自增
            self.count += 1


if __name__ == '__main__':
    args = sys.argv

    if len(args) != 2:
        print("""
        Usage: python {} <option>
        option can be:
        \tconfig: pre config of products or notification
        \tstart: start to monitor
        """.format(args[0]))
        exit(1)

    if args[1] == "config":
        AppleStoreMonitor.config()

    if args[1] == "start":
        AppleStoreMonitor().start()
