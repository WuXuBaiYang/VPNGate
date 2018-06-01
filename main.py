import requests
from lxml import html
import os
from fake_useragent import UserAgent

# 模拟useragent
fake_user_agent = UserAgent(use_cache_server=False)
# 基础地址
base_url = "http://www.vpngate.net/cn/"
# 基础图片地址
base_image_url = "http://www.vpngate.net/images/flags/"


def get_headers():
    """
    获取头部参数
    :return: 返回头部参数
    """
    return {"User-Agent": fake_user_agent.random}


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


def parse_vpn_param(param_list):
    """
    解析vpn参数
    :param param_list: 参数集合
    :return:
    """
    for index in range(len(param_list)):
        param = param_list[index]
        if index == 0:
            # 国家 / 地区 (物理位置)
            national_flag_url = base_image_url + os.path.basename(get_first_attr(param, "img", "src"))
            country = get_first_attr_tail(param, "br")
            print("国旗：", national_flag_url, "\t国家：", country, end="", sep="")
            pass
        elif index == 1:
            # DDNS 主机名 IP 地址 (ISP 主机名)
            pass
        elif index == 2:
            # VPN 会话数 运行时间 累计用户数
            pass
        elif index == 3:
            # 线路质量 吞吐量和 Ping 累积转移 日志策略
            pass
        elif index == 4:
            # SSL-VPN Windows (合适的)
            pass
        elif index == 5:
            # L2TP/IPsec Windows, Mac,iPhone, Android 无需 VPN 客户端
            pass
        elif index == 6:
            # OpenVPN Windows, Mac,iPhone, Android
            pass
        elif index == 7:
            # MS-SSTP Windows Vista,7, 8, RT 无需 VPN 客户端
            pass
        elif index == 8:
            # 志愿者操作员的名字 (+ 操作员的消息)
            pass
        elif index == 9:
            # 总分 (质量)
            pass
    print("")
    pass


def parse_vpn_gate_page(page_url):
    """
    解析页面
    :param page_url: 页面地址
    :return:
    """
    response = http_get(page_url).content
    selector = html.fromstring(response)
    # 先获取到table中的cell
    cell_list = selector.xpath("//table[@id='vg_hosts_table_id' and not(@align)]//tr")
    for cell in cell_list:
        param_list = cell.xpath("td")
        # header的属性只有1个，所以属性数量大于1的就是需要用到的参数集合
        if len(param_list) > 0 and len(param_list[0].attrib) > 1:
            parse_vpn_param(param_list)
    pass


# 入口
if __name__ == "__main__":
    parse_vpn_gate_page(base_url)
