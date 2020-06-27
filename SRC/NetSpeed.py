import sys
import os
import PyQt5
import time
from psutil import net_io_counters
from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QLabel, QMenu, qApp, QSystemTrayIcon, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon, QPixmap, QBitmap, QPainter

# 导入要用到的图片数据
from PicData import *
from base64 import b64decode

# 在这儿定义要用到的临时图片文件
temp_pic_name_list = ['background.png', 'favicon.ico']


# 格式化当前的网络流量
def net_format(traffic):
    if traffic < 1024:
        return "%.2f B/s" % traffic
    traffic /= 1024
    if traffic < 1024:
        return "%.2f KB/s" % traffic
    traffic /= 1024
    if traffic < 1024:
        return "%.2f MB/s" % traffic
    traffic /= 1024
    return "%.2f GB/s" % traffic


# 得到当前的流量信息
def get_flow():
    old = [0, 0]
    # 获取流量信息
    net_info = net_io_counters()
    recv_bytes = net_info.bytes_recv
    send_bytes = net_info.bytes_sent
    old[0], old[1] = recv_bytes, send_bytes

    time.sleep(1)
    # 获取新的流量数据
    net_info = net_io_counters()
    info = [net_info.bytes_recv - old[0], net_info.bytes_sent - old[1]]
    return info


class NetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.net_speed_label()
        self.offset = None
        # 获得在托盘上显示的部件
        self.attach_bar = QSystemTrayIcon(self)
        # 获取背景图片，这里可以根据您们自己的喜好选择自己的图片
        self.pix = QPixmap('background.png')  # 蒙版
        self.run_flag = 1
        self.init_GUI()

    def init_GUI(self):
        self.setGeometry(1250, 200, self.pix.width(), self.pix.height())
        # 设置蒙版
        self.setMask(self.pix.mask())
        # self.setWindowTitle("With Icon") # 不再需要窗口标题
        # 无边框，保持在所有应用的最上方，隐藏任务栏中的窗口提示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 设定样式(因为使用了蒙版，不再使用下列赋值语句)
        # self.setStyleSheet("background: #88B7C9;")
        # self.setStyleSheet("background: url(\"../Archive/Images/test2.png\")")
        # 网速显示部分
        self.net_speed_label()
        # start方法创建后台线程
        Thread(target=self.start).start()
        self.show()

    def paintEvent(self, event):
        paint = QPainter(self)
        paint.drawPixmap(0, 0, self.pix.width(), self.pix.height(), self.pix)

    # 一下3个函数实现鼠标的拖动
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    # 添加网速显示部分，与父窗口一样大
    def net_speed_label(self):
        self.label.resize(self.width(), self.height())
        self.label.setStyleSheet("font: 14px \"consolas\"; color: #88B7C9; margin-top: 5px")
        self.label.setAlignment(Qt.AlignCenter)

    def start(self):
        while self.run_flag:
            flow = get_flow()
            self.label.setText(net_format(flow[0]) + " ↓\n" + net_format(flow[1]) + " ↑")

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        user_quit = context_menu.addAction("退出")
        minimize = context_menu.addAction("最小化到托盘")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        # 用户单击退出
        if action == user_quit:
            self.quit()
        elif action == minimize:
            self.minimize_on_bar()

    # 自定义退出方法，主要是结束子线程的while循环
    def quit(self):
        self.run_flag = 0
        self.close()
        # 删除两张图片
        for name in temp_pic_name_list:
            os.remove(name)
        sys.exit(app.exec_())

    def show_window(self):
        # 显示窗口，隐藏托盘图标
        # 回到用户在屏幕中能看见的地方
        self.move(1250, 200)
        self.show()
        # self.attach_bar.hide() # 还是让托盘部件显示吧

    # 这儿必须是reason，看activated的库函数说明，至于为什么不能更改参数名，我也不清楚
    def icon_event(self, reason):
        # 1 是鼠标右击单击，2是左键双击，3是左键单击，4是鼠标中键
        if reason == 2 or reason == 3:
            self.show_window()

    # 添加一个托盘的处理事件
    def minimize_on_bar(self):
        # 同理，这里也可以选择你们自己喜欢的图片
        icon = QIcon("favicon.ico")
        self.attach_bar.setIcon(icon)
        # 关闭当前窗口
        self.close()
        # 新的菜单栏
        bar_menu = QMenu()
        show_window = bar_menu.addAction("显示(show)")
        user_exit = bar_menu.addAction("退出(exit)")
        # 为选项绑定事件
        show_window.triggered.connect(self.show_window)
        user_exit.triggered.connect(self.quit)
        self.attach_bar.setContextMenu(bar_menu)
        # 为托盘图标的单击或双击添加一个事件
        self.attach_bar.activated.connect(self.icon_event)
        # 显示托盘上的部件
        self.attach_bar.show()


if __name__ == "__main__":
    # 首先生成需要的两张图片，注意没有引号
    pic_name_list = [background_png, favicon_ico]
    i = 0
    for pic_name in pic_name_list:
        # 创建一个临时的图片文件
        image = open(temp_pic_name_list[i], 'wb')
        # 写入图片数据
        image.write(b64decode(pic_name))
        # 关闭流
        image.close()
        i += 1
    # 创建我们的程序
    app = QApplication(sys.argv)
    w = NetWindow()
    sys.exit(app.exec_())
