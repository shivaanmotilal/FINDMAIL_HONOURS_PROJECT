#Shivaan Motilal
#Programme to generate search and browse indices

#Porting Code from python 2 to 3
from __future__ import print_function, division
from __future__ import unicode_literals
from __future__ import absolute_import

import xml.etree.cElementTree as ET
import string
import os
import json
from collections import Counter, defaultdict, Mapping
import re
import errno
import time
from multiprocessing import Process
import shutil
from sys import platform
import sys
#Check that version of python >= 2.7
major, minor, micro, releaselevel, serial = sys.version_info
if (major,minor) <= (2,6):
    # provide advice on getting version 2.7 or higher.
    print("You need need Python version > 2.7. Download from here: https://www.python.org/")
    sys.exit(2)

#Suffers from IO bottleneck as writing to each index file more than once, main 2 is faster method
def main(path):
    stopwords = { #intialized map
      'html' : 1,
      'search' : 1,
      'and' : 1,
      'books' : 1,
      'the' : 1,
      'of' : 1,
      's' : 1,
      'a' : 1,
      'or' : 1,
      'by' : 1,
      'to' : 1,
      'file' : 1,
      'index' : 1,
      'is' : 1,
      'title' : 1,
      'it' : 1,
      'subject' : 1,
      'to' : 1,
      'from' : 1,
      'time' : 1,
      'date': 1,
      'datetime' :1,
      'i':1
    }
    doc_id=1
    msgSubject=""
    msgDate=""
    msgFrom=""      
    midpath=""     
    for dirname, subdirs, files in os.walk(path):
        #NB: Does not process files in order appearing in original folder
        for name in files:
            file_path = os.path.join(dirname, name)   
            final_tokens=[]                      
            """Extract content from documents"""
            tree = ET.parse(file_path)
            doc_id= name[:-4]

            alldir= os.path.normpath(file_path).split(os.path.sep)
            alldir= alldir[2:-1]
            if alldir:
                midpath=os.path.join(*alldir)
            else:
                midpath=""
            root = tree.getroot()
            for child in root:
                if child.tag == 'doc_id': 
                    pass
                else:
                    text = child.text 
                    if not text:
                        """No text in field.Can't add to token."""
                    else:
                        """Tokenizing and stemming""" 
                        text= re.sub('[^A-Za-z]+', ' ', text)#Remove punctuation
                        text= text.strip(string.punctuation)
                        tokens= text.split(" ")
                        tokens = [i.strip(string.punctuation) for i in tokens if i not in string.punctuation] #filters out punctuation as keywords
                        tokens = [i for i in tokens if (len(i)<=45)]
                        tokens = [i.lower() for i in tokens if i.lower() not in stopwords] #filters out punctuation as keywords
                        counts = Counter(tokens)
                        dictCounts=dict(counts)
                        for key1 in dictCounts:
                            filename= os.path.join("index",str(key1)+".xml")
                            if not os.path.exists(os.path.dirname(filename)):
                                try:
                                    os.makedirs(os.path.dirname(filename))
                                    root1 = ET.Element("email")
                                    if root.find('subject').text:
                                        msgSubject=root.find('subject').text
                                    else:
                                        msgSubject="No Subject"
                                    if root.find('from').text:
                                        msgFrom=root.find('from').text
                                    else:
                                        msgFrom="No Sender"
                                    if root.find('date').text:
                                        msgDate= root.find('date').text
                                    else:
                                        msgDate="No Date"
                                    ET.SubElement(root1, "tf",id= str(doc_id),file=os.path.join("FINDMAIL/HTML_files/",midpath,str(doc_id)+".txt"),sender=msgFrom, subject= msgSubject, date=msgDate ).text = str(dictCounts[key1])
                                    tree.write(filename)
                                except OSError as exc:
                                    if exc.errno != errno.EEXIST:
                                        raise
                                    print(exc)
                            else:
                                if not os.path.isfile(filename) :
                                    root1 = ET.Element("email")
                                    if root.find('subject').text:
                                        msgSubject=root.find('subject').text
                                    else:
                                        msgSubject="No Subject"
                                    if root.find('from').text:
                                        msgFrom=root.find('from').text
                                    else:
                                        msgFrom="No Sender"
                                    if root.find('date').text:
                                        msgDate= root.find('date').text
                                    else:
                                        msgDate="No Date"
                                    ET.SubElement(root1, "tf",id= str(doc_id),file=os.path.join("FINDMAIL/HTML_files/",midpath,str(doc_id)+".txt"),sender=msgFrom, subject= msgSubject, date=msgDate ).text = str(dictCounts[key1])
                                    tree = ET.ElementTree(root1)
                                    tree.write(filename)
                                else: 
                                    text=""
                                    with open(filename, 'r') as myfile:
                                        text=myfile.read()

                                    root1= ET.fromstring(text)
                                    found_doc= None
                                    for tf in root1.iter('tf'):
                                        if int(tf.attrib.get("id"))==doc_id:
                                            newWeight= int(tf.text)+dictCounts[key1]
                                            tf.text= str(newWeight)
                                            found_doc=True
                                            break
                                    if(found_doc):
                                        pass
                                    else:
                                        if root.find('subject').text:
                                            msgSubject=root.find('subject').text
                                        else:
                                            msgSubject="No Subject"
                                        if root.find('from').text:
                                            msgFrom=root.find('from').text
                                        else:
                                            msgFrom="No Sender"
                                        if root.find('date').text:
                                            msgDate= root.find('date').text
                                        else:
                                            msgDate="No Date"
                                        ET.SubElement(root1, "tf",id= str(doc_id),file=os.path.join("FINDMAIL/HTML_files/",midpath,str(doc_id)+".txt"),sender=msgFrom, subject= msgSubject, date=msgDate ).text = str(dictCounts[key1])
                                    tree = ET.ElementTree(root1)
                                    tree.write(filename)
                                    myfile.close()                                          

#Does Write once to all files at the end
def main2(path):
    stopwords = { #intialized map
      'html' : 1,
      'search' : 1,
      'and' : 1,
      'books' : 1,
      'the' : 1,
      'of' : 1,
      's' : 1,
      'a' : 1,
      'or' : 1,
      'by' : 1,
      'to' : 1,
      'file' : 1,
      'index' : 1,
      'is' : 1,
      'title' : 1,
      'it' : 1,
      'subject' : 1,
      'to' : 1,
      'from' : 1,
      'time' : 1,
      'date': 1,
      'datetime' :1,
      'i':1
    }
    doc_id=1
    msgSubject=""
    msgDate=""
    msgFrom=""      
    midpath=""    
    nameDict={} 
    subDict={}
    for dirname, subdirs, files in os.walk(path):
        #NB: Does not process files in order appearing in original folder
        for name in files:
            file_path = os.path.join(dirname, name)   
            final_tokens=[]                      
            """Extract content from documents"""
            tree = ET.parse(file_path)
            doc_id= name[:-4]

            alldir= os.path.normpath(file_path).split(os.path.sep)
            alldir= alldir[2:-1]
            if alldir:
                midpath=os.path.join(*alldir)
            else:
                midpath=""
            root = tree.getroot()
            for child in root:
                if child.tag == 'doc_id': 
                    pass
                else:
                    text = child.text 
                    if not text:
                        """No text in field.Can't add to token."""
                    else:
                        """Tokenizing and stemming""" 
                        text= re.sub('[^A-Za-z]+', ' ', text)#Remove punctuation
                        text= text.strip(string.punctuation)
                        tokens= text.split(" ")
                        tokens = [i.strip(string.punctuation) for i in tokens if i not in string.punctuation] #filters out punctuation as keywords
                        tokens = [i for i in tokens if (len(i)<=45)]
                        tokens = [i.lower() for i in tokens if i.lower() not in stopwords] #filters out punctuation as keywords
                        counts = Counter(tokens)
                        dictCounts=dict(counts)
                        for key1 in dictCounts:
                            #if word already in dict, as a file
                            if key1 in nameDict: 
                                #if word in the same doc as another file parsed
                                if str(doc_id) in nameDict[key1]:
                                    newVal= int(nameDict[key1][str(doc_id)]['count'])+dictCounts[key1]
                                    nameDict[key1][str(doc_id)]['count']= str(newVal)
                                else:
                                    #same word in different doc , add new field to dict
                                    if root.find('subject').text:
                                        msgSubject=root.find('subject').text
                                    else:
                                        msgSubject="No Subject"
                                    if root.find('from').text:
                                        msgFrom=root.find('from').text
                                    else:
                                        msgFrom="No Sender"
                                    if root.find('date').text:
                                        msgDate= root.find('date').text
                                    else:
                                        msgDate="No Date"
                                    subDict=nameDict[key1]
                                    subDict[str(doc_id)]= {"file":os.path.join("FINDMAIL/HTML_files/",midpath,str(doc_id)+".txt"), "sender":msgFrom, "subject":msgSubject,"date":msgDate , "count":str(dictCounts[key1])}
                                    nameDict[key1]=subDict
                            else:
                                #no word or docs exist
                                if root.find('subject').text:
                                    msgSubject=root.find('subject').text
                                else:
                                    msgSubject="No Subject"
                                if root.find('from').text:
                                    msgFrom=root.find('from').text
                                else:
                                    msgFrom="No Sender"
                                if root.find('date').text:
                                    msgDate= root.find('date').text
                                else:
                                    msgDate="No Date"
                                subDict={}
                                subDict[str(doc_id)]= {"file":os.path.join("FINDMAIL/HTML_files/",midpath,str(doc_id)+".txt"), "sender":msgFrom, "subject":msgSubject,"date":msgDate , "count":str(dictCounts[key1])}
                                nameDict[key1]=subDict  
    count=0
    for key in nameDict:
        filename= os.path.join("index",str(key)+".xml")
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
                root1 = ET.Element("email")
                for val in nameDict[key]: #iterating through doc_IDs
                    ET.SubElement(root1, "tf",id= str(val),file=nameDict[key][val]['file'],sender=nameDict[key][val]['sender'], subject= nameDict[key][val]['subject'], date=nameDict[key][val]['date'] ).text = nameDict[key][val]['count']
                tree = ET.ElementTree(root1)
                tree.write(filename)
                count=count+1
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                print(exc)
        else:
            root1 = ET.Element("email")
            for val in nameDict[key]: #iterating through doc_IDs
                ET.SubElement(root1, "tf",id= str(val),file=nameDict[key][val]['file'],sender=nameDict[key][val]['sender'], subject= nameDict[key][val]['subject'], date=nameDict[key][val]['date'] ).text = nameDict[key][val]['count']
            tree = ET.ElementTree(root1)
            tree.write(filename)
            count=count+1

    print(str(count)+" index files")


if __name__ == '__main__':
    start_time = time.time()
    if os.path.exists(os.path.join("index")):
        shutil.rmtree("index")
    """Run indexing in parallel """
    if platform == "linux" or platform == "linux2":
        # linux
        p = Process(target=main2, args=(os.path.join("FINDMAIL/","XML_files"),))
        p.start()
        p.join()
    elif platform == "darwin":
        # OS X
        p = Process(target=main2, args=(os.path.join("FINDMAIL/","XML_files"),))
        p.start()
        p.join()
    elif platform == "win32": #Windows can't compile the multiprocessing module written in c,  infinite recursion would occur
        # Windows..
        main2(os.path.join("FINDMAIL/","XML_files"))
    
    print("--- %s seconds ---" % (time.time() - start_time))#Measure execution time of program