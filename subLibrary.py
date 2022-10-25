import re

'''

def get_type(s: str): -> str : html의 종류 보여줌. gui 표기되는건 디렉토리, 북마크로 있음.
def get_text(roughString) -> str 해당 디렉토리 북마크의 이름을 얻음.
def get_link(roughString): -> 북마크의 링크를 얻음.
def set_link(roughstring:str, newLink:str): -> 북마크의 링크를 변경함.
def set_text (roughString: str, newText:str): -> 북마크, 폴더의 이름을 바꿈.

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
    if strType == "rootfolder" or strType == "newfolderName" or strType == "bookMark":
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

def find_last_children_lineNum (fc, folderline):

    startIndex = folderline
    i = startIndex + 1
    count  = 0
    while True : 
        if get_type(fc[i]) == "newfolder":
            count += 1
        elif get_type(fc[i]) == "end":
            count -= 1
        else:
            pass

        if count == 0 :
            break

        i += 1
    return i - 1

def find_first_children_lineNum (fc, folderline):

    result = folderline + 2

    return result

def get_folder_end (fc, folderline):

    startIndex = folderline
    i = startIndex + 1
    count  = 0
    while True : 
        if get_type(fc[i]) == "newfolder":
            count += 1
        elif get_type(fc[i]) == "end":
            count -= 1
        else:
            pass

        if count == 0 :
            break

        i += 1
    return i 


def is_folder_empty(fc,folderline):
    if get_type(fc[find_first_children_lineNum (fc, folderline)]) == "end":
        return True
    else:
        return False

def get_prefix_spaceNum(roughText):

    count = 0

    for c in roughText:
        if c == " ":
            count += 1
        else:
            break
    

    return count


def get_tag_content(roughText):
    p = re.compile("<.+?>")
    lineContent = roughText.strip()

    text_type = get_type(roughText)

    target =  p.findall(roughText)[1][1:-1]
    result = []
    for e in target.split(' '):
        
        if '=' not in e:
            pass
        else:
            index = None
            for i in range(len(e)):
                if e[i] == "=":
                    index = i
                    break
                else:
                    pass

            tag = e[0:i]
            content = e[i+2:-1]
            result.append((tag,content))

    return result

if __name__ == "__main__" :
    a = '''<DT><H3 ADD_DATE="1663067002" LAST_MODIFIED="1663731763">최신화까지 다본거</H3>'''
    b = '''<DT><A HREF="http://povis.postech.ac.kr/irj/portal" ADD_DATE="1630989655" ICON="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACNElEQVQ4jdWSXUiTcRTGf/93Y9p0pm5BdSNI8WoZRF94EeIwQ8i0D4QVBCFFYEEFEWSEbxcVZhp454UpURh0k6mURB9qaCghYQWrxMgcUlvics7t3Xa6cIpXXXXT7+acB87znHNx4L9H6Xqrw+v1AqDrTrzeADpOcIHXDxDAhRMn4NJB1xsAPy50bj72xhXUzoINEMBksTeT+dZkXdIJstKDWCxWIuG5xM496Q7lOdctNScKyciwcad1gOZrIzS2HcCRJpw984zjNVspKVyPZZWd3ic+WupfI2ZQdpetVqX7c/otY0P3jOHhn/Jq4DN+/xwq1U77rb1qe/5aOvsn5Eh5LhUlW9Rg31epO79LjX8PRTXbpNVzclNnpHpNuRYRRVHROiWIetDxVlVVFqgPEz6Gx6aoLMtTv80onybn5ULdS+WblWjV4Tybu2JDT9rRQJWh3HE2l96VpvYhmYnE5OO3aZkOhqXt0aAYzUMyHYomno+OJ2IxU37Nm5EfCyI3Onq6MNAABSga29+J53SvDL4PyBKmhGRBIsv6iy8WOWU8lev3O7sADUQlA1APX3ijuTlZ+KZmCEfCpFgTXLk6QtSEy5e2kZ1hS4SsqSlDb0a7m4KeSgwRtegVAKXS68Vht2LGBYVg0cAMLcZr9jgbC7LZdyyt+2B136EdqiXGCjOAuni7oy4aS6Bp2vJ3aTYgAUopybSmmLX5mQ3K7Y4lz142/xNUsWFY/zZQDBiGEfunW1fyB1JQAGCsUAVpAAAAAElFTkSuQmCC">홈 - 학부생 - SAP NetWeaver Portal</A>'''
    result = get_tag_content(b)

    print(result)