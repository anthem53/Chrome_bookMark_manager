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
        self.copy_elem_list = []
        self.cut_elem_list = []

        self.init_onefile('''C:\\Users\\LeeJihyeon\\Documents\\GitHub\\BookMark-Manager\\bookmarks_22. 10. 9..html''')

    def initUi(self):
        self.actionOpen.triggered.connect(lambda : self.open_bookMarkFile())
        #self.actionSave.triggered.connect(lambda : self.saveBookMark())
        self.actionSave.triggered.connect(lambda : self.saveBookMark2())
        self.actionSetting.triggered.connect(lambda : print("Setting"))
        self.actionQuit.triggered.connect(lambda : print("Quit"))

        self.actiontest.triggered.connect(lambda : self.test())

        
        self.fileListWidget.installEventFilter(self)
        self.fileListWidget.setStyleSheet("alternate-background-color: rgb(230,230,230);background-color: white;")
        self.fileListWidget.doubleClicked.connect(self.itemDoubleClicked)

        self.fileListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
    
    def test(self):
        for e in self.fileListWidget.selectedItems():
            print(e.text())


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

    def saveBookMark2(self):
        saveDialog = QFileDialog()
        saveDialog.setFilter(saveDialog.filter() | QtCore.QDir.Hidden)
        saveDialog.setDefaultSuffix('html')
        saveDialog.setAcceptMode(QFileDialog.AcceptSave)
        saveDialog.setNameFilters(['HTML (*.html)'])

        if saveDialog.exec_() == QDialog.Accepted:
            fileName  = saveDialog.selectedFiles()[0]
            print(fileName)
            currentFC = create_fc_from_tree(self.root)
            save_new_bookMark_file(currentFC,fileName)
        else:
            print('Cancelled')


        #text =   QFileDialog.getSaveFileName(self, 'Save file', '.html')

        #
    # https://gist.github.com/stevenliebregt/8e4211937b671ac637b610650a11914f
    # https://learndataanalysis.org/source-code-how-to-implement-context-menu-to-a-qlistwidget-pyqt5-tutorial/
    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.fileListWidget:
            menu = QMenu()
            menu.addAction('??????',lambda: self.modify_folder(source.itemAt(event.pos())))
            menu.addAction('????????????',lambda: self.cut_items())
            #menu.addAction('????????????',lambda: self.cut_item(source.itemAt(event.pos())))
            menu.addAction('??????',lambda: self.copy_items())
            #menu.addAction('??????',lambda: self.copy_item(source.itemAt(event.pos())))
            menu.addAction('????????????',lambda: self.paste_elems())            
            #menu.addAction('????????????',lambda: self.paste_elem(source.itemAt(event.pos())))            
            menu.addAction('??????',lambda: self.delete_item(source.itemAt(event.pos())))
            
            if menu.exec_(event.globalPos()):
                pass
            else:
                print("Fail to open menu")
            return True

        return super().eventFilter(source, event)

    def modify_folder(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_item_text(item.text())

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
        elem = self.find_elem_with_item_text(item.text())
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

    def cut_items(self):

            selectedItemList = self.fileListWidget.selectedItems()
            if len(selectedItemList) == 0:
                return None

            self.cut_elem_list = []
            for item in selectedItemList:
 
                elem = self.find_elem_with_item_text(item.text())
                self.cut_elem_list.append(elem) 
                
            
            self.is_cut = True
            self.is_copy = False


    def cut_item(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_item_text(item.text())
        self.cut_elem = elem
        self.is_cut = True
        self.is_copy = False
        pass

    def copy_items(self):
        selectedItemList = self.fileListWidget.selectedItems()
        if len(selectedItemList) == 0:
            return None

        self.copy_elem_list = []
        for item in selectedItemList:

            elem = self.find_elem_with_item_text(item.text())
            self.copy_elem_list.append(elem) 
            
        
        self.is_copy = True
        self.is_cut = False

        pass

    def copy_item(self,item):
        if item == None:
            return 
        elem = self.find_elem_with_item_text(item.text())
        self.copy_elem = elem
        self.is_cut = False
        self.is_copy = True
        pass

    def paste_elems(self):
        if self.is_copy == False and self.is_cut == False:
            return

        destinationFolderElem = self.current

        elem_list = None
        if self.is_cut == True and self.is_copy == False: 
            elem_list = self.cut_elem_list
        elif self.is_copy == True and self.is_cut == False : 
            elem_list = self.copy_elem_list
        else:
            quit(" paste_elems(self) : Wrong programming")

        
        if self.is_copy == True :
            for e in elem_list:
                #e.parent.childrenList.remove(e)
                e.parent = destinationFolderElem
                
                if e.type == "bookMark":
                    e.parent.childrenList.append(e)
                elif e.type =="newfolderName":
                    e.parent.childrenList.insert(0,e)
                else:
                    print("paste_elems() : something wrong")
            self.refresh()
        elif self.is_cut == True:
            for e in elem_list:
                e.parent.childrenList.remove(e)
                e.parent = destinationFolderElem
                
                if e.type == "bookMark":
                    e.parent.childrenList.append(e)
                elif e.type =="newfolderName":
                    e.parent.childrenList.insert(0,e)
                else:
                    print("paste_elems() : something wrong")
            self.cut_elem_list = []
            self.is_cut = False
            self.refresh()
        else:
            pass


    def paste_elem(self,destinationFolderItem):
        
        if self.is_copy == False and self.is_cut == False:
            return

        destinationFolderElem = self.current

        elem = None
        if self.is_cut == True and self.is_copy == False: 
            elem = self.cut_elem
        elif self.is_copy == True and self.is_cut == False : 
            elem = self.copy_elem
        else:
            quit("Wrong programming")

        # cut
        if self.is_cut == True and self.is_copy == False : 
            if elem.type == "bookMark":
                old_parent = elem   .parent
                destinationFolderElem.childrenList.append(elem)
                old_parent.childrenList.remove(elem)
                elem.parent = destinationFolderElem

                self.fc = move_bookMark(self.fc, destinationFolderElem,elem)
                self.root = parse_html_to_treeView(self.fc)
                
                pass
            elif elem.type == "newfolderName":
                self.fc = move_Folder(self.fc, destinationFolderElem,elem)
                self.root = parse_html_to_treeView(self.fc)
                pass
            else:
                quit("paste_elem, warning")
            self.is_cut = False 
            self.cut_elem = None
            self.current = set_address(self.root, get_address(self.current) + [self.current])
            self.refresh()
        # copy
        elif self.is_cut == False and self.is_copy == True : 
            copy_elem_text = elem.text
            if elem.type == "bookMark":
                self.fc = copy_bookMark(self.fc, destinationFolderElem,elem)
                self.root = parse_html_to_treeView(self.fc)
                pass
            elif elem.type == "newfolderName":
                self.fc = copy_Folder(self.fc, destinationFolderElem,elem)
                self.root = parse_html_to_treeView(self.fc)
                pass
            else:
                quit("paste_elem, warning")
            self.current = set_address(self.root, get_address(self.current) + [self.current])
            self.copy_elem = self.find_elem_with_text(copy_elem_text)
            self.refresh()
        else :
            print("self.is_cut",self.is_cut)
            print("self.is_copy",self.is_copy)
        


    def find_elem_with_text(self,text):
        
        for c in self.current.childrenList:
            if c.text == text:
                return c
            else:
                pass
        return None     


    def find_elem_with_item_text(self,name):
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
    