from pytube import YouTube
import re
import urllib.request
import threading


def progressFun(chunk: bytes, file_handler: bytes, bytes_remaining: int):
    a = 10

class ControllerClass:
    # controller
    url = ""
    urlList = []
    askResolution = False
    isAutoDownload = True
    onPrefex = True  # put number in title on video list
    folder = './download/'
    resolution = -1
    onList = True
    filesize = 100  # for progress
    title = ""
    index = 0
    listLength = 0
    download_complete = False
    progressFun = progressFun
    progress = 0.0
    speed = 0.0
    jumpedUrl = []


def printTargetDownload():
    i = ControllerClass.index + 1
    size = ControllerClass.listLength
    title = ControllerClass.title
    if ControllerClass.onList:
        print(f'{i} / {size} -> title : {title}')
    else:
        print(f'-> title : {title}')

def getListFormUrl(url, is_on_list):
    if not is_on_list:
        return [url]
    arr = []
    fp = urllib.request.urlopen(url)
    data = str(fp.read())
    regex = "\"url\":\"(/watch\?v=[\w-]*).*?index=\d+"
    matches = re.findall(regex, data)
    i = 1
    for item in matches:
        arr.append(f'https://www.youtube.com{item}')
        print(f'--> {i} : https://www.youtube.com{item}')
        i += 1
    return arr

def getUrlCode(s):
    regexCode = "/watch\?v=[\w-]*"
    matchesCode = re.findall(regexCode, s)

    regexIndex = "index=\d+"
    matchesIndex = re.findall(regexIndex, s)
    nbr = int(re.sub(r'index=', '', str( matchesIndex[0])))
    return str(matchesCode[0]), nbr

def getListUrlFromFile(url, is_on_list):
    if not is_on_list:
        return [url]
    dic = {}
    thefile = open("htmlpage", 'r', encoding='utf-8')
    data = str(thefile.read())
    regex = "href=\"/watch\?v=[\w-]*.*?;index=\d+"
    matches = re.findall(regex, data)
    i = 1
    for item in matches:
        code, index = getUrlCode(item)
        if index not in dic.keys():
            newItem = f'https://www.youtube.com{code}'
            dic[index] = newItem

    a = sorted(dic.keys())
    final = []
    for item in a:
        print(f'{item} => {dic[item]}')
        final.append(dic[item])
    return final

class YoutubeDownloader:

    def askResolutionFun(self, arr, resolution):
        index = 1
        if resolution != -1:
            return resolution
        if ControllerClass.askResolution:
            for item in arr:
                print(f'{index} : {item}')
                index += 1
            i = int(input("chose : ")) - 1
        else:
            i = 0
        return i

    def askToDownload(self, isAutoDownload):
        if isAutoDownload:
            return True
        else:
            return bool(input(f'download this vidio (0/1) : '))

    def downloadVideo(self, url, prefex, resolution=-1):
        yt = YouTube(url, on_progress_callback=ControllerClass.progressFun)
        title = prefex + yt.title
        ControllerClass.title = title
        printTargetDownload()
        arr = yt.streams.filter(mime_type="video/mp4", progressive=True).order_by('resolution').desc()
        selectedResolustion = self.askResolutionFun(arr, resolution)
        ControllerClass.resolution = selectedResolustion
        if selectedResolustion >= 0:
            video = arr[selectedResolustion]
            ControllerClass.filesize = video.filesize
            video.download(ControllerClass.folder, title)
            ControllerClass.resolution = -1
            ControllerClass.title = ""

    def downloadVideoMain(self, url, prefex=""):
        self.downloadVideo(url, prefex)

    def getPrefex(self, i):
        if ControllerClass.onPrefex:
            return f"{i + 1} - "
        else:
            return ""

    def downloadVideoFromList(self, url, i, size):
        ControllerClass.index = i
        ControllerClass.listLength = size
        if self.askToDownload(ControllerClass.isAutoDownload):
            self.downloadVideoMain(url, self.getPrefex(i))

    def downloadList(self, url):
        urls = ControllerClass.urlList
        size = len(urls)
        i = ControllerClass.index
        while i < size:
            self.downloadVideoFromList(urls[i], i, size)
            i += 1
        ControllerClass.download_complete = True
        print("\n\ndownload list complete !!")
        print(ControllerClass.jumpedUrl)

def download():
    #try:
    a = YoutubeDownloader()
    url = ControllerClass.url
    a.downloadList(url)

    #except:
    #    print(f'error occurred -> start again ...')

def startDownload():
    i = 0
    index = ControllerClass.index
    while not ControllerClass.download_complete:
        t1 = threading.Thread(target=download, daemon=True)
        t1.start()
        t1.join()

        if index == ControllerClass.index:
            i += 1
        else:
            i = 0

        if i > 1:
            i = 0
            ControllerClass.jumpedUrl.append(ControllerClass.urlList[ControllerClass.index])
            ControllerClass.index += 1
            if ControllerClass.index >= len(ControllerClass.urlList):
                print('List Consumed !!')
                print(ControllerClass.jumpedUrl)
                break
