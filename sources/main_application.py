import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject

import shutil
from downloader_gui import MainWindow

class YoutubeDownloaderApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="com.gregoire.youtubeDownloader",flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)
    
    def on_activate(self, data=None):
        main = MainWindow(self)
        self.temp_directory = main.temp_directory

if __name__ == "__main__":
    app = None
    try:
        app = YoutubeDownloaderApplication()
        app.run(None)
    except Exception as e:
        print(e)
        shutil.rmtree(app.temp_directory)
