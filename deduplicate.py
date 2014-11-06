#!/usr/bin/python

from __future__ import print_function
import sys, hashlib, os, shutil, time
from collections import Counter


#function to remove duplicates in folder by genrating and comparing their hash values
#has option to remove file automatically or move them to a separate place.

#add locations here where duplicacy may occur, (absolute/paths/only/with/trailing/)
global dir_to_check
#all duplicates will be moved into dir_to_move ignoring their relative filestructure.
global dir_to_move
#dir_to_move="/media/xt1/BackThisUp/devices/s2/duplicates/"

#function to get list of files, recursive so more deph==heavier
def scour(rootdirpath, filetype=None, exclude=[], follow_links=False):
	#scans and returns sorted list[files, folders, links], given root directorypath...ends in /
	#pass list of filetypes as filter (eg ['.txt', '.zip'] or just '.txt' if single element) #MIND THE DOT
	#excludes if item in exclude[list] (eg ['.txt', 'directoryname', 'symlinkname'])
	#set follows_links=True to include symlink resolve, only if pointed file or dir not already in list #DOES NOT FOLLOW LINKS
	files=[] #file list
	dirs=[]  #dirs list
	links=[] #links list
	def rectree(filepath): #recursive tree to scan files/folders
		#print filepath
		filelist=os.listdir(filepath)
		for item in filelist:
			#print item
			if (os.path.splitext(item)[1] not in exclude) & (str(item) not in exclude): #if extension or dirname or linkname not in excludelist
			#if file, and (if specified) file extension is in filetype
				if os.path.isfile(os.path.join(filepath, item)):
					if (filetype==None) or (os.path.splitext(item)[1] in filetype): # if filter is provided, append only files that match the extensions
						files.append(os.path.join(filepath, item))
			#if dir	
				if os.path.isdir(os.path.join(filepath, item)):
					dirs.append(os.path.join(filepath, item))
					rectree(os.path.join(filepath, item))
			#if symlink
				if os.path.islink(os.path.join(filepath, item)):
					links.append(os.path.join(filepath, item))
					#if follow_links==True: #DOES NOT FOLLOW LINKS
					#	realpath=os.path.realpath(filepath+str(item)) #resolve realpath
					#	if rootdirpath not in realpath: #if realpath not in root directory (avoids loops) include realpath in scouring
					#		filelist.append(realpath)
	#run function, then sort and serve
	if type(rootdirpath)==str: #single path
		if os.path.isdir(rootdirpath): #if directory exists
			rectree(rootdirpath)
	elif type(rootdirpath)==list or type(rootdirpath)==tuple: #many paths in list/tuple
		for item in rootdirpath:
			rectree(item)
	#if not os.path.isdir(rootdirpath):
	#	return
	#rectree(rootdirpath)
	files.sort() #turn off sorting if too heavy
	dirs.sort()
	links.sort()
	return files, dirs, links

#deprecated
#def titlecheck(rootdirpath, filetype=None, exclude=[]): #extract titles, convert to counter, check duplicates, print ones which occur >1 with their path
#	titles=[]
#	duptitles=[]
#	oplist=[]
#	filepathlist=scour(rootdirpath, filetype=filetype, exclude=exclude)[0]
#	for path in filepathlist:
#		titles.append(os.path.basename(path))
#	titlecount=Counter(titles)
#	for path in filepathlist:
#		title=os.path.basename(path)
#		if titlecount[title] > 1: #select only titles that have more than 1 occurance
#			if title not in duptitles:
#				print "Original:", title, path
#				duptitles.append(title)
#			else:
#				print "Duplicate:", title, path
#				oplist.append(path)
#	duptitles.sort()
#	print "\n\nTotal Files:", len(filepathlist)
#	print "Total unique filenames:", len(titlecount)
#	print "Total filenames that have duplicates:", len(duptitles), "\n\n"
#	print oplist
#	return oplist #list of files that have duplicate names

#deprecated	
#def md5sum(filepath): #hash func
#	md5 = hashlib.md5()
#	with open(filepath,'rb') as f: 
#		for chunk in iter(lambda: f.read(128*md5.block_size), b''): 
#			md5.update(chunk)
#	return md5.hexdigest()

def sha1sum(filepath): #hash func
	sha1 = hashlib.sha1()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(128*sha1.block_size), b''): 
			sha1.update(chunk)
	return sha1.hexdigest()

def hashcheck(rootdirpath, filetype=None, exclude=[]): #gen filelist, list hashes, detect duplicates by hashes, return duplicate files
	i=1
	#j=1
	hashes=[]
	hashlist=[]
	duphashes=[]
	oplist=[]
	filepathlist=scour(rootdirpath, filetype=filetype, exclude=exclude)[0]
	print("\nTotal Files:", len(filepathlist))
	for path in filepathlist: #hashing
		print("Hashing done:", i*100/len(filepathlist))
		title=os.path.basename(path)
		filehash=sha1sum(path)
		hashes.append(filehash)
		hashlist.append([filehash, title, path])
		i+=1
	print("\nFinished hashing...")
	hashcount=Counter(hashes)
	#print hashcount
	hashlist.sort()
	print("Checking for duplicates...")
	for fhash in hashcount: #getting duplicates
		#j+=1
		#print "Checking done:", j*100/len(hashcount)
		if hashcount[fhash]>1:
			for item in hashlist:
				filehash, title, path=item
				if fhash==filehash and filehash not in duphashes:
					print("\nOriginal:", title, "("+filehash+")")
					print("Copies:", hashcount[filehash]-1)
					print(path)
					duphashes.append(filehash)
				elif fhash==filehash and filehash in duphashes:
					print("\nDuplicate:", title, "("+filehash+")","\n", path)
					oplist.append(path)
		
	print("\n\nStats:\nTotal Files:", len(filepathlist))
	print("Total unique files:", len(hashcount))
	print("Total files that have duplicates:", len(duphashes))
	print("Total files that are duplicates:", len(oplist), "\n\n")
	#print oplist
	return oplist

#moving files
#print hashcheck("/media/xt1/BackThisUp/devices/s2/duplicates/", filetype=['.jpg', '.jpeg', '.png', '.tif', '.webm'])
#	shutil.move(item, "/media/xt1/BackThisUp/devices/s2/duplicates/"+os.path.basename(item))

def main(rootdirpath, filetype=None, exclude=[], move_files=True, move_dir='', remove_files=False):
	#get files to move/remove from hashcheck
	#filelist=[]
	#for item in rootdirpath:
	filelist=hashcheck(rootdirpath, filetype=filetype, exclude=exclude) #returns all duplicate files
	if not filelist:
		print( "Yay! No duplicate items. :)")
		return
	#else start moving
	if move_files and os.path.isdir(move_dir):
		print("Moving duplicates to:", move_dir)
		for item in filelist: #moving files
			print("Moving:", os.path.basename(item))
			#make destination filepath= common
			commonpath=os.path.commonprefix([item, move_dir])
			destdir=os.path.join(move_dir, item.replace(commonpath, '').replace(os.path.basename(item), ''))
			#print os.path.join(move_dir, destdir)
			#print destdir
			if not os.path.exists(destdir):
				try: 
					os.makedirs(destdir)
				except OSError:
					if not os.path.isdir(destdir):
						raise
			try:
				shutil.move(item, destdir)
			except: #file exists
				shutil.move(item, os.path.join(destdir, os.path.basename(item)+time.strftime("%Y%m%d%H%M%S"))) #doesn't replace unless specified			
	elif remove_files:
		for item in filelist: #USE WITH CAUTION
			print("Removing:", os.path.basename(item))
			os.remove(item)

if __name__=="__main__":
	if len(sys.argv)>=2:
		dir_to_check=os.path.abspath(sys.argv[1])
		dir_to_move=os.path.abspath(sys.argv[2]) if len(sys.argv)>=3  and os.path.exists(os.path.abspath(sys.argv[2])) else os.path.join(dir_to_check, "__duplicates__")
		
		#create duplicates dir if not exists
		if not os.path.exists(dir_to_move):
			try: 
  				os.makedirs(dir_to_move)
			except OSError:
				if not os.path.isdir(dir_to_move):
					raise
		print("Cheking    --> ", dir_to_check)
		print("Duplicates --> ", dir_to_move)
		#commonpath=os.path.commonprefix([dir_to_check, dir_to_move])
		#relpaths=os.path.relpath(dir_to_check, dir_to_move)
		#print commonpath, relpaths
		#print dir_to_move+dir_to_check.replace(commonpath, '/')
		main(dir_to_check, move_files=True, move_dir=dir_to_move, exclude=['__duplicates__'])

	#show usage
	else:
		print("Usage:\npython", sys.argv[0], "/path/to/check", "/path/where/duplicates/go")
	#dir_to_check='/home/arch/scrap/pix/'
	#dir_to_check=sys.argv[0]
	#dir_to_move="/home/arch/scrap/pix/duplicates/"
	#main(dir_to_check, move_files=True, move_dir=dir_to_move, exclude=['duplicates'])