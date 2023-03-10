import base64

import requests
from scrapy import signals

from ayugespidertools.common.MultiPlexing import ReuseOperation
from ayugespidertools.common.Params import Param


class ExclusiveProxyDownloaderMiddleware(object):
    """
    独享代理中间件
    """

    def __init__(self, exclusive_proxy_config):
        """
        初始化独享代理设置
        Args:
            exclusive_proxy_config: 使用的独享代理的配置信息
        """
        self.proxy = None
        # 查看独享代理配置是否符合要求
        is_match = ReuseOperation.if_dict_meet_min_limit(
            dict_config=exclusive_proxy_config,
            key_list=["PROXY_URL", "USERNAME", "PASSWORD", "PROXY_INDEX"],
        )
        assert is_match, f"没有配置独享代理，配置示例为：{Param.exclusive_proxy_config_example}"

        self.proxy_url = exclusive_proxy_config["PROXY_URL"]
        self.username = exclusive_proxy_config["USERNAME"]
        self.password = exclusive_proxy_config["PASSWORD"]
        self.proxy_index = exclusive_proxy_config["PROXY_INDEX"]

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(
            exclusive_proxy_config=crawler.settings.get("EXCLUSIVE_PROXY_CONFIG", None)
        )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def get_proxy_ip(self):
        """获取独享代理接口的索引为 proxy_index 的代理信息"""
        try:
            r = requests.get(self.proxy_url)
            proxy_list = r.json().get("data").get("proxy_list")
            proxy_list.sort()
            if self.proxy_index < len(proxy_list):
                self.proxy = proxy_list[self.proxy_index]
            else:
                raise Exception("独享代理索引超出范围，请确认独享代理服务情况。")

        except Exception:
            raise Exception("获取独享代理是失败，请及时查看。")

    def process_request(self, request, spider):
        if request.url.startswith("https://"):
            request.meta["proxy"] = f"https://{self.proxy}"
        elif request.url.startswith("http://"):
            request.meta["proxy"] = f"http://{self.proxy}"
        else:
            spider.slog.info(f"request url error: {request.url}")

        proxy_user_pass = f"{self.username}:{self.password}"
        encoded_user_pass = "Basic " + base64.urlsafe_b64encode(
            bytes(proxy_user_pass, "ascii")
        ).decode("utf8")
        request.headers["Proxy-Authorization"] = encoded_user_pass

    def spider_opened(self, spider):
        self.get_proxy_ip()
        spider.slog.info(
            f"独享代理中间件: ExclusiveProxyDownloaderMiddleware 已开启，生效脚本为: {spider.name}，当前独享代理为: {self.proxy}"
        )