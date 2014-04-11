#!/usr/bin/env python3
#coding: utf-8

import os
import json
import time
import sys
import re
import shutil


import config

newPosts = config.newPosts
articlesPerPage = config.articlesPerPage
posts = config.posts
blogPath = config.blogPath
email = config.email
files = config.files
title = config.title
url = config.url



def init():
	if not os.path.isdir(newPosts):
		os.makedirs(newPosts)	##pfad noch relativ machen!
	else:
		print(newPosts + " exists already!")
	
	if not os.path.isdir(posts):
		os.makedirs(posts)	##pfad noch relativ machen!
	else:
		print(posts + " exists already!")

	if not os.path.isdir(blogPath):
		os.makedirs(blogPath)	##pfad noch relativ machen!
	else:
		print(blogPath + " exists already!")

	if not os.path.isdir(blogPath+"/singlePosts"):
		os.makedirs(blogPath+"/singlePosts")	##pfad noch relativ machen!
	else:
		print(blogPath+"/singlePosts" + " exists already!")
	
	if not os.path.isdir(files):
		os.makedirs(files)	##pfad noch relativ machen!
	else:
		print(files + " exists already!")
	
	config = []
	if os.path.isfile('posts.db'):
		print("there is a posts.db file - keeping it")
	else:
		postFile = open('posts.db', "w")
		postFile.close()
	if os.path.isfile(blogPath + '/style.css'):
		print("there is a style.css file - keeping it")
	else:
		shutil.copyfile("templates/style.css", blogPath + "/style.css") 

	if os.path.isfile(blogPath + '/singlePosts/style.css'):
		print("there is a style.css file in singlePosts - keeping it")
	else:
		shutil.copyfile("templates/style.css", blogPath + "/singlePosts/style.css") 
	if os.path.isfile('links.html'):
		print("there is a links.html file - keeping it")
	else:
		linkfile = open('links.html', "w")
		linkfile.close()

	print("...start blogging! :)")


def parseAttachments(lines):
	attached = []
	#regex für images
	reg=re.compile('(.*)<image (.*)>(.*)')
	for line in lines:
		while reg.match(line):
			line=line.split("<image ")
			line=line[1].split(">")
			line=line[0]
			attached.append(line)
	return attached

def resizeImage(path, filename):
	os.system("convert " + path + "/" + filename + " -resize 1400x1400\> " + path + "/" + filename )
	os.system("convert " + path + "/" + filename + " -resize 500x500\> " + path  + "/thumb_" + filename ) 

def add():
	objects = os.listdir(newPosts)
	objects.sort()
	existingFiles = os.listdir(posts)
	for objectname in objects:
		addSpecific(objectname)

def addSpecific(name):
	db = open('posts.db', "a")
	objects = os.listdir(newPosts)
	if (name in objects) and len(name.split("."))<2:	#nur wenns den namen gibt und der keine dateiendung hat (also keine bilder undso parsen)
		existingFiles = os.listdir(posts)
		newObjectname = name
		i=2
		#einen schönen namen finden dens nochnicht gibt
		while newObjectname in existingFiles:
			newObjectname = name + str(i)
			i+=1
		#checken obs anhänge hat
		lines=open(newPosts + "/" + name).readlines()
		attached = parseAttachments(lines)
		for thing in attached:
			if thing in os.listdir(files):
				print("found attachment, moving it to " + posts + "/" + newObjectname + "_files/" + thing)
				if not os.path.isdir(posts + "/" + newObjectname + "_files/"):
					os.mkdir(posts + "/" + newObjectname + "_files/")
				os.rename(files + "/" + thing, posts + "/" + newObjectname + "_files/" + thing)
				#wenns ein bild ist, verkleinern
				reg=re.compile('((.*)\.png)|((.*)\.jpg)|((.*)\.jpeg)')
				if reg.match(thing):
					resizeImage(posts + "/" + newObjectname + "_files", thing)
			else:
				print("attachment not found in " + files + "!\nnot added this post...\n")
				return False
		#neuen eintrag im db file machen
		db.write(str(int(time.time())) + ' : ' + newObjectname + "\n")
		#datei wegnehmen und ins archiv packen
		os.rename(newPosts + "/" + name, posts + "/" + newObjectname)
		print("added " + name + " as "+ newObjectname + " to db")
		return True
	else:
		if len(objects) != 0:
			print("post not found!")
			print("existing new Posts are:")
			for objectname in objects:
				print("- " +objectname)
		else:
			print("no new posts found!")
		return False
	db.close()

def remove(name):
	db = open('posts.db', "r")
	
	lines = db.readlines()
	newLines = []
	for line in lines:	
		split=line.split("\n")
		split=split[0].split(" : ")
		
		if split[1] != name:
			#nicht gesuchte behalten
			newLines.append(line)
		else:
			#das gefundene löschen
			print("removing " + name + "from db!")
			existingFiles = os.listdir(posts)

			if name in existingFiles:
				#datei löschen
				print("...and the article file") 
				os.remove(posts + "/" + name)
			else:
				print(name + " File not found - that should not happen...")
			#wenns aus der db raus ist, bin ich zufrieden
	db.close()
	if lines == newLines:
		print("post not found!")
		return False
	else:
		db = open('posts.db', "w")
		db.writelines(newLines)
		db.close()
		return True

def show():
	db = open('posts.db', "r")
	lines = db.readlines()
	for line in lines:
		split=line.split("\n")
		split=split[0].split(" : ")
		print(split[1] + " at " + time.ctime(int(split[0])))

def htmlify(path, thisfile, onlyAttachments):
	lines = open(path + "/" + thisfile).readlines()
	newLines = []
	if not onlyAttachments:
		lines[0] = "<h3>" + lines[0].split("\n")[0] + "</h3>"
	
	reg=re.compile('(.*)<image (.*)>(.*)')
	for line in lines:
		while reg.match(line):
			filename=line.split("<image ")
			partbefore=filename[0]
			filename=filename[1].split(">")
			partafter=filename[1]
			filename=filename[0]
			line=partbefore + "<a href='" + url + "/singlePosts/" + thisfile + "_files/" + filename + "'>" + \
					"<img src='" + url + "/singlePosts/" + thisfile + "_files/thumb_" + filename + "'/>" \
					+ "</a>" + partafter
					
		line=line.replace("\n", "</br>\n")
		newLines.append(line)
	return newLines

def createSinglePost(time, title, content, fromPage, htmlTop, htmlBottom):
	f = open(blogPath + "/" + "singlePosts/" + title + ".html", "w") #hier hin
	f.writelines(htmlTop)
	
	f.write("<div id='body'>")
	f.write("<div id = 'article'>")
	f.writelines(content)
	f.write("</div>")
	f.write("<div id='nav'>")
	f.write("<a href='../page" + str(fromPage) + ".html'><<</a>")
	f.write("</div></div>") #/nav /body
	f.writelines(htmlBottom)

def rmleaf(path):
	print("rmleaf: " + path)
	for f in os.listdir(path):
		if os.path.isfile(path + "/" + f):
			os.remove(path + "/" + f)
		else:
			rmleaf(path + "/" + f)
			os.rmdir(path + "/" + f)
	os.rmdir(path)

def createFeed():
	feed = open(blogPath + "/feed.xml", "w")
	feed.write("<?xml version='1.0' encoding='UTF-8' ?>\n")
	feed.write("<rss version='2.0'>\n")
	feed.write("<channel>")
	feed.write("<title>" + title + "</title>")
	feed.write("<description></description>") ##TODO!
	feed.write("<link>" + url +  "</link>")
	feed.write("<lastBuildDate></lastBuildDate>") ##TODO!
	feed.write("<ttl>1800</ttl>")

	postFile = open('posts.db', "r")
	lines = postFile.readlines()
	lines.reverse()
	for line in lines:
		split=line.split("\n")
		split=split[0].split(" : ")
		currArticle = htmlify(posts, split[1], True)

		feed.write("<item>")
		feed.write("<title>" + currArticle[0].split("</br>\n")[0] + "</title>\n")
		feed.write("<description><![CDATA[")
		for line in currArticle[1:]:
			feed.write(line)
		feed.write("]]></description>\n")
		feed.write("<link>" + url + "/" + split[1] + ".html</link>")
		feed.write("<guid>" + url + "/" + split[1] + ".html</guid>\n")
		feed.write("<pubDate>" + time.ctime(int(split[0])) + "</pubDate>\n")
		feed.write("</item>")
	feed.write("</channel>") 
	feed.write("</rss>\n")                                                                                                                  
#<lastBuildDate>2013-11-14 17:16:22 +0100</lastBuildDate>





#rebuild the blog!
def rebuild():
	#alten krempel löschen
	for f in os.listdir(blogPath):
		if os.path.isfile(blogPath + "/" + f) and "page" in f:
			os.remove(blogPath + "/" + f)
	#singleposts auch löschen
	for f in os.listdir(blogPath + "/singlePosts"):
		if os.path.isfile(blogPath + "/singlePosts/" + f):
			if not ".css" in f:
				os.remove(blogPath + "/singlePosts/" + f)
		else:
			rmleaf(blogPath + "/singlePosts/" + f)		

	postFile = open('posts.db', "r")
	
	htmlTop = open("./templates/top.html").readlines()
	temp=[]
	for line in htmlTop:
		line=line.replace("%TITLE%", title)
		temp.append(line)
	htmlTop=temp
	temp=[]

	htmlBottom = open("./templates/bottom.html").readlines()
	
	for line in htmlBottom:
		line=line.replace("%EMAIL%", email)
		line=line.replace("%URL%", url)
		temp.append(line)
	htmlBottom=temp

	acnt = 0
	page = 0
	lines = postFile.readlines()
	lines.reverse()
	for line in lines:
		if acnt % articlesPerPage == 0:
			f = open(blogPath + "/" + "page" + str(page) + ".html", "w") #hier hin
			f.writelines(htmlTop)
			f.write("<div id='body'>")
		split=line.split("\n")
		split=split[0].split(" : ")
		
		#split[0] ==time
		#split[1] ==title==filename	
		currArticle = htmlify(posts, split[1], False)
		
		createSinglePost(split[0], split[1], currArticle, page, htmlTop, htmlBottom)
		
		#included files for this post?
		if os.path.isdir(posts + "/" + split[1] + "_files"):
			shutil.copytree(posts + "/" + split[1] + "_files", blogPath + "/singlePosts/" + split[1] + "_files"  )
			print("copying all files from " + posts + "/" + split[1] + "_files" + " to " + blogPath + "/singlePosts/" + split[1] + "_files") 
		
		f.write("<div id = 'article'>")
		f.write("<div id = 'time'>" + "<a href='singlePosts/" + split[1] + ".html'>" +  "<time datetime='" + time.ctime(int(split[0])) + "'>" + time.ctime(int(split[0])) + "</time>" + "</a></div>")
		f.writelines(currArticle)
		
	#	f.write("<em>" + str(acnt) + "  " + str(len(lines)) + "</em>")
		f.write("</br>")
		f.write("</br>")
		f.write("</div>")
		if ((acnt % articlesPerPage) == (articlesPerPage)-1) or (acnt == len(lines)-1):
			f.write("<div id='nav'>")
			f.write("<h1><a style='font-size:90%'>" + str(page+1) + "</a><a style='font-size:70%'>/" + str(int((len(lines)-1) / articlesPerPage)+1) + "</h1></a></br>")
			if page != 0:
				f.write("<a href='page" + str(page-1) + ".html'><<</a>")
			
			if (page != int((len(lines)-1) / articlesPerPage)):
				f.write("<a href='page" + str(page+1) + ".html'>>></a>")
		
			#links schreiben
			for line in open("links.html").readlines():
				f.write(line)
			
			f.write("</div></div>") #/div body, /dev nav
			f.writelines(htmlBottom)
			f.close()
			page+=1	
	
		acnt+=1
	if os.path.isfile(blogPath + "/page0.html"):
		shutil.copy(blogPath + "/page0.html",blogPath + "/index.html")
	postFile.close()
	print("rebuilt the blog pages.")


""" #vllt irgendwann mal einbauen...
import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.prefix_chars

group.add_argument("--rebuild", "-r", help="just rebuild the blog from the database", action="store_true")
group.add_argument("--init", help="set up a new environment or update an existing", action="store_true")
group.add_argument("--add", "-a", help="add the new stuff to the blog and rebuild it", action="store_true")
group.add_argument("--remove", nargs=1, dest="name", help="remove post", action="store_true")
args = parser.parse_args()

if not any(vars(args).values()):
	parser.print_help()

if args.init:
	init()
	quit()

if not (os.path.isfile(configFilePath)):
	print("init first!")
	quit()

if args.add:
	add()
	rebuild()
	quit()

if args.rebuild:
	rebuild()
	quit()

if args.remove:
	print(args.name)


"""

usage = "Usage: " + sys.argv[0] + "\n" \
		"--init			set up a new environment or update an existing\n" \
		"--add|-a [NAME]		add the new stuff to the blog and rebuild it (all, if NAME not given)\n" \
		"--rebuild		rebuild the blog from the database\n" \
		"--remove NAME		remove post with NAME\n" \
		"--show			print the db\n"


if len(sys.argv) < 2:
	#sys.exit('Usage: %s --init	\n%s' % sys.argv[0], usage)
	print(usage)
	quit()
else:

	if sys.argv[1] == "--init":
		init()
		quit()

	if not (os.path.isfile("posts.db")):
		print("init first!")
		quit()
	
	if sys.argv[1] == "--add" or sys.argv[1] == '-a':
		if len(sys.argv) == 3:
			if addSpecific(sys.argv[2]):
				rebuild()
		else:
			add()
			rebuild()
			createFeed()
		quit()

	if sys.argv[1] == "--rebuild":
		rebuild()
		createFeed()
		quit()
	
	if sys.argv[1] == "--remove":
		if len(sys.argv) == 3:
			remove(sys.argv[2])
		else:
			print(usage)
		quit()
	if sys.argv[1] == "--show":
		show()


