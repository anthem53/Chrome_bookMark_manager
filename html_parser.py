import re
from subLibrary import *

class tree:
    def __init__(self, rough = None, lineNum = None):
        if rough == None : 
            self.type = None
            self.text = None
            self.link = None
            self.llineNum = None
            self.rough = None
            self.parent = None
        else:
            lineContent = rough.strip()
            self.type = get_type(lineContent)
            self.text = get_text(lineContent)
            if self.type == "bookMark":
                self.link = get_link(lineContent)
            else:
                self.link = None
            self.rough = rough
            self.lineNum = lineNum
            self.parent = None

        self.childrenList = []

    def add_child(self, child):
        child.set_parent(self)
        self.childrenList.append(child)

    def get_lineNum(self):
        return self.lineNum
    def get_type(self):
        return self.type
    def get_text(self):
        return self.text
    def get_link(self):
        if self.type == "bookMark":
            return self.link
        else : 
            return None
    def get_parent(self):
        return self.parent
    
    def set_parent(self,parent):
        self.parent = parent

    def show_info(self):
        print("#"*20)
        print("type:" , self.type)
        print("text:" , self.text) 
        print("link:" , self.link)
        print("lineNum:" , self.lineNum)
        print("#"*20+"\n")

def parse_html_to_treeView(fc : list) -> tree:
    
    root = None
    current = None
    parent = None

    for i, rough in enumerate(fc):

        lineContent = rough.strip()
        lineType = get_type(lineContent)

        if lineType == "rootfolder": 
            root = tree(rough,i)  
            current = root
            parent = None

            pass
        elif lineType == "newfolder": 
            #temp = tree(rough,i)
            parent = current
            
            #print("root folder")
            #print("newfolder")
            ## newfolder
        elif lineType == "newfolderName":
            temp = tree(rough,i)
            parent.add_child(temp)
            current = temp
            
            #print("newfolderName")
        elif lineType == "bookMark":
            temp = tree(rough,i)
            parent.add_child(temp)
            print(temp.link)
            #print("bookMark")
        elif lineType == "end":
            current = parent
            parent = current.get_parent()
            #print("end")

    return root

def update_link(fileContentsList, bookMark, newLink):
    lineNum = bookMark.get_lineNum()
    result = set_link(bookMark.rough,newLink)

    fileContentsList[lineNum] = result
    return fileContentsList
    pass


if __name__ == "__main__":

    file = open("bookmarks_22. 9. 21..html", "r", encoding="UTF-8")

    fileContents = file.readlines()
    fc = fileContents

    root = parse_html_to_treeView(fc)
    
    