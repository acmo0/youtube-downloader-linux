def readfile(filename):
	data=None
	try:
		with open(filename, "r") as f:
			data = f.read()
	except:
		pass
	return data

def get_cfg_path():
	cfg_path = ""
	with open("/usr/local/lib/youtube-downloader/var.cfg" ,"r") as f:
	#with open("var.cfg" ,"r") as f:
		cfg_path = f.read()
	return cfg_path.split("\n")[0].replace(" ","")

def get_default_config_path():
	cfg_path = ""
	with open("/usr/local/lib/youtube-downloader/var.cfg" ,"r") as f:
	#with open("var.cfg" ,"r") as f:
		cfg_path = f.read()
	return cfg_path.split("\n")[1].replace(" ","")
	
def cleantab(tab):
	while None in tab:
		tab.remove(None)
	while "" in tab:
		tab.remove("")
	for i in range(len(tab)):
		tab[i] = tab[i].replace(" ","")
		tab[i] = tab[i].replace("\t","")
		tab[i] = tab[i].replace("\n","")
	return tab

def extractcfg(cfg):
	lines=cfg.split('\n')
	lines = cleantab(lines)
	values = {}
	for line in lines:
		separate = line.split(":")
		separate = cleantab(separate)
		if separate[0][0] != "#":
			if len(separate)==2:
				values[separate[0]] = separate[1]
			elif  (len(separate)==3 and len(cleantab(line.split('{')))==2):
					values[separate[0]] = separate[1]+':'+separate[2]
	return values

class AppConfig:

	def writecfg(self,config, config_path=None):
		if config_path==None:
			config_path = self.config_file
		if type(config)!=dict:
			raise TypeError("Must be dict, not "+str(type(config)))
		else:
			data = ""
			for key in config.keys():
				data+=key+":"+config[key]+'\n'
			with open(config_path, "w+") as f:
				f.write(data)

	def getcfg(self, config_path=None):
		if config_path == None:
			config_path = self.config_file
		data = readfile(config_path)
		if data != None:
			return extractcfg(data)
		else:
			return None

	def __init__(self):
		self.config_file = get_cfg_path()
		self.config = self.getcfg()
		if self.config == None or self.config == {}:
			default_config_path = get_default_config_path()
			self.default_config = self.getcfg(default_config_path)
			self.writecfg(self.default_config, self.config_file)
			self.config = self.getcfg()
			print(self.config)


