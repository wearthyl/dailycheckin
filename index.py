# -*- coding: utf-8 -*-
import json
import os
import sys
import time
from datetime import datetime, timedelta

from motto import Motto
from utils.config import checkin_map, get_checkin_info, get_notice_info
from utils.message import push_message


def main_handler(event, context):
    start_time = time.time()
    utc_time = datetime.utcnow() + timedelta(hours=8)
    if "IS_GITHUB_ACTION" in os.environ:
        message = os.getenv("ONLY_MESSAGE")
        motto = os.getenv("MOTTO")
        notice_info = get_notice_info(data=None)
        check_info = get_checkin_info(data=None)
    else:
        if isinstance(event, dict):
            message = event.get("Message")
        else:
            message = None
        try:
            with open(os.path.join(os.path.dirname(__file__), "config/config.json"), "r", encoding="utf-8") as f:
                data = json.loads(f.read())
            motto = data.get("MOTTO")
            notice_info = get_notice_info(data=data)
            check_info = get_checkin_info(data=data)
        except Exception as e:
            raise e
    content_list = [f"当前时间: {utc_time}"]
    if message == "xmly":
        if check_info.get("xmly_cookie_list"):
            msg_list = checkin_map.get("XMLY_COOKIE_LIST")(xmly_cookie_list=check_info.get("xmly_cookie_list")).main()
            content_list += msg_list
    else:
        for one_check, check_func in checkin_map.items():
            if one_check not in ["XMLY_COOKIE_LIST"]:
                try:
                    if check_info.get(one_check.lower()):
                        print(f"----------已检测到正确的配置，并开始执行 {one_check} 签到----------")
                        msg_list = check_func(check_info.get(one_check.lower())).main()
                    else:
                        print(f"----------未检测到正确的配置，并跳过执行 {one_check} 签到----------")
                        msg_list = []
                except Exception as e:
                    print(e)
                    msg_list = []
                content_list += msg_list
        if motto:
            try:
                msg_list = Motto().main()
            except Exception as e:
                print(e)
                msg_list = []
            content_list += msg_list
    content_list.append(f"本次任务使用时间: {time.time() - start_time} 秒")
    if message == "xmly":
        if utc_time.hour in [9, 18] and utc_time.minute == 0:
            flag = True
        else:
            flag = False
    else:
        flag = True
    if flag:
        push_message(content_list=content_list, notice_info=notice_info)
    return


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1:
        event = {"Message": args[1]}
    else:
        event = None
    main_handler(event=event, context=None)
