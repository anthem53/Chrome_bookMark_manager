# GUI bookmark management tool

import os
import sys
import math, re, shutil

from html_parser import *
from subLibrary import *


import PyQt5
from PyQt5 import (uic , QtCore)
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *

form_class = uic.loadUiType("bookMark.ui")[0]
fc = None
root = None

class mainWindowClass (QMainWindow,form_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.initUi()
        self.fc = None
        self.root = None
        self.current = None

    def initUi(self):
        self.actionOpen.triggered.connect(lambda : self.open_bookMarkFile())
        self.actionSave.triggered.connect(lambda : print("Save"))
        self.actionSetting.triggered.connect(lambda : print("Setting"))
        self.actionQuit.triggered.connect(lambda : print("Quit"))

        self.fileListWidget.setStyleSheet("alternate-background-color: rgb(230,230,230);background-color: white;")
        self.fileListWidget.doubleClicked.connect(self.itemDoubleClicked)
        pass
        #self.okButton.clicked.connect(self.onOKButtonClicked)
        #self.cancelButton.clicked.connect(self.onCancelButtonClicked)

    def open_bookMarkFile(self):
        fnameDataset = QFileDialog.getOpenFileName(self, 'Open file', './')
        fname = fnameDataset[0]
        print(fname)
        self.fc = get_fileContents(fname)
        self.root = parse_html_to_treeView(self.fc)
        self.current = self.root

        print(self.root.childrenList[0].text)
        self.show_folder(self.root)

    def show_folder(self,treeElem):
        self.folderNameLineEdit.setText(treeElem.text)
        self.fileListWidget.addItem(".")
        for c in treeElem.childrenList:
            if c.type == "bookMark":
                prefix = "[B] "
            elif c.type == "newfolderName":
                prefix = "[F] "
            self.fileListWidget.addItem(prefix + c.text)
        pass

    def itemDoubleClicked(self):
        targetRow = self.fileListWidget.currentIndex().row()
        targetText = self.fileListWidget.item(targetRow).text()
        print(targetText)

        if targetText == "." and self.current.type != "rootfolder":
            self.fileListWidget.clear()
            self.current = self.current.parent
            self.show_folder(self.current)
        else :
            for c in self.current.childrenList:
                if c.text == targetText[4:]:
                    if c.type == "newfolderName":
                        self.fileListWidget.clear()
                        self.current = c 
                        self.show_folder(c)
                        break
                    else:
                        # bookMark:
                        print("bookMark double clicked")
                        print(c.text)
                        print(self.fc[c.lineNum])                        
                    #print("find")
                else:
                    pass
                #print("Defeat")


    #def onOKButtonClicked(self):
    #    self.accept()
    #def onCancelButtonClicked(self):
    #    self.reject()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = mainWindowClass()
    myWindow.show()
    app.exec_()
    