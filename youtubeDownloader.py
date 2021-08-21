import sys
from PyQt5.QtWidgets import QLineEdit, QHBoxLayout, QCheckBox, QMessageBox, QInputDialog, QApplication, QLabel, \
    QPushButton, QVBoxLayout, \
    QWidget, QFileDialog, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
import downloader
import time
from os import path
import subprocess

import queue  # If this template is not loaded, pyinstaller may not be able to run the requests template after packaging
import requests


################################################
def current_milli_time():
    return time.time() * 1000


################################################
class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        # region def
        super(Widget, self).__init__(*args, **kwargs)
        layout = QGridLayout(self)

        self.onSearch = True
        self.setTitle = False
        self.oldValue = 0.0
        self.time = 0.0

        self.setWindowTitle("Hi")
        self.setFixedWidth(1200)
        self.setStyleSheet("background : #161219;")

        self.url_label = QLabel()
        self.url_input = QLineEdit()

        self.des_label = QLabel()
        self.des_input = QLineEdit()

        self.index_label = QLabel()
        self.index_input = QLineEdit()

        self.check_is_list = QHBoxLayout()
        check_box_label = QLabel()
        check_box = QCheckBox()
        check_box.setChecked(True)
        check_box_label.setText("Download a list : ")
        check_box_label.setStyleSheet(self.text_style())
        self.check_is_list.addWidget(check_box_label)
        self.check_is_list.addWidget(check_box)

        self.search_btn = QPushButton()
        self.result = QPlainTextEdit()
        self.progressBar = QProgressBar()
        self.titleInfo = QLabel()

        self.openFolderBtn = QPushButton()
        self.openFolderBtn.setText("Open Folder")
        self.openFolderBtn.setStyleSheet(self.text_style())
        self.openFolderBtn.clicked.connect(self.openDownloadFolder)
        # endregion

        # region style
        self.url_input.setStyleSheet(self.text_style() + "padding : 10px 10px;")
        self.des_input.setStyleSheet(self.text_style() + "padding : 10px 10px;")
        self.index_input.setStyleSheet(self.text_style() + "padding : 10px 10px;")

        self.url_label.setText("URL :")
        self.url_label.setStyleSheet(self.text_style())

        self.des_label.setText("Destination Folder : ")
        self.des_label.setStyleSheet(self.text_style())

        self.index_label.setText("Index : ")
        self.index_label.setStyleSheet(self.text_style())

        self.titleInfo.setText("title : ")
        self.titleInfo.setStyleSheet("color : #ffffff; font-size : 14px;")

        self.result.setReadOnly(True)
        self.result.setStyleSheet(self.text_style() + "font-size : 15px;")

        self.search_btn.setText("Search")
        self.search_btn.setStyleSheet(
            "*{border : 4px solid #BC006C; " +
            "border-radius:25px;" +
            "font-size : 25px;" +
            "color : white;" +
            "padding : 15px 0px;" +
            "margin: 30px 100px;}" +
            "*:hover{background : #BC006C;}"
        )

        self.progressBar.setStyleSheet("color : black;")
        self.progressBar.setMaximum(100 * 100)
        self.progressBar.setValue(0)
        self.progressBar.setFormat("%.02f %%" % 0.0)
        self.progressBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # endregion

        isFileExist = path.isfile("last_session")
        if isFileExist:
            f = open("last_session", "r", encoding='utf-8')
            oldValues = f.read().split("\n")[0].split(" ### ")
            if len(oldValues) == 3:
                self.url_input.setText(oldValues[0])
                self.des_input.setText(oldValues[1])
                self.index_input.setText(oldValues[2])
            f.close()
        else:
            open("last_session", "w")

        self.search_btn.clicked.connect(self.on_pushButton_clicked)

        layout.addWidget(self.url_label, 0, 0)
        layout.addWidget(self.url_input, 1, 0)
        layout.addLayout(self.check_is_list, 2, 0)
        layout.addWidget(self.des_label, 3, 0)
        layout.addWidget(self.des_input, 4, 0)
        layout.addWidget(self.index_label, 5, 0)
        layout.addWidget(self.index_input, 6, 0)
        layout.addWidget(self.search_btn, 7, 0)
        layout.addWidget(self.openFolderBtn, 8, 0)
        layout.addWidget(self.titleInfo, 9, 0, 1, 3)
        layout.addWidget(self.progressBar, 10, 0, 1, 3)
        layout.addWidget(self.result, 0, 2, 8, 1)

    def openDownloadFolder(self):
        path = "E:\\bin\\youtubeDownloader\\download"
        subprocess.call(f"explorer {path}", shell=True)

    def text_style(self):
        style = "color : #ffffff;" \
                "font-size : 20px;" \
                "margin : 10px 5px;"
        return style

    def getListUrl(self, list):
        s = ""
        i = 1
        for item in list:
            s += f'--> {i} : {item}\n'
            i += 1
        return s

    def search_click(self):
        f = open("last_session", "w")
        url_input = self.url_input
        des_input = self.des_input
        index_input = self.index_input
        result = self.result
        search_btn = self.search_btn

        try:
            if url_input.text() == "":
                url_input.setStyleSheet(self.text_style() + "padding : 10px 10px; border : 1px solid #ff0000;")
                raise Exception()

            if not index_input.text().isnumeric() or int(index_input.text()) <= 0:
                index_input.setStyleSheet(self.text_style() + "padding : 10px 10px; border : 1px solid #ff0000;")
                raise Exception()

            url = url_input.text()
            folder = des_input.text()
            index = int(index_input.text())
            f.write(url + " ### ")
            f.write(folder + " ### ")
            f.write(str(index) + "\n")
            f.close()



            is_on_list = self.check_is_list.itemAt(1).widget().isChecked()

            downloader.ControllerClass.url = url
            downloader.ControllerClass.folder = "download\\" + folder + "\\"
            downloader.ControllerClass.index = index - 1
            downloader.ControllerClass.onList = is_on_list

            if not is_on_list:
                downloader.ControllerClass.index = 0
            list_items = downloader.getListFormUrl(url, is_on_list)
            #list_items = downloader.getListUrlFromFile(url, is_on_list)

            downloader.ControllerClass.urlList = list_items
            result.insertPlainText(self.getListUrl(list_items))
            self.index_input.setStyleSheet(self.text_style() + "padding : 10px 10px; border : 1px solid #ffffff;")
            self.url_input.setStyleSheet(self.text_style() + "padding : 10px 10px; border : 1px solid #ffffff;")
            search_btn.setText("Download")
            self.onSearch = False

        except:
            print("error")

    def download_click(self):
        print("download")
        self.downloadThread = downloadThread()
        self.downloadThread.download_proess_signal.connect(self.set_progressbar_value)
        self.downloadThread.start()
        # test2.startDownload()
        self.search_btn.setEnabled(False)

    def on_pushButton_clicked(self):
        if self.onSearch:
            self.search_click()
        else:
            self.download_click()

    # Setting progress bar
    def formatF(self, f):
        return "{:00.2f}".format(f)

    def set_progressbar_value(self, v):
        title = downloader.ControllerClass.title
        if not self.setTitle:
            self.time = current_milli_time()
            self.oldValue = 0.0
            self.titleInfo.setText(title)
            self.setTitle = True

        size = downloader.ControllerClass.filesize / (1024 * 1024)
        percentage = downloader.ControllerClass.progress
        value = (size * percentage) / 100.0
        timeDef = (current_milli_time() - self.time)
        if timeDef > 500:
            downloader.ControllerClass.speed = (value - self.oldValue) * 1024 * 1000 / (timeDef)
            self.oldValue = value
            self.time = current_milli_time()

        # print(percentage)
        valueText = self.formatF(value)
        sizeText = self.formatF(size)
        percentageText = self.formatF(percentage)
        speedText = self.formatF(downloader.ControllerClass.speed)
        self.progressBar.setFormat(f'{valueText}MB / {sizeText}MB ({percentageText}%)      {speedText}KB/s')
        self.progressBar.setValue(int(percentage) * 100)

        if percentage == 100:
            self.setTitle = False
            print(title + " --> Done")

        if percentage == 100 and downloader.ControllerClass.download_complete:
            QMessageBox.information(self, "Tips", "Download success!")
            self.search_btn.setEnabled(True)
            return


##################################################################
# Download thread
##################################################################
class downloadThread(QThread):
    download_proess_signal = pyqtSignal(int)  # Create signal

    def __init__(self):
        super(downloadThread, self).__init__()

    def printProgressBar(self, iteration, total):
        percent = 100 * (float(iteration) / float(total))
        downloader.ControllerClass.progress = percent
        self.download_proess_signal.emit(int(percent))

    def run(self):
        def progressFun(chunk: bytes, file_handler: bytes, bytes_remaining: int):
            filesize = downloader.ControllerClass.filesize
            downloaded = filesize - bytes_remaining
            self.printProgressBar(downloaded, filesize)

        downloader.ControllerClass.progressFun = progressFun
        downloader.startDownload()


####################################
# Program entry
####################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
    #url = "https://www.youtube.com/playlist?list=PLTChhmU8tbQxUHmGpllpbwZKkz5xNbagD"
    #list_items = downloader.getListUrlFromFile(url, True)
