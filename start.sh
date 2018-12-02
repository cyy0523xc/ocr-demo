#!/bin/bash
# 
# 
# Author: alex
# Created Time: 2018年12月02日 星期日 19时41分39秒

sudo docker run --rm -ti -p 8080:8080 \
    -v /var/www/src/github.com/cyy0523xc/ocr-demo/static:/app/static \
    -v /var/www/src/github.com/cyy0523xc/ocr-demo/ocr.html:/app/templates/ocr.html \
    -v /var/www/src/github.com/cyy0523xc/ocr-demo/app_idcard.py:/app/app_idcard.py \
    "$1" /bin/bash
