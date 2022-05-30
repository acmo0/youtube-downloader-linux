import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,GObject, GdkPixbuf,Pango,GLib
from youtubesearchpython import VideosSearch, PlaylistsSearch,Playlist
from youtube_downloader import VideoResearcher
import os
from httplib2 import ServerNotFoundError
import concurrent.futures
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from urllib import request as rq
import requests
from io import BytesIO
import threading
GObject.threads_init()
class PlaylistDisplayer:
	def __init__(self, application,temp_directory,layout_folder,installation_path,label_size,font_directory,default_directory,playlist,video_searcher):
		self.label_size = label_size
		self.default_directory_download = default_directory
		self.application = application
		self.installation_path = installation_path
		self.temp_directory = temp_directory
		self.layout_folder = layout_folder
		self.playlist_dict = playlist
		self.font_directory = font_directory
		self.videos = []
		self.builder = Gtk.Builder()
		self.builder.add_from_file(self.layout_folder+"playlist_displayer.glade")
		self.main_window = self.builder.get_object("playlist_window")
		self.box = self.builder.get_object("video_box")
		self.spinner = self.builder.get_object("spinner")
		self.title = self.builder.get_object("playlist_title")
		self.button_download = self.builder.get_object('download_all_button')
		button_image = Gtk.Image()
		button_pixbuff = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.installation_path+"download.png", width=32,height=32,preserve_aspect_ratio=True)
		button_image.set_from_pixbuf(button_pixbuff)
		self.button_download.set_image(button_image)
		self.button_download.set_label("Download")
		self.button_download.set_halign(Gtk.Align.END)
		self.button_download.set_valign(Gtk.Align.CENTER)
		self.button_download.set_visible(True)
		self.button_download.connect("clicked", self.on_download_all_button_clicked,playlist)
		self.title.set_text("Playlist : "+self.format_title(self.playlist_dict['name']))
		self.title.modify_font(Pango.FontDescription(str(int(self.label_size)+4)))
		self.spinner.start()
		self.builder.connect_signals(self)
		self.main_window.set_application(self.application)
		self.main_window.set_title('Youtube Downloader - '+self.playlist_dict['name'])
		self.main_window.maximize()
		self.main_window.show_all()
		self.video_searcher = video_searcher
		thread_search = threading.Thread(target=self.getVideos)
		thread_search.daemon = True
		thread_search.start()
		
	def on_download_all_button_clicked(self,object,data=None):
		folder = self.askFolderPlaylist(data)
		if folder != None:
			self.video_searcher.downloadMp3(data,folder)

	def askFolderPlaylist(self,playlist):
		filechooserdialog = Gtk.FileChooserDialog("Save...",None,Gtk.FileChooserAction.SELECT_FOLDER)
		filechooserdialog.set_title("FileChooserDialog")
		filechooserdialog.add_button("_Save", Gtk.ResponseType.OK)
		filechooserdialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
		filechooserdialog.set_default_response(Gtk.ResponseType.OK)
		filechooserdialog.set_current_folder(self.default_directory_download)
		response = filechooserdialog.run()
		filename = None
		if response == Gtk.ResponseType.OK:
		    filename = filechooserdialog.get_filename()
		filechooserdialog.destroy()

		return filename

	def on_download(self,object,data=None):
		folder = self.askFolder(data)
		if folder != None:
			self.video_searcher.downloadMp3(data,folder)
	def askFolder(self,video):
		filechooserdialog = Gtk.FileChooserDialog("Save...",None,Gtk.FileChooserAction.SAVE)
		filechooserdialog.set_title("FileChooserDialog")
		filechooserdialog.add_button("_Save", Gtk.ResponseType.OK)
		filechooserdialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
		filechooserdialog.set_default_response(Gtk.ResponseType.OK)
		filechooserdialog.set_current_name(video['name']+'.mp3')
		response = filechooserdialog.run()
		filename = None
		if response == Gtk.ResponseType.OK:
			filename = filechooserdialog.get_filename()
		filechooserdialog.destroy()
		return filename

	def format_title(self,video_name):
		exp = ["&quot;","&#39;"]
		corr = ["\"","'"]
		for i in range(len(exp)):
			video_name = video_name.replace(exp[i],corr[i])

		if len(video_name) >= 80:
			video_name = video_name[0:77]+"..."
		return video_name

	def getVideos(self):
		self.videos = []
		self.playlist = Playlist(self.playlist_dict['link'])
		while self.playlist.hasMoreVideos:
			self.playlist.getNextVideos()
		for video in self.playlist.videos:
			self.videos.append(self.constructVideo(video))
		self.downloadThumbnails(self.temp_directory)
		GLib.idle_add(self.packVideos)
		GLib.idle_add(self.spinner.stop)
	def packVideos(self):
		for video in self.videos:
			self.packVideo(video)
	def constructVideo(self,video):
		dict_video = {}

		dict_video['type'] = 'video'
		dict_video['vid'] = video['id']
		dict_video['title'] = self.format_title(video['title'])
		dict_video['name'] = video['title']
		if 'thumbnails' in video.keys() and video['thumbnails'] != [] and video['thumbnails'] != None:
			dict_video['thumbnail'] = video['thumbnails'][0]
		elif 'richThumbnail' in video.keys() and video['richThumbnail'] != None and video['richThumbnail'] != []:
			dict_video['thumbnail'] = video['richThumbnail']
		else:
			dict_video['thumbnail'] = {'url':None}
		dict_video['duration'] = video['duration']
		return dict_video
	
	def packVideo(self, video):
		button = Gtk.Button()
		#pixbuf1 = GdkPixbuf.Pixbuf.new_from_file(self.installation_path+"images/download.png")
		button_image = Gtk.Image()

		button_pixbuff = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.installation_path+"download.png", width=24,height=24,preserve_aspect_ratio=True)
		button_image.set_from_pixbuf(button_pixbuff)
		button.set_image(button_image)
		button.set_halign(Gtk.Align.END)
		button.set_valign(Gtk.Align.CENTER)
		button.set_visible(True)
		button.connect("clicked", self.on_download,video)
		layout = Gtk.Box()
		layout.set_orientation(Gtk.Orientation.HORIZONTAL)
		layout.set_spacing(10)
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.temp_directory+"/"+video['vid']+".png", 240,190)

		image = Gtk.Image()
		image.set_visible(True)
		image.set_from_pixbuf(pixbuf)
		label = Gtk.Label()
		label.modify_font(Pango.FontDescription('Dejavu Sans Mono '+str(self.label_size)))
		label.set_text(video['title'])
		label.set_visible(True)
		layout.pack_end(button, False, True, 15)
		layout.pack_start(image, False, False, 5)
		layout.pack_start(label, False, False, 5)

		image.set_alignment(Gtk.Align.START, Gtk.Align.START)
		label.set_valign(Gtk.Align.FILL)

		layout.set_valign(Gtk.Align.END)
		layout.set_halign(Gtk.Align.FILL)
		layout.set_margin_bottom(5)
		layout.set_homogeneous(False)
		layout.set_margin_end(5)
		layout.set_margin_left(30)
		layout.set_visible(True)
		self.box.pack_start(layout, True, False, 0)
		return False

	def downloadThumbnails(self, folder):
		if not os.path.isdir(folder):
			try:
				os.mkdir(folder)
			except Exception as e:
				traceback.print_exc()
				raise e
		with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
			futures = []
			for video in self.videos:
				url = video['thumbnail']['url']
				size = (video['thumbnail']['width'],video['thumbnail']['height'])
				image_name = video['vid']
				folder = self.temp_directory
				futures.append(executor.submit(self.download_image,url=url,image_name=image_name,folder=folder,size=size))
			for future in concurrent.futures.as_completed(futures):
				print(future.result())
	def close(self):
		self.main_window.destroy()
	def download_image(self,url,image_name, folder,size):
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