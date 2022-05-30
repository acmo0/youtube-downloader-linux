#!/usr/bin/python3
from __future__ import unicode_literals
import threading
import sys
from urllib import request as rq
import requests
import json
import subprocess
import traceback
import time
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import os
import shutil
import tempfile
from httplib2 import ServerNotFoundError
import concurrent.futures
import yt_dlp as youtube_dl
from youtubesearchpython import VideosSearch, PlaylistsSearch
from io import BytesIO

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify


class VideoResearcher:
    def __init__(self,temp_directory,app_config,font_directory="fonts/",debug=False):
        Notify.init('VideoDownloader')
        self.app_config = app_config
        print("config",self.app_config)
        self.videos = []
        self.playlists = []
        self.temp_directory = temp_directory
        self.font_directory = font_directory
        self.videos_to_download = []
        self.debug = debug
        self.thread_list = []
        self.exit_event = False
    def my_hook(self,dict_):
        if dict_['status']=='finished':
            print('Converting...')
        if self.exit_event:
            raise ValueError
    def clearThumbnails(self):
        thumb_dir = self.temp_directory
        if self.temp_directory[-1]!='/':
            thumb_dir += "/"
        for video in self.videos:
            try:

                os.remove(thumb_dir+video['vid']+'.png')
                self.videos= []
            except Exception as e:
                print(e)

        for playlist in self.playlists:
            try:
                os.remove(thumb_dir+playlists['pid']+'.png')
                self.playlists = []
            except Exception as e:
                print(e)
    def addVideoToList(self,video):
        self.videos_to_download.append(video)
    
    def delVideoFromList(self,video):
        try:
            self.videos_to_download.remove(video)
        except ValueError as error:
            print(error)
        except Exception as e:
            traceback.print_exc()
    def search(self,query,research_type,results_max=30):
        print(research_type)
        self.research_type = research_type
        self.clearThumbnails()
        if research_type == 'video':
            self.searchVideo(query)
        else:
            self.searchPlaylist(query)
    def searchVideo(self,query,results_max=30):
        self.query = query
        print("Start query")
        try:
            self.video_searcher = VideosSearch(query,limit=results_max)
        except ServerNotFoundError as pb:
            print("It seems that you don't have any internet connection :", pb)
            
        except Exception as e:
            traceback.print_exc()
            raise
        else:
            print('finish query')
            videos_info = []
            self.videos = []
            for result in self.video_searcher.result()['result']:
                if result["type"] == "video":
                    videos_info.append(result)
            self.videos_info = videos_info
            print('parse results')
            for video in videos_info:
                dict_video = {}
                print("video")
                dict_video['type'] = 'video'
                dict_video['vid'] = video['id']
                dict_video['title'] = self.format_title(video['title'])+' - '+video['duration']
                dict_video['name'] = video['title']
                if 'thumbnails' in video.keys() and video['thumbnails'] != [] and video['thumbnails'] != None:
                    print('normal')
                    dict_video['thumbnail'] = video['thumbnails'][0]
                elif 'richThumbnail' in video.keys() and video['richThumbnail'] != None and video['richThumbnail'] != []:
                    print('rich')
                    dict_video['thumbnail'] = video['richThumbnail']
                else:
                    print('no thumb')
                    dict_video['thumbnail'] = {'url':None}
                dict_video['duration'] = video['duration']
                if dict_video['duration'] != "0:0":
                    self.videos.append(dict_video)
            print('finish parsing')

    def searchPlaylist(self,query,results_max=30):
        self.query = query
        print('start query')
        try:
            self.playlist_searcher = PlaylistsSearch(query, limit=results_max)
        except Exception as e:
            traceback.print_exc()
            raise
        else:
            print("finish query")
            playlists_info = []
            self.playlists = []
            for result in self.playlist_searcher.result()['result']:
                if result['type'] == 'playlist':
                    playlists_info.append(result)
            self.playlists_info = playlists_info
            print("parse result")
            for playlist in playlists_info:
                dict_playlist = {}
                dict_playlist['type'] = 'playlist'
                dict_playlist['pid'] = playlist['id']
                dict_playlist['title'] = self.format_title(playlist['title'])+" - "+playlist['videoCount']+" videos"
                dict_playlist['name'] = playlist['title']
                dict_playlist['link'] = playlist['link']
                if 'thumbnails' in playlist.keys() and playlist['thumbnails'] != [] and playlist['thumbnails'] != None:
                    print('normal')
                    dict_playlist['thumbnail'] = playlist['thumbnails'][0]
                elif 'richThumbnail' in playlist.keys() and playlist['richThumbnail'] != None and playlist['richThumbnail'] != []:
                    print('rich')
                    dict_playlist['thumbnail'] = playlist['richThumbnail']
                else:
                    print('no thumb')
                    dict_playlist['thumbnail'] = {'url':None}
                    dict_playlist['nvideo'] = playlist['videoCount']
                if playlist['videoCount'] != "0":
                    self.playlists.append(dict_playlist)
    def getResults(self):
        if self.research_type == "video":
            return self.videos
        return self.playlists

    def download_image(self,url,image_name, folder,size):
        print("download image")
        image_path = ""
        if folder[-1]=='/':
            image_path = folder+image_name+".png"
        else:
            image_path = folder+"/"+image_name+".png"
        error = False
        if url != None:
            for i in range(3):
                try :
                    response = rq.urlopen(url)
                    stream = BytesIO(response.read())
                    img = Image.open(stream).save(image_path)
                    stream.close()
                    error = False
                    break
                except Exception as e:
                    error = True
                    traceback.print_exc()
                    time.sleep(1)
        if error or url == None:
            image_error = Image.new('RGB',size)
            draw = ImageDraw.Draw(image_error)
            font = ImageFont.truetype(self.font_directory+"Bebas-Regular.ttf", 30)
            draw.text((10.0, 10.0),"ERROR",(255,255,255),font=font)
            image_error.save(image_path)
        return error
        print("finish download image")
    def format_title(self,video_name):
        exp = ["&quot;","&#39;"]
        corr = ["\"","'"]
        for i in range(len(exp)):
            video_name = video_name.replace(exp[i],corr[i])
        
        if len(video_name) >= 80:
            video_name = video_name[0:77]+"..."
        return video_name
    def downloadThumbnails(self, folder):
        if not os.path.isdir(folder):
            try:
                os.mkdir(folder)
            except Exception as e:
                traceback.print_exc()
                raise e
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            if self.research_type == "video":
                for video in self.videos:
                    url = video['thumbnail']['url']
                    size = (video['thumbnail']['width'],video['thumbnail']['height'])
                    image_name = video['vid']
                    folder = self.temp_directory
                    futures.append(executor.submit(self.download_image,url=url,image_name=image_name,folder=folder,size=size))
                for future in concurrent.futures.as_completed(futures):
                    print(future.result())
            else:
                for video in self.playlists:
                    url = video['thumbnail']['url']
                    size = (video['thumbnail']['width'],video['thumbnail']['height'])
                    image_name = video['pid']
                    folder = self.temp_directory
                    futures.append(executor.submit(self.download_image,url=url,image_name=image_name,folder=folder,size=size))
                for future in concurrent.futures.as_completed(futures):
                    print(future.result())
                
    def downloadMp3(self,video,folder):
        t= threading.Thread(target=self._downloadMp3,args=(video,folder,))
        self.notifier = Notify.Notification.new('Video Downloader','Download started')
        self.thread_list.append(t)
        #self.notifier.add_action("stop_callback","Cancel",self.callback,None,None)
        self.notifier.show()
        t.start()
    def callback(self,notif_object, action_name, users_data,arg):
        self.notifier.close()
        print('call_back')
        try:
            self.exit_event = True
        except Exception as e:
            print(e)
    def _downloadMp3(self,video,folder):
        k = 0
        error = False
        print(os.getenv('HTTP_PROXY'))
        while k < 5:
            args = ['yt-dlp','-i','-f','mp3/bestaudio/best','--embed-thumbnail','-x','--audio-format',self.app_config['dl_format'],'-o',folder]
            try:
                if video['type'] == 'video':
                    args.append(video['vid'])
                    cmd = subprocess.Popen(args)
                    error = False
                else:
                    if folder[-1] != '/':
                        folder+='/'
                    args[-1] = folder+"%(playlist_index)s - %(title)s.%(ext)s"
                    print(args[-1])
                    args.append(video['pid'])
                    cmd = subprocess.Popen(args)
                    error = False
            except:
                error = True
                k+=1
                if k == 5:
                    traceback.print_exc()
                    raise
            else:
                break
            print(cmd.stdout,cmd.stderr)
            if self.exit_event:
                print('is set')
                cmd.kill()
            else:
                print('not_set')
        cmd.wait()
        self.notifier = Notify.Notification.new('Video Downloader','Download of'+video["title"]+' finished !')
        self.notifier.show()

        
    def downloadMp3List(self,folder):
        if self.videos_to_download == []:
            raise ValueError("Any videos to download")
            return
        for video in self.videos_to_download:
            self.downloadMp3(video)
        
    def __del__(self):
        self.exit_event = True
        shutil.rmtree(self.temp_directory)
 
