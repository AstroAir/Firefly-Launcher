import sys
import json
import subprocess
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QDesktopServices, QFont
from PySide6.QtCore import Qt, QUrl, QSize, QProcess
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (Pivot, qrouter, ScrollArea, CustomColorSettingCard, PushButton, OptionsSettingCard,
                            setThemeColor, PrimaryPushSettingCard, TitleLabel, SubtitleLabel, setCustomStyleSheet,
                            SwitchSettingCard, InfoBar, InfoBarPosition, ComboBoxSettingCard)
from app.model.setting_card import SettingCardGroup, LineEditSettingCard_Port
from app.model.style_sheet import StyleSheet
from app.model.check_update import checkUpdate
from app.model.config import cfg, get_json


class Setting(ScrollArea):
    Nav = Pivot
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.setObjectName(text)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        # 栏定义
        self.pivot = self.Nav(self)
        self.stackedWidget = QStackedWidget(self)

        # 添加项
        self.PersonalInterface = SettingCardGroup(self.scrollWidget)
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('主题色'),
            self.tr('默认流萤主题色，开拓者你不会改的吧?')
        )
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("DPI调整"),
            self.tr("调整全局缩放"),
            texts=["100%", "125%", "150%", "175%", "200%", self.tr("跟随系统设置")]
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('语言'),
            self.tr('设置UI界面显示语言'),
            texts=['简体中文', '繁體中文', 'English', self.tr('跟随系统设置')]
        )
        self.updateOnStartUpCard = PrimaryPushSettingCard(
            self.tr('检查更新'),
            FIF.UPDATE,
            self.tr('手动检查更新'),
            self.tr('当前版本 : ')+ cfg.APP_VERSION
        )
        self.restartCard = PrimaryPushSettingCard(
            self.tr('重启程序'),
            FIF.ROTATE,
            self.tr('重启程序'),
            self.tr('无奖竞猜，存在即合理')
        )
        self.FunctionInterface = SettingCardGroup(self.scrollWidget)
        self.autoCopyCard = SwitchSettingCard(
            FIF.COPY,
            self.tr('命令自动复制'),
            self.tr('选择命令时，自动复制命令到剪贴板'),
            configItem=cfg.autoCopy
        )
        self.useLoginCard = SwitchSettingCard(
            FIF.PENCIL_INK,
            self.tr('启用登录功能'),
            self.tr('使用自定义登陆彩蛋'),
            configItem=cfg.useLogin
        )
        self.useAudioCard = SwitchSettingCard(
            FIF.MUSIC,
            self.tr('启用流萤语音(外部)'),
            self.tr('使用随机流萤语音彩蛋'),
            configItem=cfg.useAudio
        )
        self.ProxyInterface = SettingCardGroup(self.scrollWidget)
        self.proxyCard = SwitchSettingCard(
            FIF.CERTIFICATE,
            self.tr('使用代理端口'),
            self.tr('启用代理，在配置文件里更改地址'),
            configItem=cfg.proxyStatus
        )
        self.proxyPortCard = LineEditSettingCard_Port(
            self.tr('代理端口')
        )
        self.chinaCard = SwitchSettingCard(
            FIF.CALORIES,
            self.tr('使用国内镜像'),
            self.tr('为Github下载启用国内镜像站链接'),
            configItem=cfg.chinaStatus
        )
        self.noproxyCard = PrimaryPushSettingCard(
            self.tr('重置'),
            FIF.POWER_BUTTON,
            self.tr('重置代理'),
            self.tr('重置部分服务端未关闭的代理')
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
        self.__initInfo()
        self.__connectSignalToSlot()

    def __initLayout(self):
        # 项绑定到栏目
        self.PersonalInterface.addSettingCard(self.themeColorCard)
        self.PersonalInterface.addSettingCard(self.zoomCard)
        self.PersonalInterface.addSettingCard(self.languageCard)
        self.PersonalInterface.addSettingCard(self.updateOnStartUpCard)
        self.PersonalInterface.addSettingCard(self.restartCard)
        self.FunctionInterface.addSettingCard(self.autoCopyCard)
        self.FunctionInterface.addSettingCard(self.useLoginCard)
        self.FunctionInterface.addSettingCard(self.useAudioCard)
        self.ProxyInterface.addSettingCard(self.proxyCard)
        self.ProxyInterface.addSettingCard(self.proxyPortCard)
        self.ProxyInterface.addSettingCard(self.chinaCard)
        self.ProxyInterface.addSettingCard(self.noproxyCard)

        # 栏绑定界面
        self.addSubInterface(self.PersonalInterface,'PersonalInterface',self.tr('程序'), icon=FIF.SETTING)
        self.addSubInterface(self.FunctionInterface,'FunctionInterface',self.tr('功能'), icon=FIF.TILES)
        self.addSubInterface(self.ProxyInterface, 'ProxyInterface',self.tr('代理'), icon=FIF.CERTIFICATE)
        self.AboutInterface = About('AboutInterface', self)
        self.addSubInterface(self.AboutInterface, 'AboutInterface',self.tr('关于'), icon=FIF.INFO)

        # 初始化配置界面
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setSpacing(15)
        self.vBoxLayout.setContentsMargins(0, 10, 10, 0)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.PersonalInterface)
        self.pivot.setCurrentItem(self.PersonalInterface.objectName())
        qrouter.setDefaultRouteKey(self.stackedWidget, self.PersonalInterface.objectName())
    
    def __initInfo(self):
        port = get_json('./config/config.json', 'PROXY_PORT')
        self.proxyPortCard.titleLabel.setText(self.tr('代理端口 (当前: ') + port + ')')
        if not cfg.proxyStatus.value:
            self.proxyPortCard.setDisabled(True)
        
    def __connectSignalToSlot(self):
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c, lazy=True))
        self.zoomCard.comboBox.currentIndexChanged.connect(self.restart_application)
        self.languageCard.comboBox.currentIndexChanged.connect(self.restart_application)
        self.updateOnStartUpCard.clicked.connect(lambda: checkUpdate(self.parent))
        self.restartCard.clicked.connect(self.restart_application)
        self.autoCopyCard.checkedChanged.connect(lambda: self.common_changed(cfg.autoCopy.value, self.tr('自动复制功能已开启！'), self.tr('自动复制功能已关闭！')))
        self.useLoginCard.checkedChanged.connect(lambda: self.common_changed(cfg.useLogin.value, self.tr('登录功能已开启！'), self.tr('登录功能已关闭！')))
        self.useAudioCard.checkedChanged.connect(lambda: self.common_changed(cfg.useAudio.value, self.tr('流萤语音已开启！'), self.tr('流萤语音已关闭！')))
        self.proxyCard.checkedChanged.connect(lambda: self.common_changed(cfg.proxyStatus.value,self.tr('代理端口已开启！'),self.tr('代理端口已关闭！'),True))
        self.proxyPortCard.set_port.connect(self.handleSetProxyPort)
        self.chinaCard.checkedChanged.connect(lambda: self.common_changed(cfg.chinaStatus.value,self.tr('国内镜像已开启！'),self.tr('国内镜像已关闭！'),True))
        self.noproxyCard.clicked.connect(self.disable_global_proxy)

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

    def restart_application(self):
        current_process = QProcess()
        current_process.startDetached(sys.executable, sys.argv)
        sys.exit()
    
    def common_changed(self, status, title_true, title_false, isproxy=False):
        if status:
            InfoBar.success(
                title=title_true,
                content="",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=1000,
                parent=self
            )
        else:
            InfoBar.success(
                title=title_false,
                content="",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=1000,
                parent=self
            )
        if cfg.proxyStatus.value:
            self.proxyPortCard.setDisabled(False)
        else:
            self.proxyPortCard.setDisabled(True)
        if isproxy and cfg.chinaStatus.value and cfg.proxyStatus.value:
            InfoBar.warning(
                title=self.tr("代理设置冲突,优先使用国内镜像！"),
                content="",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=1000,
                parent=self
            )

    def disable_global_proxy(self):
        try:
            if cfg.proxyStatus.value:
                port = get_json('./config/config.json', 'PROXY_PORT')
                subprocess.run('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(f'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "127.0.0.1:{port}" /f', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.run('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run('reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "" /f', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            InfoBar.success(
                title=self.tr('全局代理已更改！'),
                content="",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=1000,
                parent=self
            )
        except:
            InfoBar.error(
                title=self.tr('全局代理关闭失败！'),
                content="",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def handleSetProxyPort(self):
        new_port = self.proxyPortCard.port_edit.text()
        if new_port != '':
            with open('config/config.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                data['PROXY_PORT'] = new_port
            with open('config/config.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        self.proxyPortCard.titleLabel.setText(self.tr('代理端口 (当前: ') + new_port + ')')


class About(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        
        main_layout = QVBoxLayout(self)
        self.setObjectName(text)
        
        image_layout = QVBoxLayout()
        image_widget = RoundedImageWidget("./src/image/bg_about.png")
        image_layout.addWidget(image_widget)
        image_widget.setFixedSize(1080, 540)
        image_layout.setAlignment(Qt.AlignHCenter)

        # APP信息
        info_layout = QVBoxLayout()
        self.info_name = TitleLabel(cfg.APP_NAME)
        self.info_version = SubtitleLabel(cfg.APP_VERSION)
        self.info_name.setFont(QFont(f'{cfg.APP_FONT}', 35))
        self.info_version.setFont(QFont(f'{cfg.APP_FONT}', 20))
        self.info_name.setContentsMargins(0, 25, 0, 0)
        self.info_version.setContentsMargins(0, 10, 0, 20)
        info_layout.addWidget(self.info_name, alignment=Qt.AlignHCenter)
        info_layout.addWidget(self.info_version, alignment=Qt.AlignHCenter)

        # Github链接
        info_button_layout = QHBoxLayout()
        link_writer = PushButton(FIF.HOME, self.tr('   作者主页'))
        link_repo = PushButton(FIF.GITHUB, self.tr('   Github项目'))
        link_releases = PushButton(FIF.MESSAGE, self.tr('   版本发布'))
        link_issues = PushButton(FIF.HELP, self.tr('   反馈交流'))

        for link_button_name in ['link_writer', 'link_repo', 'link_releases', 'link_issues']:
            eval(link_button_name).setFixedSize(270, 70)
            eval(link_button_name).setIconSize(QSize(18, 18))
            eval(link_button_name).setFont(QFont(f'{cfg.APP_FONT}', 12))
            setCustomStyleSheet(eval(link_button_name), 'PushButton{border-radius: 12px}', 'PushButton{border-radius: 12px}')
            info_button_layout.addWidget(eval(link_button_name))
            eval(link_button_name).clicked.connect(eval('self.' + link_button_name))

        main_layout.addLayout(image_layout)
        main_layout.addLayout(info_layout)
        main_layout.addLayout(info_button_layout)

    def link_writer(self):
        QDesktopServices.openUrl(QUrl(cfg.URL_WRITER))
    def link_repo(self):
        QDesktopServices.openUrl(QUrl(cfg.URL_REPO))
    def link_releases(self):
        QDesktopServices.openUrl(QUrl(cfg.URL_RELEASES))
    def link_issues(self):
        QDesktopServices.openUrl(QUrl(cfg.URL_ISSUES))


class RoundedImageWidget(QWidget):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent=parent)
        self.image_path = image_path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pixmap = QPixmap(self.image_path)

        path = QPainterPath()
        path.addRoundedRect(self.rect(), 35, 35)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self.width(), self.height(), pixmap)