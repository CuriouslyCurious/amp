#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
A script that eases mass-downloading of module files from http://amp.dascene.net
"""

import os
import re
import sys
import gzip
import argparse
import urllib.request
from bs4 import BeautifulSoup

class Artist:
	def __init__(self, handle="", real_name="", country="", ex_handles=[], groups=[]):
		self.handle = handle
		self.real_name = real_name
		self.country = country
		self.ex_handles = ex_handles
		self.groups = groups
	def __repr__(self):
		return ("Handle: %s\nReal Name: %s\nCountry: %s\nEx Handles: %s\nGroups: %s" 
				% (self.handle, self.real_name, self.country, ",".join(self.ex_handles), ",".join(self.groups)))


def get_artist_url(search, option="handle"):
	search_url = urllib.request.urlopen("http://amp.dascene.net/search.php")
	options = get_search_options(search_url)
	print(options)
	artist = ""
	if artist:
		return artist
	else:
		raise Exception("Couldn't find artist %s" % artist)
	
def get_search_options(url):
	s = '<select name="request">'
	options = []
	prev = ""
	soup = BeautifulSoup(url.read(), "html.parser")
	finds = soup.find_all(s)
	for find in finds:
			#value = line[line.find("value="):line.find(">")]
			#name = line[line.find(">")+1:line.find("</")]
		options.append((value, name))
		prev = line
	return options
	
def get_artist_info(url):
	s = '<td class="descript">Handle: </td>'
	soup = BeautifulSoup(url, "html.parser")
	artist = Artist()
	info = iter(soup.find_all(attrs="descript", limit=5))
	artist.handle = next(info).find_next().get_text().strip()
	artist.real_name = next(info).find_next().get_text().strip()
	artist.country = next(info).find_next().img["title"]
	artist.ex_handles = next(info).find_next().get_text().strip().split(',')
	artist.groups = next(info).find_next().get_text().strip().split(',')
	return artist
		
def get_domain(url):
	return re.split("^(?:https?:)?(?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n]+)", url)[1]

def get_modules(url):
	mods = []
	soup = BeautifulSoup(url, "html.parser")
	for mod in soup.find_all(href=re.compile("downmod\S*")):
		link = mod["href"]
		name = mod.get_text()
		mods.append((link, name))
	return mods
	
def remove_bad_pathchars(path):
	return re.sub("[\\\?<>\/:*\"]", "", path)

def download_modules(url):
	artist = get_artist_info(url)
	modules = get_modules(url)
	print(repr(artist))
	try:
		os.makedirs(artist.handle)
	except OSError:
		pass
	
	for mod in modules:
		if mod[1]+".mod" in os.listdir(artist.handle):
			print("'%s.mod' already exists, skipping..." % mod[1])
			continue
		link = "http://amp.dascene.net/"+mod[0]	
		path = os.path.join(artist.handle, remove_bad_pathchars(mod[1]))
		data = urllib.request.urlopen(link).read()
		print("Downloading %s." % mod[1])
		with open(path+".mod", "wb") as f:
			f.write(data)
	
	def commands(parser):
	group = parser.add_mutually_exclusive_group()
	parser.add_argument("url", 
						help="An URL for a page to download all the modules from.")
	group.add_argument("-f", "--find", dest="find",
						help="Search for an artist on amp.")
	return parser
	
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="A script that eases mass-downloading of module files from http://amp.dascene.net")
	parser = commands(parser)
	args = parser.parse_args()
	if args.url:
		if get_domain(args.url) == "amp.dascene.net":
			try:
				url = urllib.request.urlopen(args.url)
			except ValueError:
				raise Exception("Not a valid URL.")
				sys.exit()
			content = url.read()
			download_modules(content)			
		else:
			print("ERROR: Not a valid amp.dascene.net URL.")
	elif args.find:
		artist_url = get_artist_url(args.find)
		download_modules(artist_url)
