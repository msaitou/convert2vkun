# settings.py または他のファイル
from django.conf import settings
import subprocess
from subprocess import PIPE
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.urls import reverse
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

# 指定のファイル名
def getConvertFileName(oriFileName):
  # カレントディレクトリのファイルを取得
  current_dir = os.listdir()
  # .mp4 ファイルを抽出
  mp4_files = [file for file in current_dir if file.endswith(".mp4")]

  # ファイル名が一致するかどうかをチェック
  for mp4_file in mp4_files:
    mp4_file2 = mp4_file.replace("⧸", "")
    if mp4_file == oriFileName or mp4_file2 == oriFileName:
      return mp4_file

dPath = ""
@login_required
def download(request, *args, **kwargs):
  print(request.GET)
  if "f_name" in request.GET:
    ffName = dPath + request.GET["f_name"]
    ffName = getConvertFileName(ffName)
    return FileResponse(open(ffName, "rb"), as_attachment=True, filename=ffName)
  else:
    return HttpResponse(status=404)


@login_required
def fileRemove(request, *args, **kwargs):
  if "f_name" in request.GET:
    ffName = dPath + request.GET["f_name"]
    ffName = getConvertFileName(ffName)
    # でmp4のファイルをベースに、リクエストされたファイル名と一致するか確認
    # 無ければ、スラッシュっぽいのを消してチェックして、一致すればそれをダウンロードファイルとして採用
    os.remove(ffName)
  return HttpResponse(status=200)

# pythonコマンドのバージョンを規定する(主にlinux用)
PY_VER = settings.DEFAULT_PY_VER
# PY_VER = "3.13"
pyCmd = "python"  # デフォはこれ
str_ver = subprocess.run("python --version", shell=True, capture_output=True, text=True).stdout
if PY_VER not in str_ver:
  pyCmd = f"python{PY_VER}"
import locale
ENC = locale.getencoding().lower()

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
      # 日本語をファイル名にするときにsjisを指定しないとエラーになったけど気のせい
      yield '{}<br />\n'.format(escape(smart_str(line, encoding=ENC)))
      # yield '{}<br />\n'.format(escape(smart_str(line)))

  def task(cmd):
    """
    バッチを実行
    :rtype: generator
    """
    # gcpのubuntuではこれ入れないと動かん
    # env = os.environ.copy()
    # env['PATH'] = '/home/clonecopyfake/.local/bin:/home/clonecopyfake/work/convert2vkun/.venv/bin:' + env['PATH']
    # return linebreaksbr(run_process_as_generator(cmd, shell=True,env=env))
    # sourceをsubprocessで実行するためにはこれらしい
    # http://mikanbako.blog.shinobi.jp/python/subprocess%E3%83%A2%E3%82%B8%E3%83%A5%E3%83%BC%E3%83%AB%E3%81%A7%E3%82%B7%E3%82%A7%E3%83%AB%E3%81%AB%E4%BE%9D%E5%AD%98%E3%81%99%E3%82%8B%E3%83%97%E3%83%AD%E3%82%BB%E3%82%B9%E3%82%92%E5%AE%9F%E8%A1%8C%E3%81%99%E3%82%8B%E5%A0%B4%E5%90%88%E3%81%AF%E3%80%81executable%E5%BC%95%E6%95%B0%E3%82%92%E5%BF%98%E3%82%8C%E3%81%9A%E3%81%AB
    # BASH = '/bin/bash'
    # return linebreaksbr(run_process_as_generator(cmd, shell=True, executable = BASH))
    return linebreaksbr(run_process_as_generator(cmd, shell=True))

  body = request.POST
  print("POST", body)
  cmd = f"{pyCmd} convert/ytwrap.py"
  # cmd = "printenv"
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


# @receiver(request_finished)
# def signalmethod(sender, **kwargs):
#   print('シグナルが送られました。', sender, kwargs)  # 別スレッドになるのでメインプロセスでの画面操作等不可