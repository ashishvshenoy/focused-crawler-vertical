from urllib import urlopen
#install BeautifulSoup package
from bs4 import BeautifulSoup
import itertools
import re
import HTMLParser
import unicodedata
import pdb
try:
	#get the page here
	seedlink="http://www.whatsabyte.com/"
	seedpage_html=urlopen(seedlink).read()

	#Need to Collect a few seed pages
	soupify=BeautifulSoup(seedpage_html)

	#empty list to hold candidate pages
	candidate_links=[]
	candidate_links_dict={}
	#a double dict to hold data of the form { {link1:{word1:TF word2:TF}} {link2:{word1:TF}} }
	dd={}
	print "Opening SeedPage and extracting links from it"
	#extracting all the links from a page
	for link in soupify.find_all('a'):
		try:
			if(link.get('href').startswith("http")):
				candidate_links.append(link.get('href'))
		except:
			pass

	candidate_links=list(set(candidate_links))
	#also storing in a dict to keep track of inlink count which is calculated next
	candidate_links_dict.update({seedlink:1})
	for link in candidate_links:
		candidate_links_dict.update({link:1})
		dd[link]={}

	#get the words from textfile and build our own corpus
	wordslist=open('techwords.txt','r').read()
	words=wordslist.split()
	print "Corpus list built successfully"
	#for pages in the candidate crawled list calculate inlinks, depth 1. that is inlink count here is calculated based on initial links in candidate_links and not in the links dict

	for crawl_candidate in candidate_links:
		try:	
			print "\nStarting Crawling of " + crawl_candidate
			crawled_html=urlopen(crawl_candidate).read()
			print "Reading the contents of the page of " + crawl_candidate
			souped=BeautifulSoup(crawled_html)
			print "Normalising data - Converting Unicode data to ASCII"
			#page_text=page_text=unicodedata.normalize('NFKD',souped.get_text()).encode('ascii','ignore')
			#page_words=page_text.split()
			page_text=""
			for string in souped.stripped_strings:
				page_text=page_text+string
			regexp = "&.+?;" 
			list_of_html = re.findall(regexp, page_text) #finds all html entites in page
			for e in list_of_html:
				h = HTMLParser.HTMLParser()
				unescaped = h.unescape(e) #finds the unescaped value of the html entity
				page_text = page_text.replace(e, unescaped) #replaces html entity with unescaped value
			page_words=[]
			page_words=page_text.split()
			wdict={}
			for word in words:
				wdict[word]=0	
			frequency=0

			for word in page_words:
				word = unicodedata.normalize('NFKD', word).encode('ascii','ignore')
				if word in words:
					frequency+=1
				if word in wdict:
					temp=wdict[word]
					temp+=1
					wdict[word]=temp
			print "Printing Frequency count to file"
			for i in wdict:
				if wdict[i]>0:
					dd[crawl_candidate][i]=wdict[i]
					#with open("Words/"+i+".txt","w") as outfile:
						#outfile.write(crawl_candidate + " " + repr(wdict[i]) + "\n")
					#	outfile.write('')
			print "Finishd Printing, closing the file"	
			crawl_temp=[]
			#read the links in each individual link now.
			#pdb.set_trace()
			print "Term Frequency is " + repr(frequency)
			if(frequency>0):
				for link in souped.find_all('a'):
					try:
						if(link.get('href').startswith("http")):
							crawl_temp.append(link.get('href'))
					except:
						pass
				print "Crawling at depth 2 to get inlink count"
				crawl_temp=list(set(crawl_temp))				
				  #Now update the links in the dict be checking
		
				for link in crawl_temp:
					if link in candidate_links_dict.keys():
						#get the inlink count first and then increment it
						count=candidate_links_dict[link]
						count+=1
						candidate_links_dict[link]=count
					else:
						#Else update that is add the link to the dict
						candidate_links_dict.update({link:1})
			else:
				print crawl_candidate+"Does not belong to domain"
		except:	
			pass

	print "\n" + repr(len(candidate_links_dict))
	for key in dd.keys():
		tempd=dd[key]
		for i in tempd.keys():
			with open("Words/"+i+".txt","a") as outfile:
				#Printing to file: <link> <TF> <inlink_count>
				outfile.write(key+" " + repr(tempd[i])+ " " + repr(candidate_links_dict[key]) + "\n")

except:
	pass

#candidate_links_dict now contains links with depth 2 and also the inlink count.
