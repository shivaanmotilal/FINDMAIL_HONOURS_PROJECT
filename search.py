"""To use nltk need to install anaconda(bundles python etc) or pip and then pypy """


import xml.etree.cElementTree as ET
import string
"""-Need to install NLTK first using Numpy and pip: 
https://davejingtian.org/2012/10/08/nltk-install-nltk-for-python2-7-on-64-bit-win-7/ """
import os
import json
from collections import Counter, defaultdict, Mapping
import re
import errno
import time
from multiprocessing import Process

"""-Deletes all files or directories in directory of path passed in"""
def clearFolder(folder):
    if not os.path.exists(folder):
        pass #No directory so nothing to clear
    else:
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                ##Uncomment to clear all directories in path specified
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)  

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
    doc_list = {}
    master = {} 
    msgSubject=""
    msgDate=""
    msgFrom=""           
    for dirname, subdirs, files in os.walk(path):
        #NB: Does not process files in order appearing in original folder
        for name in files:
            file_path = os.path.join(dirname, name)   
            final_tokens=[]                      
            """Extract content from documents"""
            tree = ET.parse(file_path)
            root = tree.getroot()
            for child in root:
                if child.tag == 'doc_id': 
                    # print("got in")
                    pass
                else:
                    text = child.text 
                    #print text
                    if not text:
                        """No text in field.Can't add to token."""
                    else:
                        """Tokenizing and stemming""" 
                        # text= text.strip(string.punctuation)
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
                            # print(filename)
                            if not os.path.exists(os.path.dirname(filename)):
                                try:
                                    os.makedirs(os.path.dirname(filename))
                                    # print("made directory")
                                    root1 = ET.Element("email")
                                    if root.find('subject'):
                                        msgSubject=root.find('subject')
                                    if root.find('from'):
                                        msgFrom=root.find('from')
                                    if root.find('date'):
                                        msgDate= root.find('date')
                                    ET.SubElement(root1, "tf",id= str(doc_id),file="FINDMAIL/HTML_files/"+str(doc_id)+".txt",sender=msgFrom, subject= msgSubject, date=msgDate ).text = str(dictCounts[key1])
                                    # print(root.find('from').text)
                                    # if root[0]:
                                    #     msgFrom= re.sub('[^A-Za-z0-9]+', ' ',root[0])
                                    #     ET.SubElement(root1, "tf",doc_id= str(doc_id),file=file_path[:-4]+".html",sender=msgFrom).text = str(dictCounts[key1])
                                    # else:
                                    #     ET.SubElement(root1, "tf",doc_id= str(doc_id),file=file_path[:-4]+".html",sender="").text = str(dictCounts[key1])
                                    tree = ET.ElementTree(root1)
                                    tree.write(filename)
                                except OSError as exc:
                                    if exc.errno != errno.EEXIST:
                                        raise
                                    print exc 
                            else:
                                # my_file = Path(filename)
                                if not os.path.isfile(filename) :
                                    #First time writing to file
                                    # print("Got in")
                                    root1 = ET.Element("email")
                                    if root.find('subject'):
                                        msgSubject=root.find('subject')
                                    if root.find('from'):
                                        msgFrom=root.find('from')
                                    if root.find('date'):
                                        msgDate= root.find('date')
                                    ET.SubElement(root1, "tf",id= str(doc_id),file="FINDMAIL/HTML_files/"+str(doc_id)+".txt",sender=msgFrom, subject= msgSubject, date=msgDate ).text = str(dictCounts[key1])
                                    # print(root.find('from').text)
                                    # if root[0]:
                                    #     msgFrom= re.sub('[^A-Za-z0-9]+', ' ',root[0])
                                    #     ET.SubElement(root1, "tf",doc_id= str(doc_id),file=file_path[:-4]+".html",sender=msgFrom).text = str(dictCounts[key1])
                                    # else:
                                    #     ET.SubElement(root1, "tf",doc_id= str(doc_id),file=file_path[:-4]+".html",sender="").text = str(dictCounts[key1])
                                    tree = ET.ElementTree(root1)
                                    tree.write(filename)
                                else:  

                                    # print(filename)
                                    text=""
                                    with open(filename, 'r') as myfile:
                                        text=myfile.read()
                                    # print(text)
                                    root1= ET.fromstring(text)
                                    found_doc= None
                                    for tf in root1.iter('tf'):
                                        if int(tf.attrib.get("id"))==doc_id:
                                            newWeight= int(tf.text)+dictCounts[key1]
                                            # print(tf.text)
                                            tf.text= str(newWeight)
                                            # print("newWeight"+" "+str(newWeight))
                                            found_doc=True
                                    #if document already exists then write to it
                                    if(found_doc):
                                        pass
                                    else:
                                        if root.find('subject'):
                                            msgSubject=root.find('subject')
                                        if root.find('from'):
                                            msgFrom=root.find('from')
                                        if root.find('date'):
                                            msgDate= root.find('date')
                                        ET.SubElement(root1, "tf",id= str(doc_id),file="FINDMAIL/HTML_files/"+str(doc_id)+".txt",sender=msgFrom, subject= msgSubject, date=msgDate ).text = str(dictCounts[key1])
                                        # ET.SubElement(root1, "tf",id= str(doc_id),file="FINDMAIL/HTML_files/"+str(doc_id)+".txt",sender=root.find('from').text, subject= root.find('subject').text, date=root.find('date').text ).text = str(dictCounts[key1])
                                    
                                    tree = ET.ElementTree(root1)
                                    # print(ET.tostring(root1, encoding='utf8', method='xml'))
                                    # print(ET.tostring(root1, "utf-8"))
                                    tree.write(filename)
            doc_id=doc_id+1
    # sortedmaster= sorted(master.keys(), key=lambda x:x.lower())
    # for key in sortedmaster:
    #     print(key)                                          
                                                
if __name__ == '__main__':
    #main()
    start_time = time.time()
    if os.path.exists(os.path.join("index")):
        clearFolder(os.path.join("index"))
    """Run indexing in parallel """
    p = Process(target=main, args=(os.path.join("FINDMAIL/","XML_files"),))
    p.start()
    p.join()
    print("--- %s seconds ---" % (time.time() - start_time))#Measure execution time of program