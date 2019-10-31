import os
import re
import requests
from lxml import etree


def get_max_page(header):
    """
    获取最大页数
    :param header: 浏览器标识
    :return: 最大页数
    """
    url = 'https://bing.ioliu.cn'
    r = requests.get(url, header)
    html = etree.HTML(r.text)
    # xpath解析获取最大页数
    max_page = html.xpath('//div[@class="page"]/span/text()')[0][4:]
    return int(max_page)


def get_pics_url(header, page):
    """
    获取一页图片的url和name
    :param header: 浏览器标识
    :param page: 网页页数
    :return: 图片信息列表
    """
    pre_url = 'https://bing.ioliu.cn/?p='
    url = pre_url + str(page)
    response = requests.get(url, headers=header)
    # xpath解析页面，拿到需要的图片url
    html = etree.HTML(response.text)
    pics_url_list = html.xpath('//div[@class="container"]/div/div/img/attribute::src')
    for i in range(len(pics_url_list)):
        # 正则表达式提取图片name
        pattern = '^.*?bing/(.*?)_ZH'
        pic_name = re.match(pattern, pics_url_list[i]).group(1)
        pic_info = [pics_url_list[i], pic_name]  # 将图片url、图片name放入同一列表中
        yield pic_info


def get_pics_content(header, pics_info_list):
    """
    根据图片url获取图片二进制数据
    :param header: 浏览器标识
    :param pics_info_list: 图片信息列表
    :return: 图片二进制数据列表
    """
    for item in pics_info_list:
        content = requests.get(item[0], headers=header).content
        pic_content = [content, item[1]]
        yield pic_content


def save_pics(path, pics_content_list):
    """
    保存图片
    :param path: 文件夹路径
    :param pics_content_list: 图片二进制流列表
    :return: none
    """
    for item in pics_content_list:
        pic_path = path + '/' + item[1] + '.jpg'
        with open(pic_path, 'wb') as f:
            f.write(item[0])
    return


def main():
    """
    main
    """
    # 创建文件夹
    path = 'bing_pics'
    try:
        os.mkdir(path)
    except FileExistsError:
        print('文件夹已存在，无需创建！')
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/78.0.3904.70 Safari/537.36'
    }
    max_page = get_max_page(header)
    # 获取输入的页数
    while True:
        page_num = input('请输入抓取的页数(目前max:' + str(max_page) + '):')
        try:
            page = int(page_num)
        except ValueError:
            print('输入有误，再次输入！')
        else:
            if 0 < page <= max_page:
                break
            else:
                print('输入有误，再次输入！')

    for i in range(1, page+1):
        pics_info_list = get_pics_url(header, i)
        pics_content_list = get_pics_content(header, pics_info_list)
        save_pics(path, pics_content_list)


if __name__ == '__main__':
    main()
