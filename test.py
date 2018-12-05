# -*- coding: utf-8 -*-
#
# 测试
# Author: alex
# Created Time: 2018年12月05日 星期三 11时52分13秒
from PIL import Image
from app_idcard import image_to_text


def recognice(path):
    img = Image.open(path)
    text = image_to_text(img)
    return text


if __name__ == '__main__':
    import sys
    text = recognice(sys.argv[1])
    print(text)
