import os

import time
import requests
from lxml import html
from pymongo import MongoClient

# 基础地址
base_url = "http://www.vpngate.net/en/"
# 基础图片地址
base_image_url = "http://www.vpngate.net/images/flags/"
# 初始化mongodb客户端
mongo_client = MongoClient(host="127.0.0.1", port=27017)
vpngate_collection = mongo_client.python_spider.vpn_gate


class VPNModel:
    """
    vpn数据对象
    """

    def __init__(self, update_timestamp):
        self.update_timestamp = update_timestamp
        pass

    # 国家
    country = ""
    # 物理地址
    physical_location = ""
    # DDNS 主机名
    ddns_host_name = ""
    # IP 地址
    ip_address = ""
    # ISP 主机名
    isp_host_name = ""
    # 会话数
    vpn_sessions = ""
    # 运行时间
    up_time = ""
    # 累计用户
    cumulative_users = ""
    # 线路质量
    line_quality = ""
    # ping值
    ping = ""
    # 累计流量
    cumulative_transfers = ""
    # 日志策略
    logging_policy = ""
    # SSL-VPN是否支持
    ssl_vpn = False
    # SSL-VPN的tcp端口号
    ssl_vpn_tcp = ""
    # SSL-VPN的udp是否支持
    ssl_vpn_udp = False
    # L2TP/IPsec是否支持
    l2tp_ipsec = False
    # OPEN-VPN是否支持
    open_vpn = False
    # OPEN-VPN的tcp端口号
    open_vpn_tcp = ""
    # OPEN-VPN的udp端口号
    open_vpn_udp = ""
    # MS-SSTP是否支持
    ms_sstp = False
    # MS-SSTP的主机名
    ms_sstp_host_name = ""
    # 代理提供者名称
    volunteer_operator_name = ""
    # 服务器评分
    score = ""
    # 更新时间戳
    update_timestamp = 0


def get_headers():
    """
    获取头部参数
    :return: 返回头部参数
    """
    return {
        "User-Agent": "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"}


def get_proxies():
    """
    获取代理
    :return: 获取代理参数
    """
    return {"http": "http://127.0.0.1:1087"}


def http_get(request_url):
    """
    发起http get请求
    :param request_url: 请求地址
    :return: 返回request的请求对象
    """
    return requests.get(request_url, headers=get_headers(), proxies=get_proxies())


def get_first_attr(node, xpath, attr):
    """
    获取属性值，排除空参
    :param node:节点
    :param xpath:xpath语句
    :param attr:属性名
    :return:
    """
    target_list = node.xpath(xpath)
    if len(target_list) > 0:
        return target_list[0].get(attr)
    return ""


def get_first_attr_text(node, xpath):
    """
    获取text属性
    :param node:
    :param xpath:
    :return:
    """
    target_list = node.xpath(xpath)
    if len(target_list) > 0:
        return target_list[0].text
    return ""


def get_first_attr_tail(node, xpath):
    """
    获取tail属性
    :param node:
    :param xpath:
    :return:
    """
    target_list = node.xpath(xpath)
    if len(target_list) > 0:
        return target_list[0].tail
    return ""


def write_to_database(vpn_model):
    """
    写入到数据库
    :param vpn_model: vpngate的数据对象
    :return:
    """
    # 装类对象转换为json字符串
    model_dict = {}
    model_dict.update(vpn_model.__dict__)
    # 更新数据到数据库，存在则覆盖，不存在则插入
    vpngate_collection.update({"ip_address": vpn_model.ip_address}, model_dict, upsert=True)
    print("IP：", vpn_model.ip_address, "已插入数据库", sep="")
    pass


def parse_vpn_param(param_list):
    """
    解析vpn参数
    :param param_list: 参数集合
    :return:
    """
    vpn_model = VPNModel(time.time())
    for index in range(len(param_list)):
        param = param_list[index]
        if index == 0:
            # 国家
            vpn_model.country = base_image_url + os.path.basename(get_first_attr(param, "img", "src"))
            # 物理地址
            vpn_model.physical_location = get_first_attr_tail(param, "br")
            pass
        elif index == 1:
            for span in param.xpath(".//span"):
                span_text = span.text
                if span_text.startswith("vpn"):
                    # DDNS 主机名
                    vpn_model.ddns_host_name = span_text
                elif span_text.startswith("(") and span_text.endswith(")"):
                    # ISP 主机名
                    vpn_model.isp_host_name = span_text.lstrip("(").rstrip(")")
                else:
                    # IP 地址
                    vpn_model.ip_address = span_text
            pass
        elif index == 2:
            for span in param.xpath(".//span"):
                span_text = span.text
                if span_text.endswith("sessions"):
                    # VPN 会话数
                    vpn_model.vpn_sessions = span_text.rstrip("sessions").strip()
                else:
                    # 运行时间
                    vpn_model.up_time = span_text
            # 累计用户数
            vpn_model.cumulative_users = [br.tail for br in param.xpath("br") if br.tail is not None][0].lstrip(
                "Total").rstrip("users").strip()
            pass
        elif index == 3:
            # 线路质量
            vpn_model.line_quality = get_first_attr_text(param, ".//span")
            for b in param.xpath(".//b"):
                b_text = b.text
                if b_text is not None:
                    if b_text.endswith("ms") or b_text.endswith("-"):
                        # ping值
                        vpn_model.ping = b_text
                    elif b_text.endswith("GB"):
                        # 累计流量
                        vpn_model.cumulative_transfers = b_text
            # 日志策略
            br_list = param.xpath(".//br")
            vpn_model.logging_policy = [br_list[len(br_list) - 1].tail if len(br_list) > 0 else ""][0]
            pass
        elif index == 4:
            if len(param.xpath("./a")) > 0:
                # SSL-VPN是否支持
                vpn_model.ssl_vpn = True
                for br in param.xpath("./br"):
                    br_text = br.tail
                    if br_text.startswith("TCP:"):
                        # SSL-VPN的tcp端口
                        vpn_model.ssl_vpn_tcp = br_text.lstrip("TCP:").strip()
                    elif br_text.startswith("UDP:"):
                        # SSL-VPN是否支持udp
                        vpn_model.ssl_vpn_udp = br_text.lstrip("UDP:").strip()
            pass
        elif index == 5:
            # L2TP/IPsec是否支持
            vpn_model.l2tp_ipsec = len(param.xpath("./a")) > 0
            pass
        elif index == 6:
            if len(param.xpath("./a")) > 0:
                # OpenVPN是否支持
                vpn_model.open_vpn = True
                for br in param.xpath("./br"):
                    br_text = br.tail
                    if br_text.startswith("TCP:"):
                        # OpenVPN的tcp端口
                        vpn_model.open_vpn_tcp = br_text.lstrip("TCP:").strip()
                    elif br_text.startswith("UDP:"):
                        # OpenVPN的udp端口
                        vpn_model.open_vpn_udp = br_text.lstrip("UDP:").strip()
            pass
        elif index == 7:
            if len(param.xpath("./a")) > 0:
                # MS-SSTP是否支持
                vpn_model.ms_sstp = True
                # MS-SSTP的主机名
                vpn_model.ms_sstp_host_name = get_first_attr_text(param, ".//span[@style='color: #006600;']")
            pass
        elif index == 8:
            # 代理提供者的名称
            vpn_model.volunteer_operator_name = get_first_attr_text(param, "./i/b")
            pass
        elif index == 9:
            # 服务器评分
            vpn_model.score = get_first_attr_text(param, ".//span")
            pass
    write_to_database(vpn_model)
    pass


def parse_vpn_gate_page(page_url):
    """
    解析页面
    :param page_url: 页面地址
    :return:
    """
    print("正在请求VPNGate")
    response = http_get(page_url).content
    selector = html.fromstring(response)
    # 先获取到table中的cell
    cell_list = selector.xpath("//table[@id='vg_hosts_table_id' and not(@align)]//tr")
    for cell in cell_list:
        param_list = cell.xpath(".//td")
        # header的属性只有1个，所以属性数量大于1的就是需要用到的参数集合
        if len(param_list) > 0 and len(param_list[0].attrib) > 1:
            parse_vpn_param(param_list)
    print("VPNGate解析完成") if len(cell_list) > 0 else print("请求失败，请重试")
    pass


# 入口
if __name__ == "__main__":
    parse_vpn_gate_page(base_url)
