# GUI bookmark magagement tool

from html_parser import *
from subLibrary import *


import PyQt5
from PyQt5 import (uic , QtCore)
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *

form_class = uic.loadUiType("bookMark.ui")[0]

class bookMarkManager (QDialog,form_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.initUi()

        if target == []:
            print("default setting")
        else :
            print("existed setting")
    def initUi(self):
        pass
        #self.okButton.clicked.connect(self.onOKButtonClicked)
        #self.cancelButton.clicked.connect(self.onCancelButtonClicked)
    #def onOKButtonClicked(self):
    #    self.accept()
    #def onCancelButtonClicked(self):
    #    self.reject()


if __name__ == "__main__":
    print("main")