# Random RSS Feed generator

This is a small experiment to cook together a python script for dynamically generating an RSS Feed. 

This uses the following external libraries/ datafiles:
1. rfeed.py from the fantastic [rfeed library](https://github.com/svpino/rfeed)
   This does all the heavy-lifting of generating the RSS
2. 1iners.cap and taglines.txt from textfiles.com. These are sample data files. 

Rename any of them to data.txt and run 

`python random-rss.py`

Everytime it gives a new RSS feed. Tested with python 3.6.

