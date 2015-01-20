# Gwyn Price 
import os
import guessit
import httplib
import urllib2
import json
from pprint import pprint
import re
import time

start_time = time.time()

# files and directories
movieDir='/opt/movies'
resultFile='/opt/code/movies/movies.json'
errorFile='/opt/code/movies/notworking.txt'
delimeter=' '

# initialise variables
errorCount=0
successCount=0
movies = {}

# function to pull down json from the omdbapi site
# this contains the proper movie title, year, ratings etc
# use try/except as some movies may be mssing one of the fields

def getDirectoryDetails(newroot):
	# remove unecessary puntuation from filenames
	newroot = re.sub('[.,;-]', ' ', newroot)
	# run guessit parser to try and get the movie title and the year
	guess = guessit.guess_movie_info(newroot, info=['filename'])
	title = guess.get('title')
	year = guess.get('year')
	# a lot of movies have 'the' appeneded instead of at the start of the string title
	# e.g. Fifth Estate The
	# strip 'the' off the back and add to the fron so we get:
	# e.g. The Fifth Estate
	suffix = ['the','The']
        for s in suffix:
	    if str(title).endswith(s):
		title = title[:-3]
		title = 'The ' + title
	return title, year

def getDetails(url):
	opener = urllib2.build_opener()
	#try:
	#print url
	f = opener.open(url)
	json_data = json.loads(f.read())
	#pprint(json_data)
	title=''
	year=''
	actors=''
	rating=''

	try:
		title = json_data['Title']
	except:
		pass
	try:
		year = json_data['Year']
	except:
		pass
	try:
		actors = json_data['Actors']
	except:
		pass
	try:
		rating = json_data['imdbRating']
	except:
		pass

	return title,year,actors,rating

# change to the dir that has the movies in it
# and open the error file
os.chdir(movieDir)
ef = open(errorFile, 'w')
of = open(resultFile, 'w')
of.write("{\n \"data\": [ \n")
# walk through the movie dir grabbing all the sub directory names

for root in os.walk('.'):
	# remove ./ from start of filenames
	newroot=root[0][2:]
	
	# try and figure out the title and year from the directory name
	# this is what is needed to search imdb
	title,year = getDirectoryDetails(newroot)

	url=''
	# if we got a title and year from the directory then name build the url string for omdbapi
	if title:
		title = title.replace(" ","+")
		if year:
			url = "http://www.omdbapi.com/?t=" + title + "&y=" + str(year) + "&plot=short&r=json"
		else:
			url = "http://www.omdbapi.com/?t=" + title + "&plot=short&r=json"
	# if theres a url search for it
	if url:
		# call the movie details funstion
		title,year,actors,rating=getDetails(url)
		# add the details to the movies dict
		if title:
		#movies['data'] = {"title":title,
			#							      "year":year,
			#                  "actors":actors,
			#                  "rating": rating}
		    of.write(delimeter + '\n      [\n')
		    of.write('\t\t\"' + title + '\",\n')
		    of.write('\t\t\"' + year + '\",\n')
		    of.write('\t\t\"' + actors + '\",\n')
		    of.write('\t\t\"' + rating + '\"\n')
		    of.write("      ]")
		    successCount += 1
                    delimeter=','
                if not title:
        	#if we didnt get anything from omdbapi add to the 'broken' file
        	    ef.write(url + "\n") 
        	    errorCount += 1


of.write("\t ] \n }\n")

# close the error file
ef.close()
of.close()


pprint(movies)

# write the results to the json file
#j = json.dumps(movies, indent=4)
#print f,j
#print >> f, j

print("Time to process --- %s seconds ---" % (time.time() - start_time))
print 'Success: ',successCount
print 'Errors: ',errorCount
