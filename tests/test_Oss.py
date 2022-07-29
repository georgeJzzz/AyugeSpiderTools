#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :  test_Oss.py
@Time    :  2022/7/26 11:00
@Author  :  Ayuge
@Version :  1.0
@Contact :  ayuge.s@qq.com
@License :  (c)Copyright 2022-2023
@Desc    :  None
"""
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from ayugespidertools.Oss import AliOssBase


def test_a():
    # OssAccessKeyId, OssAccessKeySecret, Endpoint, examplebucket, operateDoc = "LTAI5tR2gK9kqPzkDsgf8EEn", "r3PAb3ES4DisPsSMIRyXhiCUxbsi6x", "https://voice-analyse.oss-cn-guangzhou.aliyuncs.com", "voice-analyse", "test"
    OssAccessKeyId, OssAccessKeySecret, Endpoint, examplebucket, operateDoc = "LTAI5tR2gK9kqPzkDsgf8EEn", "r3PAb3ES4DisPsSMIRyXhiCUxbsi6x", "https://oss-cn-guangzhou.aliyuncs.com", "voice-analyse", "test"
    ali_oss = AliOssBase(OssAccessKeyId, OssAccessKeySecret, Endpoint, examplebucket, operateDoc)

    # img_url = "https://voice-analyse.oss-cn-guangzhou.aliyuncs.com/test/%E7%BA%A2%E8%89%B2%E9%87%8E%E8%8A%B1.jpg"
    img_url = "https://static.geetest.com/captcha_v3/batch/v3/6757/2022-07-26T10/word/11875c1dd692454a82986c4cd6ed86ee.jpg"
    put_status, img_name = ali_oss.put_oss(put_bytes_or_url=img_url, file_name="test_img", file_format="jpg", file_name_md5=True)
    img_url = f'https://voice-analyse.oss-cn-guangzhou.aliyuncs.com/{operateDoc}/{img_name}.jpg'
    print(put_status, img_name, img_url)

