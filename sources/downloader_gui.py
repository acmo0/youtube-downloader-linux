import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Notify', '0.7')
from gi.repository import Notify
from gi.repository import Gtk,GObject, GdkPixbuf,Pango,GLib
from tempfile import mkdtemp
import os
from pathlib import Path
import time
from youtube_downloader import *
from playlist_displayer import PlaylistDisplayer
from parameters import Parameters
import threading
GObject.threads_init()
from config import AppConfig

class MainWindow:
    def on_parameters_activate(self,object,data=None):
        print("parameters")
        p = Parameters(self.application,self.layout_folder,self.label_size,self.config_parser)
        self.windows.append(p.main_window)
    def on_download(self,object,data=None):
        if data['type'] == 'video':
            folder = self.askFolder(data)
            if folder != None:
                self.video_searcher.downloadMp3(data,folder)
        else:
            folder = self.askFolderPlaylist(data)
            if folder != None:
                self.video_searcher.downloadMp3(data,folder)
    def on_details(self,object,data=None):
        p = PlaylistDisplayer(self.application,self.temp_directory,self.layout_folder,self.image_path,self.label_size,self.font_directory, self.config['default_save_folder'],data,self.video_searcher)
        self.windows.append(p.main_window)
    def packVideo(self, video):

        button = Gtk.Button()
        button_details = Gtk.Button().new_from_stock(Gtk.STOCK_INFO)
        button_details.set_always_show_image(True)
        button_image = Gtk.Image()

        button_pixbuff = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.image_path+"download.png", width=24,height=24,preserve_aspect_ratio=True)
        button_image.set_from_pixbuf(button_pixbuff)
        button.set_image(button_image)
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.CENTER)
        button.set_visible(True)
        button.connect("clicked", self.on_download,video)
        if video['type'] == "playlist":
            button_details.set_halign(Gtk.Align.END)
            button_details.set_valign(Gtk.Align.CENTER)
            button_details.set_visible(True)
            button_details.connect("clicked", self.on_details,video)

        layout = Gtk.Box()
        layout.set_orientation(Gtk.Orientation.HORIZONTAL)
        layout.set_spacing(10)
        pixbuf = None
        if video['type'] == 'video':
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.temp_directory+"/"+video['vid']+".png", 240,190)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.temp_directory+"/"+video['pid']+".png", 240,190)

        image = Gtk.Image()
        image.set_visible(True)
        image.set_from_pixbuf(pixbuf)
        label = Gtk.Label()
        label.modify_font(Pango.FontDescription('Dejavu Sans Mono '+str(self.label_size)))
        label.set_text(video['title'])
        label.set_visible(True)
        layout.pack_end(button, False, True, 15)
        if video['type'] == "playlist":
            layout.pack_end(button_details,False,True,10)
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
        self.research_displayer.pack_start(layout, True, False, 0)
        return False

    def askFolder(self,video):
        filechooserdialog = Gtk.FileChooserDialog("Save...",None,Gtk.FileChooserAction.SAVE)
        filechooserdialog.set_title("FileChooserDialog")
        filechooserdialog.add_button("_Save", Gtk.ResponseType.OK)
        filechooserdialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        filechooserdialog.set_default_response(Gtk.ResponseType.OK)
        filechooserdialog.set_current_folder(self.config['default_save_folder'].replace('~',os.path.expanduser('~')))
        filechooserdialog.set_current_name(video['name']+'.'+self.config['dl_format'])
        response = filechooserdialog.run()
        filename = None
        if response == Gtk.ResponseType.OK:
            filename = filechooserdialog.get_filename()
        filechooserdialog.destroy()
        return filename
    def askFolderPlaylist(self,playlist):
        filechooserdialog = Gtk.FileChooserDialog("Save...",None,Gtk.FileChooserAction.SELECT_FOLDER)
        filechooserdialog.set_title("FileChooserDialog")
        filechooserdialog.add_button("_Save", Gtk.ResponseType.OK)
        filechooserdialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        filechooserdialog.set_default_response(Gtk.ResponseType.OK)
        filechooserdialog.set_current_folder(self.config['default_save_folder'].replace('~',os.path.expanduser('~')))
        response = filechooserdialog.run()
        filename = None
        if response == Gtk.ResponseType.OK:
            filename = filechooserdialog.get_filename()
        filechooserdialog.destroy()
        return filename
    def packVideos(self):
        for video in self.results:
            self.packVideo(video)

    def clearViewer(self):
        print("clearViewer")
        for item in self.research_displayer.get_children():
            self.research_displayer.remove(item)
        return False

    def search_and_download(self):
        self.video_searcher.search(self.search_entry.get_text(),self.research_type)
        self.video_searcher.downloadThumbnails(self.temp_directory)
        self.results = self.video_searcher.getResults()
        GLib.idle_add(self.clearViewer)
        GLib.idle_add(self.packVideos)

    def on_search_button_clicked(self,object):
        self.clearViewer()
        if self.search_entry.get_text() != None and  self.search_entry.get_text() !="":
            self.research_displayer.add(self.spinner)
            self.research_type = self.combobox.get_active_id()
            self.spinner.start()
            thread_search = threading.Thread(target=self.search_and_download)
            thread_search.daemon = True
            thread_search.start()

    def quit(self,obj = None,data=None):
        for window in self.windows:
            try:
                window.destroy()
            except:
                pass
    def __init__(self, application,tmp_dir_folder="/tmp/"):
        self.config_parser = AppConfig()
        self.config = self.config_parser.getcfg()
        self.image_path = self.config['image_folder']
        self.tmp_dir_folder = self.config['temp_folder']
        self.application = application
        self.layout_folder = self.config['layout_folder']
        self.font_directory = self.config['font_folder']
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.layout_folder+"main_layout.glade")
        self.main_window = self.builder.get_object("main_window")
        self.spinner = self.builder.get_object('spinner')
        self.label_size = int(self.config['label_size'])
        self.windows = []
        self.spinner.stop()
        self.builder.connect_signals(self)
        self.combobox = self.builder.get_object('combo')
        self.research_type = self.combobox.get_active_id()
        self.temp_directory = mkdtemp(prefix="ytdownloader.", dir=self.tmp_dir_folder)
        self.search_entry = self.builder.get_object("search_entry")
        self.research_displayer = self.builder.get_object("research_displayer")
        self.research_displayer.remove(self.spinner)
        self.video_searcher = VideoResearcher(self.temp_directory,self.config,self.font_directory)
        self.main_window.connect("destroy", self.quit)
        self.main_window.set_application(self.application)
        self.main_window.set_icon_from_file(self.image_path+"icon.png")
        self.main_window.set_title('Youtube Downloader')
        self.main_window.maximize()
        self.main_window.show_all()
