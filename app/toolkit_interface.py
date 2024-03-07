import os
import sys
import shutil
import subprocess
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QTextEdit, QMainWindow, QPlainTextEdit
from PySide6.QtGui import QPixmap, Qt, QPainter, QPainterPath, QDesktopServices, QFont
from PySide6.QtCore import Qt, QUrl, QSize, QProcess, QThread, Signal
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (Pivot, qrouter, ScrollArea, SettingCardGroup,
                            CustomColorSettingCard, PushButton, setThemeColor, PrimaryPushSettingCard,
                            Theme, setTheme, TitleLabel, SubtitleLabel, BodyLabel,IndeterminateProgressBar,
                            SwitchSettingCard, InfoBar, InfoBarPosition, MessageBoxBase, PlainTextEdit)
from src.common.config import cfg
from src.common.style_sheet import StyleSheet
from src.common.custom_message import MessageFiddler


class Toolkit(ScrollArea):
    Nav = Pivot
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.setObjectName(text.replace(' ', '-'))
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        # 栏定义
        self.pivot = self.Nav(self)
        self.stackedWidget = QStackedWidget(self)

        # 添加项 , 名字会隐藏(1)
        self.ProxyToolInterface = SettingCardGroup('代理', self.scrollWidget)
        self.FiddlerCard = PrimaryPushSettingCard(
            '打开',
            FIF.VPN,
            'Fiddler',
            '为Hutao-GS使用Fiddler Scripts代理网络'
        )
        self.mitmdumpCard = PrimaryPushSettingCard( 
            '打开',
            FIF.VPN,
            'Mitmdump',
            '为Grasscutter使用Mitmdump代理网络'
        )

        self.__initWidget()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)     # 水平滚动条关闭
        self.setViewportMargins(20, 0, 20, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)    # 必须设置！！！
        
        # 使用qss设置样式
        self.scrollWidget.setObjectName('scrollWidget')
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        # 项绑定到栏目(2)
        self.ProxyToolInterface.addSettingCard(self.FiddlerCard)
        self.ProxyToolInterface.addSettingCard(self.mitmdumpCard)

        # 目前无法做到导航栏各个页面独立分组 , 故隐藏组标题(3)
        self.ProxyToolInterface.titleLabel.setHidden(True)

        # 栏绑定界面(4)
        self.addSubInterface(self.ProxyToolInterface, 'ProxyToolInterface','代理', icon=FIF.CERTIFICATE)

        # 初始化配置界面
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setSpacing(28)
        self.vBoxLayout.setContentsMargins(0, 10, 10, 0)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.ProxyToolInterface)
        self.pivot.setCurrentItem(self.ProxyToolInterface.objectName())
        qrouter.setDefaultRouteKey(self.stackedWidget, self.ProxyToolInterface.objectName())
        
    def __connectSignalToSlot(self):
        self.FiddlerCard.clicked.connect(self.proxy_fiddler)
        self.mitmdumpCard.clicked.connect(self.proxy_mitmdump)

    def addSubInterface(self, widget: QLabel, objectName, text, icon=None):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            icon=icon,
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

    def open_file(self, file_path):
        if os.path.exists(file_path):
            subprocess.run(['start', file_path], shell=True)
        else:
            InfoBar.error(
                title="找不到文件，请重新下载！",
                content="",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def proxy_fiddler(self):
        w = MessageFiddler(self)
        if w.exec():
            self.open_file('src/script/yuanshen/update.exe')
            self.open_file('tool/Fiddler/Fiddler.exe')
        else:
            self.open_file('src/script/starrail/update.exe')
            self.open_file('tool/Fiddler/Fiddler.exe')
    
    def proxy_mitmdump(self):
        subprocess.run('cd ./tool/Mitmdump && start /b Proxy.exe', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)