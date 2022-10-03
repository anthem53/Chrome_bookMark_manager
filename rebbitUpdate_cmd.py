from ssl import _create_unverified_context
from html_parser import *
from subLibrary import *
import argparse

fc = None
currentRabbitVersion = 154

# 인자값을 받을 수 있는 인스턴스 생성
parser = argparse.ArgumentParser(description='사용법 테스트입니다.')

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

    recentFolder = None
    currentFolder = None
    def findRecentFolder (elem):
        if elem.type == "rootfolder":
            for child in elem.childrenList:
                execute(child)
        elif elem.type == "newfolderName" :
            if elem.text == "최신화까지 다본거":
                global recentFolder
                recentFolder = elem
            elif elem.text == "볼거":
                global currentFolder
                currentFolder = elem

            else:
                for child in elem.childrenList:
                    execute(child)
        elif elem.type == "bookMark":
            pass

        else:
            print("Fail execute")
    
    findRecentFolder(root)
    print(recentFolder.text)
    print(currentFolder.text)
    

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




quit(1)
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

    file = open(currentOutputFolder,"w", encoding="UTF-8")

    result = "".join(fc)
    file.write(result)