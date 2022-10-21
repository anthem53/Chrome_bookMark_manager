from distutils.command.build_scripts import first_line_re
import re
import io
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
        if self.text != None:
            result = self.text
        else:
            result = ""
        return result
    def get_link(self):
        if self.type == "bookMark":
            return self.link
        else : 
            return None
    def get_parent(self):
        return self.parent
    
    def set_parent(self,parent):
        self.parent = parent
    def remove_child(self,child):
        if child in self.childrenList:
            self.childrenList.remove(child)
        else:
            print("Child",child," is not in children List")
    def set_rough(self,newRough):
        lineContent = newRough.strip()
        #self.type = get_type(lineContent)
        self.text = get_text(lineContent)
        if self.type == "bookMark":
            self.link = get_link(lineContent)
        else:
            self.link = None
        self.rough = newRough
        #self.lineNum = lineNum
        #self.parent = None
        pass
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
            root.text = "rootFolder"
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
            #print(temp.link)
            #print("bookMark")
        elif lineType == "end":
            
            if parent != None : 
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

def remove_bookMark(fileContentsList, folderName, targetBookmark):
    bookMarkNum = targetBookmark.lineNum
    folderName.remove_child(targetBookmark)
    del fileContentsList[bookMarkNum]

    return fileContentsList

def remove_folder(fc, treeFolderElem):

    startIndex = treeFolderElem.lineNum
    i =  startIndex + 1
    temp = 0
    while True  :
        targetRough = fc[i]
        if get_type(targetRough) == 'newfolder':
            temp += 1
        elif get_type(targetRough) == 'end':
            temp -= 1
        else :
            pass

        if temp <= 0 :
            break

        i += 1
    endIndex = i

    print(startIndex, endIndex)

    del fc[startIndex:endIndex+1]
    return fc

def new_bookMark(fc,parentFolderElem, newName,newLink):
    lcln = find_last_children_lineNum(fc,parentFolderElem.lineNum) + 1

    print(parentFolderElem.rough)
    print("space 개수",get_prefix_spaceNum(parentFolderElem.rough))
    space = ' ' * (get_prefix_spaceNum(parentFolderElem.rough)+4)
    
    newRough = space  +'''<DT><A HREF="%s" ADD_DATE="1657188244">%s</A>\n''' % (newLink,newName) 
    fc.insert(lcln,newRough)
    temp = tree(newRough,lcln)
    parentFolderElem.add_child(temp)
    
    print(parentFolderElem.rough)    
    print(temp.rough)

    return fc
def new_folder(fc,parentFolderElem, newName):
    lcln = find_last_children_lineNum(fc,parentFolderElem.lineNum) + 1
    space = ' ' * (get_prefix_spaceNum(parentFolderElem.rough)+4)

    newRough = space + '''<DT><H3 ADD_DATE="1662264166" LAST_MODIFIED="1662293959">%s</H3>\n''' %(newName)
    newfolder = space + "<DL><p>\n"
    end = space + "</DL><p>\n"
    
    fc.insert(lcln,newRough)
    fc.insert(lcln+1,newfolder)
    fc.insert(lcln+2,end)
    temp = tree(newRough)
    parentFolderElem.add_child(temp)

    return fc

    pass

def move_bookMark(fc,destFolderElem, targetElem):
    
    # 부모자식관계 처리
    targetElem.parent.childrenList.remove(targetElem)
    destFolderElem.add_child(targetElem)

    # 부모 공백
    destFolderPrefixSpaceNum = get_prefix_spaceNum(destFolderElem.rough)
    

    old_elem_index = targetElem.lineNum
    startIndex = destFolderElem.lineNum
    count = 0
    i = startIndex + 1
    while True :
        if get_type(fc[i]) == "newfolder":
            count += 1
        elif get_type(fc[i]) == "end":
            count  -= 1
        else :
            # Another bookMark or folder
            pass

        if count == 0 :
            break

        i += 1
    temp = (" "*(destFolderPrefixSpaceNum + 4) )+ targetElem.rough.strip()

    is_larger_than_dest = 1 if i < old_elem_index else 0
    fc.insert(i,temp)
    del fc[old_elem_index + is_larger_than_dest]
    
    return fc


def copy_bookMark(fc,destFolderElem, targetElem):
    
    # 부모 공백
    destFolderPrefixSpaceNum = get_prefix_spaceNum(destFolderElem.rough)
    
    destline = find_last_children_lineNum(fc,destFolderElem.lineNum)
    temp = (" "*(destFolderPrefixSpaceNum + 4) )+ targetElem.rough.strip()

    fc.insert(destline + 1,temp)
    
    return fc

def move_Folder(fc,destFolderElem,targetElem):

    
    destRough = fc[destFolderElem.lineNum]
    
    #타겟 폴더 끝 인덱스 구함.
    folderEndLine = get_folder_end(fc,targetElem.lineNum)
    
    #원하는 부분 도려냄.
    targetFCLines = fc[targetElem.lineNum:folderEndLine + 1]
    

    # 도려낸 부분 빼고 합침.
    
    fc_without_targetFolder = fc[0:targetElem.lineNum] + fc[folderEndLine + 1:]
    targetIndex = fc_without_targetFolder.index(destRough) + 2

    destFolderPrefixSpaceNum = get_prefix_spaceNum(destFolderElem.rough)
    currentPrifixSpace =  " " * (destFolderPrefixSpaceNum + 4)
    # 공백처리 및 붙혀넣기. 
    for s in targetFCLines:
        ss = s.strip()

        if get_type(ss) == 'end':
            currentPrifixSpace = currentPrifixSpace [0:-4]

        ss = currentPrifixSpace + ss + "\n"


        fc_without_targetFolder.insert(targetIndex,ss)
        if get_type(ss) == "newfolder":
            currentPrifixSpace += '    '
        
        targetIndex += 1

    return fc_without_targetFolder

def copy_Folder(fc,destFolderElem,targetElem):

    
    destRough = fc[destFolderElem.lineNum]
    
    #타겟 폴더 끝 인덱스 구함.
    folderEndLine = get_folder_end(fc,targetElem.lineNum)
    
    #원하는 부분 도려냄.
    targetFCLines = fc[targetElem.lineNum:folderEndLine + 1]
    
    # 집어 넣을 부분 인덱스 구함.
    targetIndex = destFolderElem.lineNum + 2

    destFolderPrefixSpaceNum = get_prefix_spaceNum(destFolderElem.rough)
    currentPrifixSpace =  " " * (destFolderPrefixSpaceNum + 4)
    # 공백처리 및 붙혀넣기. 
    for s in targetFCLines:
        ss = s.strip()

        if get_type(ss) == 'end':
            currentPrifixSpace = currentPrifixSpace [0:-4]

        ss = currentPrifixSpace + ss + "\n"

        fc.insert(targetIndex,ss)
        if get_type(ss) == "newfolder":
            currentPrifixSpace += '    '
        
        targetIndex += 1

    return fc


def get_address(elem):
        # rootFolder
            if elem.type == "rootfolder":
                return []
            elif elem.parent.type == "rootfolder" :
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

    if elem_address[0].type == 'rootfolder':
        return root
    for folderelem in elem_address:
        folderName = folderelem.text
        for c in temp.childrenList:
            if c.text == folderName:
                next = c
                break
        temp = next
    return temp


def cutting_treeElem(treeElem):
    result = get_address(treeElem) + [treeElem]
    return result



def get_fileContents(address):
    
    file = open(address, "r", encoding="UTF-8")
    fileContents = file.readlines()
    return fileContents

def save_new_bookMark_file(fc, outputName):
    file = open(outputName,"w", encoding="UTF-8")
    result = "".join(fc)
    file.write(result)
    
if __name__ == "__main__":

    fc = get_fileContents("bookmarks_22. 10. 3..html")

    root = parse_html_to_treeView(fc)

    # 북마크바
    folder = root.childrenList[0]
    sFolder =root.childrenList[0].childrenList[8] 
    target = root.childrenList[0].childrenList[9].childrenList[0]
    targetFolder = root.childrenList[0].childrenList[8] 

    postech = root.childrenList[0].childrenList[2]
    school = root.childrenList[0].childrenList[3]
    
    fc = move_Folder(fc,school,postech)
    

    save_new_bookMark_file(fc, "result.html")

    quit()
    for x in result:
        print(x.text)
    

    targetNum = target.lineNum
    #print(fc[targetNum] )
    #print(target.text)
    fc = remove_folder(fc,target)
    root = parse_html_to_treeView(fc)
    
    #print(fc[targetNum] ,targetNum)

    save_new_bookMark_file(fc, "result.html")
    