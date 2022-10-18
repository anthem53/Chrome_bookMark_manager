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
bookmark_rename_class = uic.loadUiType("bookMarkChange.ui")[0]
fc = None
root = None

class bookMarkRenameClass (QDialog,bookmark_rename_class):
    def __init__(self,old_name="",old_link=""):
        super().__init__()

        self.setupUi(self)
        self.initUi()
        self.nameEdit.setText(old_name)
        self.linkEdit.setText(old_link)
        self.old_name = old_name
        self.old_link = old_link
            
    def initUi(self):
        self.setFixedSize(386,165)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def execute_rename(self):
        isOkclicked = super().exec_()
        newFileName = self.nameEdit.text()
        newFileLink = self.linkEdit.text()
        return isOkclicked,newFileName,newFileLink


class folderRenameClass (QDialog,folder_rename_class):
    def __init__(self,old_name=""):
        super().__init__()

        self.setupUi(self)
        self.initUi()
        self.lineEdit.setText(old_name)

            
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
        self.cut_elem = None
        self.copy_elem = None
        self.is_cut = None
        self.is_copy = None

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
            menu.addAction('잘라내기',lambda: self.cut_item(source.itemAt(event.pos())))
            menu.addAction('복사',lambda: self.copy_item(source.itemAt(event.pos())))
            menu.addAction('붙여넣기',lambda: self.paste_elem(source.itemAt(event.pos())))            
            menu.addAction('삭제',lambda: self.delete_item(source.itemAt(event.pos())))
            
            if menu.exec_(event.globalPos()):
                pass
            else:
                print("Fail to open menu")
            return True

        return super().eventFilter(source, event)

    def modify_folder(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_name(item.text())

        if elem.type == "newfolderName":
            renameWin = folderRenameClass(elem.text)
            isOK, newName = renameWin.execute_rename()

            if isOK == 1 :
                elem.set_rough(set_text(elem.rough,newName))
                self.fc[elem.lineNum] = elem.rough
                self.refresh()
            else:
                pass
        elif elem.type == "bookMark":
            renameWin = bookMarkRenameClass(elem.text,elem.link)
            isOK, newName, newLink = renameWin.execute_rename()
            if isOK == 1 :
                elem.set_rough(set_text(elem.rough,newName))
                elem.set_rough(set_link(elem.rough,newLink))
                self.fc[elem.lineNum] = elem.rough
                self.refresh()
            else:
                pass
        else :
            pass

    
    def delete_item(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_name(item.text())
        self.delete_elem(elem)

    def delete_elem(self,elem):
        
        
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

    def cut_item(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_name(item.text())
        self.cut_elem = elem
        self.cut_elem_address = get_address(self.cut_elem)
        self.is_cut = True
        self.is_copy = False
        print(self.cut_elem_address)
        pass

    def copy_item(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_name(item.text())
        self.copy_elem = elem
        self.copy_elem_address = get_address(self.cut_elem)
        self.is_cut = False
        self.is_copy = True
        pass

    def paste_elem(self,destinationFolderItem):
        
        if destinationFolderItem == None:
            destinationFolderElem = self.current
        elif self.find_elem_with_name(destinationFolderItem.text()).type == "bookMark":
            destinationFolderElem = self.current
        else:
            destinationFolderElem = self.find_elem_with_name(destinationFolderItem.text())

        elem = None
        if self.is_cut == True and self.is_copy == False: 
            elem = self.cut_elem
        elif self.is_copy == True and self.is_cut == True : 
            elem = self.copy_elem
        else:
            print("Wrong programming")
            quit(1)


        # Tree structure Part
        if elem.type == "bookMark":
            old_parent = elem.parent
            destinationFolderElem.childrenList.append(elem)
            old_parent.childrenList.remove(elem)
            elem.parent = destinationFolderElem

            move_bookMark(self.fc, destinationFolderElem,elem)
            pass
        elif elem.type == "newfolderName":
            old_parent = elem.parent
            destinationFolderElem.childrenList.append(elem)
            old_parent.childrenList.remove(elem)
            elem.parent = destinationFolderElem

            pass
        else:
            
            quit("paste_elem, warning")

        self.refresh()

        # FC part, 
        pass

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
    