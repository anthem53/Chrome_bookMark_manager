# GUI bookmark management tool

import os
import sys
import math, re, shutil
import webbrowser

from html_parser import *
from subLibrary import *


import PyQt5
from PyQt5 import (uic , QtCore)
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *

form_class = uic.loadUiType("bookMark.ui")[0]
folder_rename_class = uic.loadUiType("folderChange.ui")[0]
fc = None
root = None

class folderRenameClass (QDialog,folder_rename_class):
    def __init__(self,old_name=""):
        super().__init__()

        self.setupUi(self)
        self.initUi()
        self.old_name = old_name
        if old_name == "":
            print("default setting")
        else :
            print("existed setting")
            
    def initUi(self):
        #self.okButton.clicked.connect(self.onOKButtonClicked)
        #self.cancelButton.clicked.connect(self.onCancelButtonClicked)
        self.setFixedSize(386,165)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def execute_rename(self):
        isOkclicked = super().exec_()
        newFileName = self.lineEdit.text()
        return isOkclicked,newFileName
class mainWindowClass (QMainWindow,form_class):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.initUi()
        self.fc = None
        self.root = None
        self.current = None

        self.init_onefile('''C:\\Users\\LeeJihyeon\\Documents\\GitHub\\BookMark-Manager\\bookmarks_22. 10. 9..html''')

    def initUi(self):
        self.actionOpen.triggered.connect(lambda : self.open_bookMarkFile())
        self.actionSave.triggered.connect(lambda : self.saveBookMark())
        self.actionSetting.triggered.connect(lambda : print("Setting"))
        self.actionQuit.triggered.connect(lambda : print("Quit"))

        
        self.fileListWidget.installEventFilter(self)
        self.fileListWidget.setStyleSheet("alternate-background-color: rgb(230,230,230);background-color: white;")
        self.fileListWidget.doubleClicked.connect(self.itemDoubleClicked)
        pass
        #self.okButton.clicked.connect(self.onOKButtonClicked)
        #self.cancelButton.clicked.connect(self.onCancelButtonClicked)
        
        

    def open_bookMarkFile(self):
        self.fileListWidget.clear()
        fnameDataset = QFileDialog.getOpenFileName(self, 'Open file', './')
        fname = fnameDataset[0]
        print(fname)
        self.fc = get_fileContents(fname)
        self.root = parse_html_to_treeView(self.fc)
        self.current = self.root

        print(self.root.childrenList[0].text)
        self.show_folder(self.root)

    # Debugging
    def init_onefile(self,fname):
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
    def refresh(self):
        self.fileListWidget.clear()
        self.show_folder(self.current)

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
                if c.text == ' '.join(targetText.split(' ')[1:]):
                    if c.type == "newfolderName":
                        self.fileListWidget.clear()
                        self.current = c 
                        self.show_folder(c)
                        break
                    else:
                        # bookMark:
                        print("bookMark double clicked")
                        webbrowser.open(c.link)
                    #print("find")
                else:
                    pass
                #print("Defeat")


    def saveBookMark(self):
        saveDialog = QFileDialog()
        saveDialog.setFilter(saveDialog.filter() | QtCore.QDir.Hidden)
        saveDialog.setDefaultSuffix('html')
        saveDialog.setAcceptMode(QFileDialog.AcceptSave)
        saveDialog.setNameFilters(['HTML (*.html)'])

        if saveDialog.exec_() == QDialog.Accepted:
            fileName  = saveDialog.selectedFiles()[0]
            print(fileName)
            save_new_bookMark_file(self.fc,fileName)
        else:
            print('Cancelled')

        #text =   QFileDialog.getSaveFileName(self, 'Save file', '.html')

        #
    # https://gist.github.com/stevenliebregt/8e4211937b671ac637b610650a11914f
    # https://learndataanalysis.org/source-code-how-to-implement-context-menu-to-a-qlistwidget-pyqt5-tutorial/
    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.fileListWidget:
            menu = QMenu()
            menu.addAction('편집',lambda: self.modify_folder(source.itemAt(event.pos())))
            menu.addAction('이동',lambda: print("이동"))
            menu.addAction('삭제',lambda: self.delete_item(source.itemAt(event.pos())))
            
            if menu.exec_(event.globalPos()):
                pass
            else:
                print("Fail to open menu")
            return True

            return True
        return super().eventFilter(source, event)

    def modify_folder(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_name(item.text())

        renameWin = folderRenameClass()
        isOK, newName = renameWin.execute_rename()

        if isOK == 1 :
            elem.set_rough(set_text(elem.rough,newName))
            self.fc[elem.lineNum] = elem.rough
            self.refresh()
        elif isOK == 0:
            pass
        else:
            print("modify_folder error")
            pass
    
    def delete_item(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_name(item.text())
        self.delete_elem(elem)

    def delete_elem(self,elem):
        
        def get_address(elem):
        # rootFolder
            
            if elem.parent.type == "rootfolder" :
                return []
            else:
                if elem.parent != None : 
                    result = [elem.parent]
                else:
                    result = []
                return get_address(elem.parent) + result
            pass
        
        def set_address(root,elem_address):
            temp = root 
            next = None
            for folderelem in elem_address:
                folderName = folderelem.text
                for c in temp.childrenList:
                    if c.text == folderName:
                        next = c
                        break
                temp = next
            return temp
        elem_address = get_address(elem)


        for t in elem_address:
            if t != None :
                print(t.text)
        elemParent = elem.parent
        if elem.type == "bookMark":
            self.fc = remove_bookMark(self.fc,self.current,elem)
            self.root = parse_html_to_treeView(self.fc)
        elif elem.type == "newfolderName":
            self.fc = remove_folder(self.fc,elem)
            self.root = parse_html_to_treeView(self.fc)
        else:
            print("wrong")
            pass
        #self.root = 
        self.current = set_address(self.root, elem_address)
        self.refresh()

    def find_elem_with_name(self,name):
        name = ' '.join(name.split(' ')[1:])
        for c in self.current.childrenList:
            if c.text == name:
                return c
            else:
                pass
        return None
    #def onOKButtonClicked(self):
    #    self.accept()
    #def onCancelButtonClicked(self):
    #    self.reject()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = mainWindowClass()
    myWindow.show()
    app.exec_()
    