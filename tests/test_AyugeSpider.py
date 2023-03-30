import warnings
from unittest import mock

import loguru
import pytest
from scrapy import signals
from scrapy.http import HtmlResponse, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.settings import Settings
from scrapy.spiders import CrawlSpider, Rule, Spider, XMLFeedSpider
from scrapy.utils.test import get_crawler

from ayugespidertools.common.MultiPlexing import ReuseOperation
from ayugespidertools.scraper.spiders import AyuSpider
from ayugespidertools.scraper.spiders.crawl import AyuCrawlSpider
from tests import CONSUL_CONFIG, MONGODB_CONFIG, PYMYSQL_CONFIG


class TestSpider:
    spider_class = AyuSpider
    scrapy_spider_class = Spider

    def setup_method(self):
        warnings.simplefilter("always")

    def teardown_method(self):
        warnings.resetwarnings()

    def test_base_spider(self):
        spider = self.spider_class("example.com")
        assert spider.name == "example.com"
        assert spider.start_urls == []

    def test_spider_args(self):
        """``__init__`` method arguments are assigned to spider attributes"""
        spider = self.spider_class("example.com", foo="bar")
        assert spider.foo == "bar"

    def test_spider_without_name(self):
        """``__init__`` method arguments are assigned to spider attributes"""
        with pytest.raises(ValueError):
            self.spider_class()
        with pytest.raises(ValueError):
            self.spider_class(somearg="foo")

    def test_from_crawler_crawler_and_settings_population(self):
        crawler = get_crawler()
        spider = self.spider_class.from_crawler(crawler, "example.com")
        assert hasattr(spider, "crawler")
        assert spider.crawler is crawler
        assert hasattr(spider, "settings")
        assert spider.settings is crawler.settings

    def test_from_crawler_init_call(self):
        with mock.patch.object(
            self.spider_class, "__init__", return_value=None
        ) as mock_init:
            self.spider_class.from_crawler(get_crawler(), "example.com", foo="bar")
            mock_init.assert_called_once_with("example.com", foo="bar")

    def test_closed_signal_call(self):
        class TestSpider(self.spider_class):
            closed_called = False

            def closed(self, reason):
                self.closed_called = True

        crawler = get_crawler()
        spider = TestSpider.from_crawler(crawler, "example.com")
        crawler.signals.send_catch_log(signal=signals.spider_opened, spider=spider)
        crawler.signals.send_catch_log(
            signal=signals.spider_closed, spider=spider, reason=None
        )
        assert spider.closed_called

    def test_update_settings(self):
        spider_settings = {"TEST1": "spider", "TEST2": "spider"}
        project_settings = {"TEST1": "project", "TEST3": "project"}
        self.spider_class.custom_settings = spider_settings
        settings = Settings(project_settings, priority="project")

        self.spider_class.update_settings(settings)
        assert settings.get("TEST1") == "spider"
        assert settings.get("TEST2") == "spider"
        assert settings.get("TEST3") == "project"

    def test_slog(self):
        slog_info = "this is a test log msg"
        # 创建一个 sink 对象来捕获日志消息
        sink = []
        # 配置 loguru 日志记录器
        loguru.logger.remove()
        loguru.logger.add(
            lambda message: sink.append(message), format="{message}", level="INFO"
        )

        crawler = get_crawler()
        spider = self.spider_class.from_crawler(crawler, "example.com")
        spider.slog.info(slog_info)

        # 获取捕获的日志消息
        record = sink[0]
        assert str(record).strip() == slog_info

    def test_get_mysql_config(self):
        # 测试本地 mysql 配置
        local_mysql_conf = {
            "HOST": PYMYSQL_CONFIG["host"],
            "PORT": PYMYSQL_CONFIG["port"],
            "USER": PYMYSQL_CONFIG["user"],
            "PASSWORD": PYMYSQL_CONFIG["password"],
            "CHARSET": PYMYSQL_CONFIG["charset"],
            "DATABASE": PYMYSQL_CONFIG["database"],
        }
        true_mysql_conf = {
            key.lower(): value for key, value in local_mysql_conf.items()
        }
        spider_settings = {"APP_CONF_MANAGE": False}
        project_settings = {"LOCAL_MYSQL_CONFIG": local_mysql_conf}
        self.spider_class.custom_settings = spider_settings
        settings = Settings(project_settings, priority="project")
        self.spider_class.update_settings(settings)

        spider = self.spider_class("example.com")
        mysql_conf_res = spider.get_mysql_conf(settings=settings)
        assert mysql_conf_res == true_mysql_conf

        # 测试应用管理中心 mysql 配置
        CONSUL_CONF = {
            "TOKEN": CONSUL_CONFIG["TOKEN"],
            "URL": CONSUL_CONFIG["URL"],
            "FORMAT": CONSUL_CONFIG["FORMAT"],
        }
        spider_settings = {"APP_CONF_MANAGE": True}
        project_settings = {
            "CONSUL_CONFIG": CONSUL_CONF,
        }
        self.spider_class.custom_settings = spider_settings
        settings = Settings(project_settings, priority="project")
        self.spider_class.update_settings(settings)

        consul_mysql_conf = spider.get_mysql_conf(settings)
        assert consul_mysql_conf == true_mysql_conf

    def test_get_mongodb_config(self):
        # 测试本地 mysql 配置
        local_mongodb_conf = {
            "HOST": MONGODB_CONFIG["host"],
            "PORT": MONGODB_CONFIG["port"],
            "USER": MONGODB_CONFIG["user"],
            "PASSWORD": MONGODB_CONFIG["password"],
            "AUTHSOURCE": MONGODB_CONFIG["authsource"],
            "DATABASE": MONGODB_CONFIG["database"],
        }
        true_mongodb_conf = {
            key.lower(): value for key, value in local_mongodb_conf.items()
        }
        spider_settings = {"APP_CONF_MANAGE": False}
        project_settings = {"LOCAL_MONGODB_CONFIG": local_mongodb_conf}
        self.spider_class.custom_settings = spider_settings
        settings = Settings(project_settings, priority="project")
        self.spider_class.update_settings(settings)

        spider = self.spider_class("example.com")
        mongodb_conf_res = spider.get_mongodb_conf(settings)
        assert mongodb_conf_res == true_mongodb_conf

        # 测试应用管理中心 mysql 配置
        CONSUL_CONF = {
            "TOKEN": CONSUL_CONFIG["TOKEN"],
            "URL": CONSUL_CONFIG["URL"],
            "FORMAT": CONSUL_CONFIG["FORMAT"],
        }
        spider_settings = {"APP_CONF_MANAGE": True}
        project_settings = {
            "CONSUL_CONFIG": CONSUL_CONF,
        }
        self.spider_class.custom_settings = spider_settings
        settings = Settings(project_settings, priority="project")
        self.spider_class.update_settings(settings)

        consul_mongo_conf = spider.get_mongodb_conf(settings)
        assert consul_mongo_conf == true_mongodb_conf


class TestCrawlSpider(TestSpider):
    test_body = b"""<html><head><title>Page title<title>
        <body>
        <p><a href="item/12.html">Item 12</a></p>
        <div class='links'>
        <p><a href="/about.html">About us</a></p>
        </div>
        <div>
        <p><a href="/nofollow.html">This shouldn't be followed</a></p>
        </div>
        </body></html>"""
    spider_class = AyuCrawlSpider
    scrapy_spider_class = CrawlSpider

    def test_rule_without_link_extractor(self):
        response = HtmlResponse(
            "http://example.org/somepage/index.html", body=self.test_body
        )

        class _CrawlSpider(CrawlSpider):
            name = "test"
            allowed_domains = ["example.org"]
            rules = (Rule(),)

        spider = _CrawlSpider()
        output = list(spider._requests_to_follow(response))
        assert len(output) == 3
        assert all(map(lambda r: isinstance(r, Request), output))
        assert [r.url for r in output] == [
            "http://example.org/somepage/item/12.html",
            "http://example.org/about.html",
            "http://example.org/nofollow.html",
        ]

    def test_process_links(self):
        response = HtmlResponse(
            "http://example.org/somepage/index.html", body=self.test_body
        )

        class _CrawlSpider(CrawlSpider):
            name = "test"
            allowed_domains = ["example.org"]
            rules = (Rule(LinkExtractor(), process_links="dummy_process_links"),)

            def dummy_process_links(self, links):
                return links

        spider = _CrawlSpider()
        output = list(spider._requests_to_follow(response))
        assert len(output) == 3
        assert all(map(lambda r: isinstance(r, Request), output))
        assert [r.url for r in output] == [
            "http://example.org/somepage/item/12.html",
            "http://example.org/about.html",
            "http://example.org/nofollow.html",
        ]
