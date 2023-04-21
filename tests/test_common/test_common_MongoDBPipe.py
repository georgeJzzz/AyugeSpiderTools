import pytest

from ayugespidertools.common.MongoDBPipe import Synchronize, mongodb_pipe
from ayugespidertools.common.Utils import ToolsForAyu
from ayugespidertools.Items import DataItem, MongoDataItem
from tests.conftest import mongodb_database, test_table


class TestMongoDBPipe:
    def setup_method(self):
        self._article_info = {
            "article_detail_url": DataItem("_article_detail_url", "文章详情链接"),
            "article_title": DataItem("_article_title", "文章标题"),
            "comment_count": DataItem("_comment_count", "文章评论数量"),
            "favor_count": DataItem("_favor_count", "文章赞成数量"),
            "nick_name": DataItem("_nick_name", "文章作者昵称"),
        }

    @pytest.mark.usefixtures("mongodb_conn")
    def test_MongoDBPipe_with_MongoDataItem(self, mongodb_conn):
        item_normal = MongoDataItem(
            alldata=self._article_info,
            table=test_table,
        )
        item_dict = ToolsForAyu.convert_items_to_dict(item_normal)
        mongodb_pipe(
            Synchronize(),
            item_dict=item_dict,
            db=mongodb_conn[mongodb_database],
            collection_prefix="",
        )

        num = (
            mongodb_conn[mongodb_database][test_table]
            .find({"article_detail_url": "_article_detail_url"})
            .count()
        )
        assert num >= 1

        item_with_mongo_update_rule = MongoDataItem(
            alldata=self._article_info,
            table=test_table,
            mongo_update_rule={"article_detail_url": "_article_detail_url"},
        )
        item_dict = ToolsForAyu.convert_items_to_dict(item_with_mongo_update_rule)
        mongodb_pipe(
            Synchronize(),
            item_dict=item_dict,
            db=mongodb_conn[mongodb_database],
            collection_prefix="",
        )

        num = (
            mongodb_conn[mongodb_database][test_table]
            .find({"article_detail_url": "_article_detail_url"})
            .count()
        )
        assert num >= 1

    @pytest.mark.usefixtures("mongodb_conn")
    def test_mongodb_pipe_with_dict(self, mongodb_conn):
        item_dict = {
            "alldata": self._article_info,
            "table": test_table,
            "item_mode": "MongoDB",
            "mongo_update_rule": {
                "article_detail_url": "_article_detail_url",
            },
        }
        item_dict = ToolsForAyu.convert_items_to_dict(item_dict)
        mongodb_pipe(
            Synchronize(),
            item_dict=item_dict,
            db=mongodb_conn[mongodb_database],
            collection_prefix="",
        )

        num = (
            mongodb_conn[mongodb_database][test_table]
            .find({"article_detail_url": "_article_detail_url"})
            .count()
        )
        assert num >= 1

        item_dict = {
            "table": test_table,
            "item_mode": "MongoDB",
            "mongo_update_rule": {
                "article_detail_url": "这条的查重规则应该会新增一条数据_",
            },
        }
        item_dict.update(
            {
                "article_detail_url": "_article_detail_url",
                "article_title": "_article_title",
                "comment_count": "_comment_count",
                "favor_count": "_favor_count",
                "nick_name": "_nick_name",
            }
        )
        item_dict = ToolsForAyu.convert_items_to_dict(item_dict)
        mongodb_pipe(
            Synchronize(),
            item_dict=item_dict,
            db=mongodb_conn[mongodb_database],
            collection_prefix="",
        )

        num = (
            mongodb_conn[mongodb_database][test_table]
            .find({"article_detail_url": "_article_detail_url"})
            .count()
        )
        assert num >= 2
