from html_parser import *
from subLibrary import *

fc = None
currentRabbitVersion = 154


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
            result = "https://manatoki%d.net/comic/%s" %(currentRabbitVersion,tagNum)
            
            fc[elem.get_lineNum()] = set_link(elem.rough,result)
            if fc[elem.get_lineNum()] == None:
                print(elem.get_lineNum())
            #print("elem.get_lineNum()\n",elem.get_lineNum())
            #print()
            #print("elem.rough\n",elem.rough)
            
            #print(result)

    else:
        print("Fail execute")







def get_pure_text(elem):

    def remove_rhyme(a):
        l = len(a)
        result = a[0:l-17]
        return result

    def remove_episodeNum(a):
        aList = a.split(" ")
        result = " ".join(aList[0:-1])
        return result

    result = elem
    #result = elem.text
    result = remove_rhyme(result)
    
    if result[-1] =="화":
        result = remove_episodeNum(result)

    return result


def removeOld(root):
    global  fc

    def findRecentFolder(elem):

        result = []
        for child in elem.childrenList:
            if child.type == "newfolderName":
                #print("debug",child.text)
                if child.text == "최신화까지 다본거":
                    result.append(child)
                    result += findRecentFolder(child)
                elif child.text == "볼거":
                    result.append(child)
                    result += findRecentFolder(child)
                else:
                    result += findRecentFolder(child)
            elif child.type == "bookMark":
                pass
            else:
                pass

        return result
    



    currentFolder, recentFolder = findRecentFolder(root)

    for r in recentFolder.childrenList:
        if r.type == "bookMark":
            rPureText = get_pure_text(r.text)
            
            for c in currentFolder.childrenList:
                if c.type == "bookMark":
                    cPureText = get_pure_text(c.text)        
                    
                    if rPureText == cPureText :  # find the same link in different foloders
                        currentFolder.childrenList(c)
                else:
                    pass
            
        else:
            pass
            


    #print(currentFolder.text)
    #print(recentFolder.text)






file = open("bookmarks_22. 10. 3..html", "r", encoding="UTF-8")

fileContents = file.readlines()
fc = fileContents

root = parse_html_to_treeView(fc)

execute(root)
root = parse_html_to_treeView(fc)

file = open("result1.html","w", encoding="UTF-8")

result = "".join(fc)
file.write(result)

removeOld(root)