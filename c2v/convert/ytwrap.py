import json
import yt_dlp
import sys
args = sys.argv
print("start1", args)

# progData = {"https://abema.tv/video/episode/444-15_s90_p820": ""}  # 進捗状況データ
progData = {args[1]: ""}
opt = {
    'format': 'worst.3',
    "outtmpl": "%(title)s.%(ext)s",
    "cachedir": False,
    'progress_with_newline': True,
    # 'username': 'xxxx',
    # 'password': 'xxxx',
    # "proxy":"https://49.212.143.246:6666/",
    # "proxy":"https://43.153.188.81:3128/",
}
if len(args) == 4 and args[2] and args[3]:
  opt["username"] = args[2]
  opt["password"] = args[3]
# print(opt)
# sys.exit()
""" https://masayoshi-9a7ee.hatenablog.com/entry/2021/11/06/112639 """
with yt_dlp.YoutubeDL(opt) as ydl:  # yt_dlp.YoutubeDL()をforで繰り返すとダメ
  for url in filter(lambda x: not x[1], progData.items()):
    # print(url[0])
    ydl.download([url[0]])
print("finish1")