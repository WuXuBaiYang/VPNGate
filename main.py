import requests
from lxml import html
import os
from fake_useragent import UserAgent

# 模拟useragent
fake_user_agent = UserAgent(use_cache_server=False)
# 基础地址
base_url = "http://www.vpngate.net/en/"
# 基础图片地址
base_image_url = "http://www.vpngate.net/images/flags/"


class VPNModel:
    """
    vpn数据对象
    """
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
    # 代理提供者的留言
    volunteer_operator_message = ""
    # 服务器评分
    score = ""


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
    vpn_model = VPNModel()
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
            vpn_model.line_quality = "..."
            # 累计流量
            vpn_model.cumulative_transfers = "..."
            # 日志策略
            vpn_model.logging_policy = "..."
            pass
        elif index == 4:
            # SSL-VPN是否支持
            vpn_model.ssl_vpn = None
            # SSL-VPN的tcp端口
            vpn_model.ssl_vpn_tcp = "..."
            # SSL-VPN是否支持udp
            vpn_model.ssl_vpn_udp = "..."
            pass
        elif index == 5:
            # L2TP/IPsec是否支持
            vpn_model.l2tp_ipsec = None
            pass
        elif index == 6:
            # OpenVPN是否支持
            vpn_model.open_vpn = None
            # OpenVPN的tcp端口
            vpn_model.open_vpn_tcp = "..."
            # OpenVPN的udp端口
            vpn_model.open_vpn_udp = "..."
            pass
        elif index == 7:
            # MS-SSTP是否支持
            vpn_model.ms_sstp = None
            # MS-SSTP的主机名
            vpn_model.ms_sstp_host_name = "..."
            pass
        elif index == 8:
            # 代理提供者的名称
            vpn_model.volunteer_operator_name = "..."
            # 代理提供者的浏览
            vpn_model.volunteer_operator_message = "..."
            pass
        elif index == 9:
            # 服务器评分
            vpn_model.score = "..."
            pass
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
        param_list = cell.xpath(".//td")
        # header的属性只有1个，所以属性数量大于1的就是需要用到的参数集合
        if len(param_list) > 0 and len(param_list[0].attrib) > 1:
            parse_vpn_param(param_list)
    pass


# 入口
if __name__ == "__main__":
    parse_vpn_gate_page(base_url)
