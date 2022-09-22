from html_parser import *
from subLibrary import *

fc = None

def execute(elem):
    global fc
    if elem.type == "rootfolder":
        for child in elem.childrenList:
            execute(child)
    elif elem.type == "newfolderName" :
        for child in elem.childrenList:
            execute(child)
    elif elem.type == "bookMark":
        lineContent = elem.rough.strip()
        link = get_link(lineContent)
        if "manatoki" in link:
            pureAddress = link.split("?")[0]
            tagNum = pureAddress.split('/')[-1]
            #print(tagNum)
            result = "https://manatoki%d.net/comic/%s" %(154,tagNum)
            
            fc[elem.get_lineNum()] = set_link(elem.rough,result)
            if fc[elem.get_lineNum()] == None:
                print(elem.get_lineNum())
            #print("elem.get_lineNum()\n",elem.get_lineNum())
            #print()
            #print("elem.rough\n",elem.rough)
            
            #print(result)

    else:
        print("Fail execute")

def test(elem):
    global fc
    if elem.type == "rootfolder":
        for child in elem.childrenList:
            execute(child)
    elif elem.type == "newfolderName" :
        for child in elem.childrenList:
            execute(child)
    elif elem.type == "bookMark":
        link = get_link(elem.rough)
        
        if "manatoki" in link:
            print(link)

    else:
        print("Fail execute")

file = open("bookmarks_22. 9. 22..html", "r", encoding="UTF-8")

fileContents = file.readlines()
fc = fileContents

root = parse_html_to_treeView(fc)

execute(root)
root = parse_html_to_treeView(fc)

file = open("result1.html","w", encoding="UTF-8")

result = "".join(fc)
file.write(result)