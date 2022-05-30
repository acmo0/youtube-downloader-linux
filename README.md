# Youtube Downloader Linux
***
## Compatibility
Tested on ubuntu 20.04LTS and Kali linux. Should work on any debian-like distros.
## Features
- Search on youtube directly from the application
- Download videos and playlists in audio format (m4a, mp3, wav,flac,...)
## Download
### Using deb package
- [Download .deb file from lastest release](https://github.com/acmo0/youtube-downloader-linux/releases/latest)
- Install it using apt (assuming you are in the directory where is located your downloaded file)
```
sudo apt install ./youtube-downloader.deb
```
### Using tar archive
- [Download .tar.gz file from lastest release](https://github.com/acmo0/youtube-downloader-linux/releases/latest)
- Go where you have downloaded the archive and then type
```
tar -xvf youtube-downloader-<version number>.tar.gz
cd youtube-downloader
sudo make install
```
## Uninstallation
- If installed with apt, type ```sudo apt remove youtube-downloader```
- If installed with .tar.gz file, type ```sudo bash /usr/local/lib/youtube-downloader/uninstall```

## Credits
-[yt-dlp](https://github.com/yt-dlp/yt-dlp) The Unlicense
-[youtube-search-python](https://github.com/alexmercerind/youtube-search-python) MIT License

