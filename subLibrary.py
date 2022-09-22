import re

'''

def get_type(s: str): -> str : html의 종류 보여줌. gui 표기되는건 디렉토리, 북마크로 있음.
def get_text(roughString) -> str 해당 디렉토리 북마크의 이름을 얻음.
def get_link(roughString): -> 북마크의 링크를 얻음.
def set_link(roughstring:str, newLink:str): -> 북마크의 링크를 변경함.
def set_text (roughString: str, newText:str): -> 북마크 폴더의 이름을 바꿈.

'''


# type : end  bookMark  newfolder newfolderName rootfodler
reDict = {}
reDict['end'] = re.compile('</DL><p>')
reDict['bookMark'] = re.compile('<DT><A')
reDict['newfolder'] = re.compile('<DL><p>')
reDict['newfolderName'] = re.compile('''<DT><H3''')
reDict['rootfolder'] = re.compile('<H1>')


def get_type(s: str):

    s = s.strip()
    for key in reDict:
        if reDict[key].match(s) != None:
            return key
            # find type
        else:
            pass
            # This is incorrect
    return None


def get_text(roughString):
    # end  bookMark  newfolder newfolderName rootfodler
    strType = get_type(roughString)
    #print(strType)
    if strType == "rootfodler" or strType == "newfolderName" or strType == "bookMark":
        isbracket = False
        textStartIndex = None
        textEndIndex = None
        for i in range(len(roughString)):
            if isbracket == True : 
                if roughString[i] == ">":
                    isbracket = False 
            else:
                if roughString[i] == "<":
                    isbracket = True
                    if textStartIndex != None :
                        textEndIndex = i
                else :
                    if textStartIndex == None:
                        textStartIndex = i
        if textStartIndex == None :
            temp = "No Name BookMark"
        else :
            temp = roughString[textStartIndex:textEndIndex]
        #print(temp)
        #print("textStartIndex",textStartIndex)
        #print("textEndIndex",textEndIndex)

        return temp
    else :
        return "Fail to get text from tag"

def get_link(roughString):

    # end  bookMark  newfolder newfolderName rootfodler
    strType = get_type(roughString)
    #print(strType)
    if strType == "bookMark":
        #print(roughString[12])
        startIndex = 13
        endIndex = None
        for i in range(startIndex,len(roughString)):
            if roughString[i] == '"':
                endIndex = i 
                break
        temp = roughString[startIndex:endIndex]
        #print(temp)

        return temp
    else:
        return None


def set_link(roughstring:str, newLink:str):

    if get_type(roughstring) != "bookMark":
        return None

    start = None
    end = None

    i = 0
    for c in (roughstring):
        
        if start == None and c == '"':
            start = i
        elif start != None and end == None and c == '"':
            end = i
            break
        else:
            pass
        i += 1
        pass
    frontPart = roughstring[0:start+1]
    backPart = roughstring[end:len(roughstring)]

    result = frontPart+newLink+backPart
    return result

def set_text (roughString: str, newText:str):
    lineType = get_type(roughString)
    if lineType != "bookMark" and lineType != "newfolderName":
        return None
    i = 0
    remainNum = 2
    sNum = None
    eNum = None
    for c in roughString:
        if remainNum > 0 :
            if c == ">" :
                remainNum -= 1
        else:
            if sNum == None :
                sNum = i
            elif c =="<":
                eNum = i 
                break
            else:
                pass

        i += 1
        
    frontPart =roughString[0:sNum]
    endPart = roughString[eNum:len(roughString)]

    result = frontPart + newText + endPart
    return result



if __name__ == "__main__" :
    a = '''<DT><H3 ADD_DATE="1663067002" LAST_MODIFIED="1663731763">최신화까지 다본거</H3>'''
    b = "테스트하고 있는거임. ㅇㄱㄹㅇ"
    result = set_text(a,b)

    print(result)