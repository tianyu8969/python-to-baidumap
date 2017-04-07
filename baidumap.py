# 百度地图：http://map.baidu.com/  百度地图poi：http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi
# coding:utf-8
# github:https://github.com/tianyu8969/python-to-baidumap
# *注意* 百度最多返回400条记录

import json
import xlwt
from datetime import datetime
from urllib import request
from urllib.parse import quote
import sys
import time

# 获取当前日期
today = datetime.today()
# 将获取到的datetime对象仅取日期如：2017-4-6
today_date = datetime.date(today)

json_name = 'data_tmap.json'
# 百度地图poi：http://api.map.baidu.com/place/v2/search
# 请替换为自己申请的key值：申请Web服务API类型KEY http://lbsyun.baidu.com/apiconsole/key?application=key
# ak=8VUjfqGwgnHwEZLxwPpnZvO1Sgeq2HFO
# http://api.map.baidu.com/place/v2/search?query=卫生服务中心&tag=医疗&page_size=20&page_num=0&scope=2&region=上海&coord_type=3&output=json&ak=8VUjfqGwgnHwEZLxwPpnZvO1Sgeq2HFO
url_amap = 'http://api.map.baidu.com/place/v2/search?query=卫生服务中心&tag=医疗&page_size=20&page_num=0&scope=2&region=上海市&coord_type=3&output=json&ak=8VUjfqGwgnHwEZLxwPpnZvO1Sgeq2HFO'
page_size = 20  # 每页条目数，最大限制为20条
page_index = r'page_num=1'  # 显示页码
total_record = 0  # 定义全局变量，总行数，百度有限制不能超过400条
# Excel表头
hkeys = ['id', '医院名称', '医院类型', '详情网址', '医院地址', '联系电话', '北纬', '东经']
# 获取数据列
bkeys = ['uid', 'name', ['detail_info', 'tag', 'detail_url'], 'address', 'telephone', ['location', 'lat', 'lng']]

u"""
        城市内检索
        百度在没有查找到对应查询请求时, 会返回在其它城市查找到的结果, 返回格式为[{'num': , 'name': ''} ...]这样的数组
        获取一页query相关地理信息
        根据关键词query查找所有地址信息
        *注意* 百度最多返回400条记录
        :param query: 查询关键词
        :param region: 地区
        :param kwargs:
        :return:  if success return
            {
                status: 本次API访问状态, 成功返回0, 其他返回其他数字,
                message: 对本次API访问状态值的英文说明, 如果成功返回'ok', 失败返回错误说明,
                total: 检索总数, 用户请求中设置了page_num字段时才会出现, 当检索总数超过760时, 多次刷新同一请求得到的total值, 可能稍有不同
                results: [
                    {
                        name:  POI名称,
                        location: {
                            lat: 纬度,
                            lng: 经度
                        },
                        address: POI地址信息,
                        telephone: POI电话信息,
                        uid: POI的唯一标识,
                        detail_info: {  # POI扩展信息, 仅当scope=2时, 显示该字段, 不同POI类型, 显示的detail_info字段不同
                            distance: 距离中心点距离,
                            type: POI类型,
                            tag: 标签,
                            detail_url: POI的详情页,
                            price: POI商户的价格,
                            shop_hours: 营业时间,
                            overall_rating: 总体评分,
                            taste_rating: 口味评分,
                            service_rating: 服务评分,
                            environment_rating: 环境评分,
                            facility_rating: 星级评分,
                            hygiene_rating: 卫生评分,
                            technology_rating: 技术评分,
                            image_num: 图片数,
                            groupon_num: 团购数,
                            discount_num: 优惠数,
                            comment_num: 评论数,
                            favorite_num: 收藏数,
                            checkin_num: 签到数
                        }
                    }
                    ...
                ]
            }
            else return None.
        """
# 获取数据
def get_data(pageindex):
    global total_record
    # 暂停500毫秒，防止过快取不到数据
    time.sleep(0.5)
    print('解析页码： ' + str(pageindex) + ' ... ...')
    url = url_amap.replace('pageindex', str(pageindex))
    # 中文编码
    url = quote(url, safe='/:?&=')
    html = ""
    with request.urlopen(url) as f:
        html = f.read()
    rr = json.loads(html)
    if total_record == 0:
        total_record = int(rr['total'])
    return rr['results']


def getPOIdata():
    global total_record
    print('获取POI数据开始')
    josn_data = get_data(1)
    if (total_record % page_size) != 0:
        page_number = int(total_record / page_size) + 2
    else:
        page_number = int(total_record / page_size) + 1

    with open(json_name, 'w') as f:
        # 去除最后]
        f.write(json.dumps(josn_data).rstrip(']'))
        print('已保存到json文件：' + json_name)
        for each_page in range(2, page_number):
            html = json.dumps(get_data(each_page)).lstrip('[').rstrip(']')
            if html:
                html = "," + html
            f.write(html)
            print('已保存到json文件：' + json_name)
        f.write(']')
    print('获取POI数据结束')


# 写入数据到excel
def write_data_to_excel(name):
    # 从文件中读取数据
    fp = open(json_name, 'r')
    result = json.loads(fp.read())
    # 实例化一个Workbook()对象(即excel文件)
    wbk = xlwt.Workbook()
    # 新建一个名为Sheet1的excel sheet。此处的cell_overwrite_ok =True是为了能对同一个单元格重复操作。
    sheet = wbk.add_sheet('Sheet1', cell_overwrite_ok=True)

    # 创建表头
    # for循环访问并获取数组下标enumerate函数
    for index, hkey in enumerate(hkeys):
        sheet.write(0, index, hkey)

    # 遍历result中的每个元素。
    for i in range(len(result)):
        values = result[i]
        n = i + 1
        index = 0
        for key in bkeys:
            val = ""
            islist = type(key) == list
            if islist:
                keyv = key[0]  # 获取属性
                key = key[1:]  # 切片，从第一个开始
                for ki, kv in enumerate(key):
                    val = values[keyv][kv]
                    sheet.write(n, index, val)
                    index = index + 1
            # 判断是否存在属性key
            elif key in values.keys():
                val = values[key]
                sheet.write(n, index, val)
            if not islist:
                index = index + 1
    wbk.save(name + str(today_date) + '.xls')
    print('保存到excel文件： ' + name + str(today_date) + '.xls ！')


if __name__ == '__main__':
    # 写入数据到json文件，第二次运行可注释
    getPOIdata()
    # 读取json文件数据写入到excel
    write_data_to_excel("上海卫生服务中心-百度地图")
