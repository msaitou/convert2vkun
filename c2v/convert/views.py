from subprocess import PIPE
import subprocess
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse
# from .models import Choice, Question
from django.views import generic
from django.utils import timezone
from django.http import StreamingHttpResponse
from django.utils.encoding import smart_str
from django.utils.html import escape
from django.core.signals import request_finished
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView)
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
import json
import os

import yt_dlp


class Login(LoginView):
  form_class = LoginForm
  template_name = "convert/login.html"


class Logout(LoginRequiredMixin, LogoutView):
  template_name = "convert/login.html"


class IndexView(LoginRequiredMixin, generic.ListView):  # LoginRequiredMixinがログイン必須
  template_name = 'convert/index.html'
  context_object_name = 'latest_question_list'

  def get_queryset(self):
    """Return the last five published questions(not including those set to be
    published in the future).."""
    # return Question.objects.filter(pub_date__lte=timezone.now()
    #                                ).order_by('-pub_date')[:5]


class MyLogger:
  def debug(self, msg):
    # For compatibility with youtube-dl, both debug and info are passed into debug
    # You can distinguish them by the prefix '[debug] '
    if msg.startswith('[debug] '):
      print(msg)
      pass
    else:
      self.info(msg)

  def info(self, msg):
    print(msg)
    pass

  def warning(self, msg):
    print(msg)
    pass

  def error(self, msg):
    print(msg)

# def download(request, *args, **kwargs):
#   print(request.POST["urls"])
#   fName = "3.mp4"
#   opt = {
#       'username': 'nsksaitou@gmail.com',
#       'password': 'nsksaitou2wsx',
#       'format': 'worst.3',
#       # "rm_cachedir": True,
#       "logger": MyLogger(),
#       # "cachedir": False,
#       "outtmpl": "%(title)s.%(ext)s"+fName,
#   }
#   # ファイル名取得
# # https://stackoverflow.com/questions/74157935/getting-the-file-name-of-downloaded-video-using-yt-dlp
#   urls = request.POST["urls"].split("\n")
#   print(urls)
#   delFlag = True
#   # try:
#   #   YoutubeDL = YoutubeDL or {}
#   #   if YoutubeDL != {} or YoutubeDL:
#   #     delFlag = False
#   # except Exception as e:
#   #   print("とくには")


#   # urls = ["https://abema.tv/video/episode/444-15_s40_p61"]
#   with yt_dlp.YoutubeDL(opt) as ydl:  # yt_dlp.YoutubeDL()をforで繰り返すとダメ
#     # if delFlag:
#     #   ydl.cache.remove()
#     for url in urls:
#       print(url)
#       filename = ydl.download(urls)
#       print(f"fName {filename}")
#   # progData[url[0]] = True
#   # with open(progF, mode='w') as f:
#   #   json.dump(progData, f, indent=2)
#   del YoutubeDL
#   return FileResponse(open(fName, "rb"), as_attachment=True, filename=fName)
# def download(request, *args, **kwargs):
#   print(request.POST["urls"])
#   ffName = "55.mp4"
#   def yt_dlp_monitor(self, d):
#     ffName = d.get('info_dict').get('_filename')
#     # You could also just assign `d` here to access it and see all the data or even `print(d)` as it updates frequently
#   opt = {
#       'username': 'nsksaitou@gmail.com',
#       'password': 'nsksaitou2wsx',
#       'format': 'worst.3',
#       # "rm_cachedir": True,
#       "logger": MyLogger(),
#       # "cachedir": False,
#       # "outtmpl": "%(title)s.%(ext)s",
#       "outtmpl": ffName,
#       # "progress_hooks": [yt_dlp_monitor]  # here's the function we just defined
#   }
#   urls = request.POST["urls"].split("\r\n")
#   print(urls)

#   proc = subprocess.run(['python', 'convert/ytwrap.py'], stdout=PIPE, stderr=PIPE)
#   print(proc.stdout.decode('utf-8').split('\n'))
#   print(proc.stderr.decode('utf-8').split('\n'))
#   print("finish2")
#   return FileResponse(open(ffName, "rb"), as_attachment=True, filename=ffName)
dPath = "C:\\workspace\\convert2vkun\\c2v\\"


@login_required
def download(request, *args, **kwargs):
  print(request.GET)
  if "f_name" in request.GET:
    ffName = dPath + request.GET["f_name"]
    return FileResponse(open(ffName, "rb"), as_attachment=True, filename=ffName)
  else:
    return HttpResponse(status=404)


@login_required
def fileRemove(request, *args, **kwargs):
  if "f_name" in request.GET:
    ffName = dPath + request.GET["f_name"]
    os.remove(ffName)
  return HttpResponse(status=200)


@login_required
def do(request, *args, **kwargs):
  def run_process_as_generator(*args, **kwargs):
    """
    サブプロセス結果をジェネレータで返す
    :rtype: generator
    """
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.STDOUT)
    popen = subprocess.Popen(*args, **kwargs)
    while True:
      line = popen.stdout.readline()
      if line:
        yield line

      if not line and popen.poll() is not None:
        break

  def linebreaksbr(gen):
    """
    ジェネレータの各行に<br />をつける
    念のため smart_str
    :type gen: generator
    :rtype: generator
    """
    for line in gen:
      # 日本語をファイル名にするときにsjisを指定しないとエラーになった
      yield '{}<br />\n'.format(escape(smart_str(line, encoding="sjis")))

  def task(cmd):
    """
    バッチを実行
    :rtype: generator
    """
    env = os.environ.copy()
    #　ubuntuでこれ入れないと動かん
    # env['PATH'] = '/home/clonecopyfake/.local/bin:/home/clonecopyfake/work/convert2vkun/.venv/bin:' + env['PATH']
    return linebreaksbr(run_process_as_generator(cmd, shell=True))

  body = request.POST
  print("POST", body)
  cmd = "python convert/ytwrap.py"
  for key in ["url", "aca", "pass",]:
    if body[key]:
      cmd += f" {body[key]}"
  print(cmd)
  try:
    response = StreamingHttpResponse(
        task(cmd), content_type="text/html; charset=utf-8")
    return response
  finally:
    print("完了")


@receiver(request_finished)
def signalmethod(sender, **kwargs):
  print('シグナルが送られました。', sender, kwargs)  # 別スレッドになるのでメインプロセスでの画面操作等不可
