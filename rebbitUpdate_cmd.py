from ssl import _create_unverified_context
from html_parser import *
from subLibrary import *
import argparse

fc = None
currentRabbitVersion = 157

# 인자값을 받을 수 있는 인스턴스 생성
parser = argparse.ArgumentParser(description='북마크를 자동 수정 및 중복된 내용 제거 하는 프로그램')

# 입력받을 인자값 등록
parser.add_argument('--version', required=True, help='What version is target site?')
parser.add_argument('--file',required=True, help="Address of bookmark html file")
parser.add_argument('--output',required=False,default="result.html",help="The folder that processd file will be saved")
args = parser.parse_args()



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
            result = "https://manatoki%d.net/comic/%s" %(currentRabbitVersion,tagNum)
            
            fc[elem.get_lineNum()] = set_link(elem.rough,result)
            if fc[elem.get_lineNum()] == None:
                print(elem.get_lineNum())

    else:
        print("Fail execute")

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
    repetitionList = []
    for r in recentFolder.childrenList:
        if r.type == "bookMark":
            #rPureText = get_pure_text(r.text)
            
            for c in currentFolder.childrenList:
                if c.type == "bookMark":
                    #cPureText = get_pure_text(c.text)        
                    
                    #if rPureText == cPureText :  # find the same link in different foloders
                    if r.text[0:15] == c.text[0:15]:
                        repetitionList.append(c)
                else:
                    pass
            
        else:
            pass
            
    
    for rep in repetitionList:
        fc = remove_bookMark(fc,currentFolder,rep)

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



if __name__ == "__main__":

    currentRabbitVersion = int(args.version)
    currentFileAddress = args.file
    currentOutputFolder = args.output

    file = open(currentFileAddress, "r", encoding="UTF-8")

    fileContents = file.readlines()
    fc = fileContents

    root = parse_html_to_treeView(fc)

    execute(root)
    root = parse_html_to_treeView(fc)

    removeOld(root)
    root = parse_html_to_treeView(fc)

    file = open(currentOutputFolder,"w", encoding="UTF-8")

    result = "".join(fc)
    file.write(result)