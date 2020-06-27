import base64


def set_pic_data(all_pictures, target_filename):
    """
    讲包含有图片的列表中的每张图片加到目标py文件中
    :param all_pictures:
    :param target_filename:
    :return:
    """
    pic_data = []
    for pic_name in all_pictures:
        # 注意这里要把'.'转化成'_'，不然调用的时候会默认去掉'.'，导致读取失败
        new_pic_name = pic_name.replace('.', '_')
        open_pic = open("../Archive/Images/%s" % pic_name, "rb")
        # 得到转化后的b64字符串数据
        b64str = base64.b64encode(open_pic.read())
        open_pic.close()
        # 注意b64str一定要加上.decode()
        pic_data.append('%s = "%s"\n' % (new_pic_name, b64str.decode()))

    f = open(target_filename, "w+")
    for data in pic_data:
        f.write(data)
    f.close()


if __name__ == "__main__":
    pics = ['background.png', 'favicon.ico']
    set_pic_data(pics, 'PicData.py')
    print("success!")
