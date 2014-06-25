#!/usr/bin/python

#function to remove duplicates in folder by genrating and comparing their hash values
#has option to remove file automatically or move them to a separate place.

#hash type: MD5/SHA1
global hashfunc
hashfunc='MD5'

#add locations in main() where duplicacy may occur, (absolute/paths/only/with/trailing/)
global dir_to_check
dir_to_check=[]
#all duplicates will be moved into dir_to_move ignoring their relative filestructure.
global dir_to_move
dir_to_move=[]

#logs are saved in dir_to_move/
#	checklogs-> original files and their duplicates
#	movelogs-> src and dsts of moved files (only when move_files=True) or removed files (only when remove_files=True)

import sys, hashlib, os, shutil, time
from collections import Counter

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
			#if file
				if os.path.isfile(filepath+str(item)):
					if (filetype==None) or (os.path.splitext(item)[1] in filetype): # if filter is provided, append only files that match the extensions
						files.append(filepath+str(item))
			#if dir	
				if os.path.isdir(filepath+str(item)):
					dirs.append(filepath+str(item)+'/')
					rectree(filepath+str(item)+'/')
			#if symlink
				if os.path.islink(filepath+str(item)):
					links.append(filepath+str(item))
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
def titlecheck(rootdirpath, filetype=None, exclude=[]): #extract titles, convert to counter, check duplicates, print ones which occur >1 with their path
	titles=[]
	duptitles=[]
	oplist=[]
	filepathlist=scour(rootdirpath, filetype=filetype, exclude=exclude)[0]
	for path in filepathlist:
		titles.append(os.path.basename(path))
	titlecount=Counter(titles)
	for path in filepathlist:
		title=os.path.basename(path)
		if titlecount[title] > 1: #select only titles that have more than 1 occurance
			if title not in duptitles:
				print "Original:", title, path
				duptitles.append(title)
			else:
				print "Duplicate:", title, path
				oplist.append(path)
	duptitles.sort()
	print "\n\nTotal Files:", len(filepathlist)
	print "Total unique filenames:", len(titlecount)
	print "Total filenames that have duplicates:", len(duptitles), "\n\n"
	print oplist
	return oplist #list of files that have duplicate names

#MD5 based hasher	
def md5sum(filepath): #hash func
	md5 = hashlib.md5()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(128*md5.block_size), b''): 
			md5.update(chunk)
	return md5.hexdigest()

#sha1 based hasher
def sha1sum(filepath): #hash func
	sha1 = hashlib.sha1()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(128*sha1.block_size), b''): 
			sha1.update(chunk)
	return sha1.hexdigest()

#logs
def logtofile(string, filepath=""):
	file=open(filepath, 'a')
	file.write(string)
	file.close()
	print string
	return

#gets filelish, checks hashes, returns duplicate files list
def hashcheck(rootdirpath, filetype=None, exclude=[], logging=False, hashfunc=hashfunc): #gen filelist, list hashes, detect duplicates by hashes, return duplicate files
	i=1 #counter  for hash
	#j=1 #counter for checking duplicates

	hashes=[] #holds all file hashes for easy checking
	hashlist=[] #holds all hashes, filenames and paths
	duphashes=[] #holds all file-hashes which have duplicates
	oplist=[] #holds all file-hashes which are the duplicates
	
	#generating list of filepaths
	filepathlist=scour(rootdirpath, filetype=filetype, exclude=exclude)[0]
	print "\nTotal Files:", len(filepathlist)
	
	for path in filepathlist: #hashing
		i+=1
		print "Hashing done:", i*100/len(filepathlist)
		title=os.path.basename(path)
		if hashfunc=='MD5': filehash=md5sum(path)
		elif hashfunc=='SHA1': filehash=sha1sum(path)
		else: 
			print "Please set hash function."
			return
		hashes.append(filehash)
		hashlist.append([filehash, title, path])
		#clearscreen
		os.system('cls' if os.name == 'nt' else 'clear')
	print "\nFinished hashing..."

	hashcount=Counter(hashes) #the files which have duplicates will have a >1 frequency in counter
	#print hashcount
	hashlist.sort()

	#checking duplicates
	print "Checking for duplicates..."
	for fhash in hashcount: 
		#j+=1
		#print "Checking done:", j*100/len(hashcount)
		if hashcount[fhash]>1:
			for item in hashlist:
				filehash, title, path=item
				#if file has no duplicates yet, must be the original file, hash into duphashes[]
				if fhash==filehash and filehash not in duphashes:
					print "\nOriginal:", title, "("+filehash+")"
					print "Copies:", hashcount[filehash]-1,"\n", path
					if logging: logtofile("orig:"+filehash+"--"+path+"\n", filepath=dir_to_move+'checklog')
					duphashes.append(filehash)
				
				#if hash already inserted, must be duplicate file, path into oplist[]
				elif fhash==filehash and filehash in duphashes:
					print "\nDuplicate:", title, "("+filehash+")","\n", path
					if logging: logtofile("dupl:"+filehash+"--"+path+"\n", filepath=dir_to_move+'checklog')
					oplist.append(path)
	#stats
	print "\n\nStats:\nTotal Files:", len(filepathlist)
	print "Total unique files:", len(hashcount)
	print "Total files that have duplicates:", len(duphashes)
	print "Total files that are duplicates:", len(oplist), "\n\n"
	#print oplist
	return oplist

#this function only handles what to do with the duplicates, as the checking is done in hashcheck()
def main(rootdirpath, filetype=None, exclude=[], move_files=True, move_dir='', remove_files=False, logging=False):
	#get files to move/remove from hashcheck
	filelist=hashcheck(rootdirpath, filetype=filetype, exclude=exclude, logging=logging) #returns all duplicate files
	if not filelist:
		print "Yay! No duplicate items. :)"
		return
	if move_files and os.path.isdir(move_dir):
		print "Moving duplicates to:", move_dir
		for item in filelist: #moving files
			print "Moving:", os.path.basename(item)
			if logging: logtofile("src:"+item+"--dst:"+move_dir+os.path.basename(item)+"\n", filepath=dir_to_move+'movelog') #separated by --
			try:
				shutil.move(item, move_dir)
			except: #file exists
				shutil.move(item, os.path.join(move_dir, os.path.basename(item)+time.strftime("%Y%m%d%H%M%S"))) #adds timestamp #doesn't replace unless specified			
	elif remove_files:
		for item in filelist: #USE WITH CAUTION
			print "Removing:", os.path.basename(item)
			if logging: logtofile("removing:"+item+"\n", filepath=dir_to_move+'movelog')
			os.remove(item)

#RUN
if __name__=="__main__":

	#check paths can be both a single path, or a number of paths in a list (handled in scour())
        # but dir_to_move must be a single dir
	dir_to_check='/absolute/path(s)/to/dir/which/is/to/be/checked/'
	dir_to_move="/absolute/path/to/dir/where/duplicate/files/will/be/moved/"
	
	#main funcion
	main(dir_to_check, move_files=True, move_dir=dir_to_move, exclude=[], logging=True)
