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
            self.icon = None 
            self.add_date = None
            self.last_modified = None
            
        else:
            lineContent = rough.strip()
            self.type = get_type(lineContent)
            self.text = get_text(lineContent)
            '''
            if self.type == "bookMark":
                self.link = get_link(lineContent)
            else:
                self.link = None
            '''
            self.rough = rough
            self.lineNum = lineNum
            self.parent = None

            self.link = None
            self.icon = None 
            self.add_date = None
            self.last_modified = None
            self.personal_toolbar_folder = False
            self.init_tag_content(rough)

        self.childrenList = []

    def init_tag_content(self,rough):
        contentList = get_tag_content(rough)

        for tagName, content in contentList:
            if tagName == "ADD_DATE":
                self.add_date = content
            elif tagName == "LAST_MODIFIED":
                self.last_modified = content
            elif tagName == "ICON":
                self.icon = content
            elif tagName == "HREF":
                self.link = content
            elif tagName == "PERSONAL_TOOLBAR_FOLDER":
                self.personal_toolbar_folder = True
            else:
                print("%s : %s" %(tagName, content))


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
           # root.text = "rootFolder"
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
    print("space ??????",get_prefix_spaceNum(parentFolderElem.rough))
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
    
    # ?????????????????? ??????
    targetElem.parent.childrenList.remove(targetElem)
    destFolderElem.add_child(targetElem)

    # ?????? ??????
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
    
    # ?????? ??????
    destFolderPrefixSpaceNum = get_prefix_spaceNum(destFolderElem.rough)
    
    destline = find_last_children_lineNum(fc,destFolderElem.lineNum)
    temp = (" "*(destFolderPrefixSpaceNum + 4) )+ targetElem.rough.strip()

    fc.insert(destline + 1,temp)
    
    return fc

def move_Folder(fc,destFolderElem,targetElem):

    
    destRough = fc[destFolderElem.lineNum]
    
    #?????? ?????? ??? ????????? ??????.
    folderEndLine = get_folder_end(fc,targetElem.lineNum)
    
    #????????? ?????? ?????????.
    targetFCLines = fc[targetElem.lineNum:folderEndLine + 1]
    

    # ????????? ?????? ?????? ??????.
    
    fc_without_targetFolder = fc[0:targetElem.lineNum] + fc[folderEndLine + 1:]
    targetIndex = fc_without_targetFolder.index(destRough) + 2

    destFolderPrefixSpaceNum = get_prefix_spaceNum(destFolderElem.rough)
    currentPrifixSpace =  " " * (destFolderPrefixSpaceNum + 4)
    # ???????????? ??? ????????????. 
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
    
    #?????? ?????? ??? ????????? ??????.
    folderEndLine = get_folder_end(fc,targetElem.lineNum)
    
    #????????? ?????? ?????????.
    targetFCLines = fc[targetElem.lineNum:folderEndLine + 1]
    
    # ?????? ?????? ?????? ????????? ??????.
    targetIndex = destFolderElem.lineNum + 2

    destFolderPrefixSpaceNum = get_prefix_spaceNum(destFolderElem.rough)
    currentPrifixSpace =  " " * (destFolderPrefixSpaceNum + 4)
    # ???????????? ??? ????????????. 
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

def create_fc_from_tree(treeRoot):
    fc,nextLineNum = create_default_fc_frame()

    parent = treeRoot.parent
    current = treeRoot 

    # root process
    
    create_folderFC(fc,treeRoot,0,nextLineNum)
    create_fc_with_search_tree(fc,current,"",6)


    return fc

def create_fc_with_search_tree(fc,current,parent_space,parent_lineNum):

    current_space = parent_space + '    '
    lastIndex = get_folder_end(fc,parent_lineNum)
    if current.type == 'bookMark':
        create_bookMark(fc,current,parent_space,lastIndex)
        pass
    elif current.type == 'newfolderName' or current.type =="rootfolder":
        create_folderFC(fc,current,parent_space,lastIndex)

        for c in current.childrenList:
            create_fc_with_search_tree(fc,c,current_space,lastIndex)
        pass
    else:
        print("wrong")
    pass

def create_default_fc_frame():
    fc = []
    fc.append("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
    fc.append("<!-- This is an automatically generated file.\n")
    fc.append("     It will be read and overwritten.\n")
    fc.append("     DO NOT EDIT! -->\n")
    fc.append('''<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n''')
    fc.append("<TITLE>Bookmarks</TITLE>\n")

    return fc,6


def create_folderFC(fc, treeElem,parentSpace,targetLineNum):
    if treeElem.type == "rootfolder":
        fc.insert(targetLineNum,'''<H1>Bookmarks</H1>\n''')
        fc.insert(targetLineNum + 1,'<DL><p>\n')
        fc.insert(targetLineNum + 2,'</DL><p>\n')
        
    elif treeElem.type == 'newfolderName':
        space = parentSpace + '    '
        if treeElem.personal_toolbar_folder == True:
            fc.insert(targetLineNum,space + '''<DT><H3 ADD_DATE="%s" LAST_MODIFIED="%s" PERSONAL_TOOLBAR_FOLDER="true">%s</H3>\n''' % (treeElem.add_date,treeElem.last_modified,treeElem.text))
        else:
            fc.insert(targetLineNum,space + '''<DT><H3 ADD_DATE="%s" LAST_MODIFIED="%s">%s</H3>\n''' % (treeElem.add_date,treeElem.last_modified,treeElem.text))            
        fc.insert(targetLineNum + 1,space + '<DL><p>\n')
        fc.insert(targetLineNum + 2,space + '</DL><p>\n')
    else:
        print("Not folder elem")

    return fc
    pass

def create_bookMark(fc,treeElem,parentSpace,targetLineNum):
    space = parentSpace + "    "
    fc.insert(targetLineNum,space + '''<DT><A HREF="%s" ADD_DATE="%s" ICON="%s">%s</A>\n''' %(treeElem.link,treeElem.add_date,treeElem.icon,treeElem.text))

    return fc


if __name__ == "__main__":

    fc = get_fileContents("bookmarks_22. 10. 3..html")

    root = parse_html_to_treeView(fc)

    fcT = create_fc_from_tree(root)
    

    save_new_bookMark_file(fcT, "result.html")

    quit(0)
    # ????????????
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
    