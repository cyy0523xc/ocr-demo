# -*- coding: utf-8 -*-
"""
@author: Alex
"""
import re
from os import remove
from PIL import Image
import json
import time
from uuid import uuid1
import web

import model

render = web.template.render('templates')
web.config.debug = True
urls = ('/ocr', 'OCR')

# 身份证正则匹配
zh = '[\u4E00-\u9FA5]'
idcard_conf = [
    "^姓名(?P<姓名>%s{3,4})$" % zh,
    "^性别(?P<性别>%s)民族(?P<民族>%s{1,5})$" % (zh, zh),
    "^出生(?P<年>\\d{4,4})年(?P<月>\\d{1,2})月(?P<日>\\d{1,2})日$",
    "^住址(?P<住址>.*)$",
    "^公民身份号码(?P<公民身份号码>\\d{17,17}[\\dA-Z])$",
]


def image_to_text(img):
    """OCR识别"""
    img = img.convert("RGB")
    W, H = img.size
    model_config = dict(
        MAX_HORIZONTAL_GAP=80,   # 字符之间的最大间隔，用于文本行的合并
        MIN_V_OVERLAPS=0.6,
        MIN_SIZE_SIM=0.6,
        TEXT_PROPOSALS_MIN_SCORE=0.2,
        TEXT_PROPOSALS_NMS_THRESH=0.3,
        TEXT_LINE_NMS_THRESH=0.99,  # 文本行之间测iou值
        MIN_RATIO=1.0,
        LINE_MIN_SCORE=0.2,
        TEXT_PROPOSALS_WIDTH=0,
        MIN_NUM_PROPOSALS=0,
    )
    _, result, angle = model.model(img,
                                   detectAngle=True,  # 是否进行文字方向检测
                                   config=model_config,
                                   leftAdjust=True,  # 对检测的文本行进行向左延伸
                                   rightAdjust=True,  # 对检测的文本行进行向右延伸
                                   alph=0.2,  # 对检测的文本行进行向右、左延伸的倍数
                                   # ifadjustDegree=True
                                   )

    res = map(lambda x: {'w': x['w'], 'h': x['h'], 'cx': x['cx'], 'cy': x['cy'],
                         'degree': x['degree'], 'text': x['text']}, result)
    res = list(res)
    return res


def parse_idcard(texts):
    """将识别的文本信息结构化
    texts:
        [{'w': 95.403797316248983,
        'h': 21.511357772772616,
        'cx': 1222.25,
        'cy': 34.25,
        'degree': 0.84618335944444922,
        'text': '识别内容'}]
    """
    data = []
    print(texts)
    for ti, text in zip(range(len(texts)), texts):
        text = text['text']
        for conf in idcard_conf:
            res = re.search(conf, text)
            if res is None:
                continue
            res = res.groupdict()
            if '住址' in res:
                # 住址可能有多行
                if len(res['住址']) > 10:
                    res['住址'] += find_address(texts, ti)

            data += list(res.items())

    print('OCR: ', data)
    return data


def find_address(texts, index):
    """处理多行地址"""
    if len(texts) <= index+1:
        return ''

    text = texts[index+1]['text']
    if re.search(idcard_conf[4], text) is not None:
        return ''   # 这是号码

    address = text
    if len(address) <= 10:
        return address
    if len(texts) <= index+2:
        return address

    text = texts[index+2]['text']
    if re.search(idcard_conf[4], text) is not None:
        return address   # 这是号码
    return address+text   # 最多往下匹配两行


class OCR:
    """通用OCR识别"""
    def GET(self):
        return render.ocr()

    def POST(self):
        x = web.input(file={})
        path = '/tmp/%s.jpg' % str(uuid1())
        if 'file' in x:
            with open(path, 'wb') as f:
                f.write(x.file.file.read())

        else:
            raise Exception('没有上传的文件')

        # OCR识别
        try:
            img = Image.open(path)
        except Exception:
            remove(path)
            raise Exception("打开文件出错")

        timeTake = time.time()
        res = image_to_text(img)
        timeTake = time.time()-timeTake

        remove(path)
        return json.dumps({'data': parse_idcard(res),
                           'waste_time': round(timeTake, 4)},
                          ensure_ascii=True)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
