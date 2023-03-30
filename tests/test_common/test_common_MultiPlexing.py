from ayugespidertools.common.MultiPlexing import ReuseOperation
from ayugespidertools.Items import DataItem


def test_judge_str_is_json():
    data = '{"post_key1": post_value1}'
    res = ReuseOperation.judge_str_is_json(judge_str=data)
    print(res)
    data = '{"post_key1": "post_value1"}'
    res1 = ReuseOperation.judge_str_is_json(judge_str=data)
    print(res1)
    data = "post_key1=post_value1"
    res2 = ReuseOperation.judge_str_is_json(judge_str=data)
    print(res2)
    assert all([res is False, res1 is True, res2 is False])


def test_get_items_except_keys():
    dict_conf = {
        "alldata": {
            "article_title": DataItem("如何使用JavaMailSender给曾经心爱的她发送一封特别的邮件", "文章标题"),
            "comment_count": DataItem("69", "文章评论数量"),
            "favor_count": DataItem("41", "文章赞成数量"),
            "nick_name": DataItem("Binaire", "文章作者昵称"),
        },
        "table": "article_info_list",
        "item_mode": "Mysql",
    }
    res = ReuseOperation.get_items_except_keys(
        dict_conf=dict_conf, key_list=["table", "item_mode"]
    )
    print("res:", res)
    assert list(res.keys()) == ["alldata"]


def test_is_dict_meet_min_limit():
    judge_dict = {"user": "admin", "age": 18, "height": 170}
    res = ReuseOperation.is_dict_meet_min_limit(
        dict_conf=judge_dict,
        key_list=["user", "age"],
    )
    res2 = ReuseOperation.is_dict_meet_min_limit(
        dict_conf=judge_dict,
        key_list=["user", "address"],
    )
    assert all([res is True, res2 is False])


def test_get_ck_dict_from_headers():
    ck_str = (
        "__gads=ID=5667bf1cc1623793-229892aad3d400f4:T=1656574796:RT=1656574796:S=ALNI_"
        "MYD2F7TGXOAaJFaIjtXL1pKiz8IwQ; _gid=GA1.2.1261442913.1661823137; _ga_5RS2C633VL"
        "=GS1.1.1661912227.10.0.1661912227.0.0.0; _ga=GA1.1.1076553851.1656574796; __gpi="
        "UID=000007372209e6e0:T=1656574796:RT=1661912226:S=ALNI_MZkxoWl7cZYRkWzt2WKaxXQ7b47xw"
    )
    res = ReuseOperation.get_ck_dict_from_headers(headers_ck_str=ck_str)
    print("ck_dict_res:", res, type(res))
    assert res == {
        "__gads": "ID=5667bf1cc1623793-229892aad3d400f4:T=1656574796:RT=1656574796:S=ALNI_MYD2F7TGXOAaJFaIjtXL1pKiz8IwQ",
        "_gid": "GA1.2.1261442913.1661823137",
        "_ga_5RS2C633VL": "GS1.1.1661912227.10.0.1661912227.0.0.0",
        "_ga": "GA1.1.1076553851.1656574796",
        "__gpi": "UID=000007372209e6e0:T=1656574796:RT=1661912226:S=ALNI_MZkxoWl7cZYRkWzt2WKaxXQ7b47xw",
    }


def test_get_req_dict_from_scrapy():
    scrapy_body_str = "post_key1=post_value1&post_key2=post_value2"

    res = ReuseOperation.get_req_dict_from_scrapy(req_body_data_str=scrapy_body_str)
    print("req body dict:", res)
    assert res == {"post_key1": "post_value1", "post_key2": "post_value2"}


def test_get_array_dimension():
    # 二维数组
    a = [[1, 2], [3, 4]]
    # 一维数组
    b = [1, 2, 3]
    # 三维数组
    c = [[[1], [2]], [[3], [4]]]
    len1 = ReuseOperation.get_array_dimension(array=a)
    len2 = ReuseOperation.get_array_dimension(array=b)
    len3 = ReuseOperation.get_array_dimension(array=c)
    print("res len1:", len1)
    print("res len2:", len2)
    print("res len3:", len3)
    assert all([len1 == 2, len2 == 1, len3 == 3])


def test_get_array_depth():
    array = ["a", "b"]
    array_two = ["a", [1, [2, [3, 4]]], ["b", "c"]]
    array_three = ["a", (1, [2, [3, 4]]), ["b", "c"]]
    len1 = ReuseOperation.get_array_depth(array=array)
    print("len1:", len1)
    len2 = ReuseOperation.get_array_depth(array=array_two)
    print("len2:", len2)
    len3 = ReuseOperation.get_array_depth(array=array_three)
    print("len3:", len3)
    assert all([len1 == 1, len2 == 4, len3 == 4])
