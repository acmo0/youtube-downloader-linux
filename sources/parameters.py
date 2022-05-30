import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,GObject, GdkPixbuf,Pango,GLib
import time
class Parameters:
	def __init__(self,application,layout_folder,font_size,app_config_interface):
		self.font_size = font_size
		self.app_config_interface = app_config_interface
		self.app_config = self.app_config_interface.getcfg()
		self.application = application
		self.layout_folder = layout_folder
		self.builder = Gtk.Builder()
		self.builder.add_from_file(self.layout_folder+"parameter.glade")
		self.main_window = self.builder.get_object("parameters_window")
		self.box = self.builder.get_object("parameters_box")
		self.builder.connect_signals(self)
		self.main_window.set_application(self.application)
		self.main_window.set_title('Youtube Downloader - Parameters')
		self.main_window.maximize()
		self.main_window.show_all()
		self.entries_dir = []
		self.entries_dis = []
		self.entries_down = []
		self.layout_dir = []
		self.layout_dis = []
		self.layout_down = []
		print(self.app_config)
		self.pack_parameters_directories()
		self.pack_parameters_display()
		self.pack_parameters_download()
		self.pack_parameters_display()
		
	def close(self):
		self.main_window.destroy()
	def pack_parameter(self,parameter):
		label = Gtk.Label()
		label.modify_font(Pango.FontDescription('Dejavu Sans Mono '+str(self.font_size)))
		label.set_text(parameter[0]+' : ')
		label.set_visible(True)
		entry = Gtk.Entry()
		entry.set_text(parameter[1])
		entry.set_name(parameter[2])
		entry.set_visible(True)
		layout = Gtk.Box()
		layout.set_homogeneous(False)
		if parameter[3]=='dir':
			self.entries_dir.append(entry)
			self.layout_dir.append(layout)
		elif parameter[3]=='dis':
			self.entries_dis.append(entry)
			self.layout_dis.append(layout)
		elif parameter[3]=='down':
			self.entries_down.append(entry)
			self.layout_down.append(layout)
		
		layout.set_orientation(Gtk.Orientation.HORIZONTAL)
		layout.set_spacing(5)
		layout.set_visible(True)
		layout.pack_start(label, False, False, 5)
		layout.pack_start(entry, False, False, 5)
		self.box.pack_start(layout,False,False,10)

	def on_directories_button_clicked(self,object,data=None):
		print("on_directories_button_clicked")
		self.pack_parameters_directories()
	def on_download_button_clicked(self,object,data=None):
		print("on_download_button_clicked")
		self.pack_parameters_download()
	def on_display_clicked(self,object,data=None):
		print("display")
		self.pack_parameters_display()
	def on_cancel_clicked(self,object,data=None):
		self.main_window.destroy()
	def on_validate_clicked(self,object,data=None):
		config = {}
		for entry in self.entries_dir:
			if entry.get_text() == "":
				self.pack_parameters_directories()
				entry.grab_focus()
				return
			folder = entry.get_text()
			if folder[-1] != '/':
				folder += "/"

			config[entry.get_name()] = folder

		for entry in self.entries_dis:
			if entry.get_text() == "":
				self.pack_parameters_display()
				entry.grab_focus()
				return
			config[entry.get_name()] = entry.get_text()
		for entry in self.entries_down:
			if entry.get_text() == "" or ((not entry.get_text() in ['m4a','mp3','wav','opus','aac','flac','alac']) and entry.get_name() == 'dl_format'):
				self.pack_parameters_download()
				entry.grab_focus()
				return
			config[entry.get_name()] = entry.get_text()
		self.app_config_interface.writecfg(config)
		self.close()
	def pack_parameters_directories(self):
		if self.layout_dir == []:
			valable_keys = ['default_save_folder','layout_folder','temp_folder', 'image_folder', 'font_folder']
			cor = ["Default save folder","Application layout folder","Application temporary folder","Application image folder","Application font folder"]
			for key in valable_keys:
				self.pack_parameter([cor[valable_keys.index(key)],self.app_config[key],key,'dir'])
		else:
			for layout in self.layout_dis:
				for item in layout.get_children():
					item.set_visible(False)
				layout.set_visible(False)
			for layout in self.layout_down:
				for item in layout.get_children():
					item.set_visible(False)
				layout.set_visible(False)
			for layout in self.layout_dir:
				for item in layout.get_children():
					item.set_visible(True)
				layout.set_visible(True)
	def pack_parameters_download(self):
		if self.layout_down == []:
			valable_keys = ['dl_format']
			cor = ["Download format (m4a,mp3,wav,opus,aac,flac,alac)"]
			for key in valable_keys:
				self.pack_parameter([cor[valable_keys.index(key)],self.app_config[key],key,'down'])
		else:
			for layout in self.layout_dis:
				for item in layout.get_children():
					item.set_visible(False)
				layout.set_visible(False)
			for layout in self.layout_dir:
				for item in layout.get_children():
					item.set_visible(False)
				layout.set_visible(False)
			for layout in self.layout_down:
				for item in layout.get_children():
					item.set_visible(True)
				layout.set_visible(True)
	def pack_parameters_display(self):
		if self.layout_dis == []:
			valable_keys = ['label_size']
			cor = ["Font size"]
			for key in valable_keys:
				self.pack_parameter([cor[valable_keys.index(key)],self.app_config[key],key,'dis'])
		else:
			for layout in self.layout_dir:
				for item in layout.get_children():
					item.set_visible(False)
				layout.set_visible(False)
			for layout in self.layout_down:
				for item in layout.get_children():
					item.set_visible(False)
				layout.set_visible(False)
			for layout in self.layout_dis:
				for item in layout.get_children():
					item.set_visible(True)
				layout.set_visible(True)