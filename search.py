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
                    print("got in")
                else:
                    text = child.text 
                    #print text
                    if not text:
                        """No text in field.Can't add to token."""
                    else:
                        """Tokenizing and stemming""" 
                        # text= text.strip(string.punctuation)
                        text= re.sub('[^A-Za-z0-9]+', ' ', text)#Remove punctuation
                        text= text.strip(string.punctuation)
                        tokens= text.split(" ")
                        tokens = [i.strip(string.punctuation) for i in tokens if i not in string.punctuation] #filters out punctuation as keywords
                    
                        tokens = [i.lower() for i in tokens if i.lower() not in stopwords] #filters out punctuation as keywords
                        counts = Counter(tokens)
                        dictCounts=dict(counts)
                        for key1 in dictCounts:
                            filename= os.path.join("index",str(key1)+".xml")
                            print(filename)
                            if not os.path.exists(os.path.dirname(filename)):
                                try:
                                    os.makedirs(os.path.dirname(filename))
                                    print("made directory")
                                    root1 = ET.Element("index")
                                    ET.SubElement(root1, "tf",doc_id= str(doc_id) ).text = str(dictCounts[key1])
                                    tree = ET.ElementTree(root1)
                                    tree.write(filename)
                                except OSError as exc:
                                    if exc.errno != errno.EEXIST:
                                        raise
                                    print exc 
                                
                                # for listing in root1.findall("tf"):
                                # document = listing.find('doc_id')
                                # oldcount = listing.findtext('description')document.attrib.get("key")

                                # print(description, address.attrib.get("key"))
                            else:
                                # my_file = Path(filename)
                                if not os.path.isfile(filename) :
                                    #First time writing to file
                                    print("Got in")
                                    root1 = ET.Element("index")
                                    ET.SubElement(root1, "tf",doc_id= str(doc_id),path=file_path ).text = str(dictCounts[key1])
                                    tree = ET.ElementTree(root1)
                                    tree.write(filename)
                                else:  

                                    print(filename)
                                    text=""
                                    with open(filename, 'r') as myfile:
                                        text=myfile.read()
                                    print(text)
                                    root1= ET.fromstring(text)
                                    found_doc= None
                                    for tf in root1.iter('tf'):
                                        if int(tf.attrib.get("doc_id"))==doc_id:
                                            newWeight= int(tf.text)+dictCounts[key1]
                                            print(tf.text)
                                            tf.text= str(newWeight)
                                            print("newWeight"+" "+str(newWeight))
                                            found_doc=True
                                    if(found_doc):
                                        pass
                                    else:
                                        ET.SubElement(root1, "tf",doc_id= str(doc_id),path=file_path ).text = str(dictCounts[key1])
                                    tree = ET.ElementTree(root1)
                                    print(ET.tostring(root1, "utf-8"))
                                    tree.write(filename)
                        # else:
                        #     # print("got in")
                        #     for key2 in dictCounts:
                        #         filename2= os.path.join("FINDMAIL/","index",str(key2)+".xml")
                        #         if not os.path.exists(os.path.dirname(filename2)):
                        #             try:
                        #                 print("made directory")
                        #                 os.makedirs(os.path.dirname(filename2))
                        #                 root2 = ET.Element("index")
                        #             except OSError as exc: # Guard against race condition
                        #                 if exc.errno != errno.EEXIST:
                        #                     raise
                        #                 print exc 

                        #         else:
                        #             with open(filename2, 'r') as myfile:
                        #                 text=myfile.read()
                        #             root2= ET.fromstring(text)
                        #         ET.SubElement(root2, "tf",doc_id= str(doc_id) ).text = str(dictCounts[key2])
                        #         tree = ET.ElementTree(root2)
                        #         tree.write(filename2)

                        # if(doc_id==1):
                        #     master= dictCounts.copy()
                        #     doc_list[str(doc_id)] = dictCounts.copy() #Addes document id as key with word&frequency(dict) as value
                        #     master = dict((key, doc_list) for key in master) #Adding that one document id for all keys(words)
                        # else:
                        #     print(doc_lis)
                        #     doc_list[str(doc_id)] = dictCounts.copy()
                        #     dictCounts = dict((key, doc_list) for key in dictCounts) #Adding that one document id for all keys(words)
                        #     #master= mergeDict(dictCounts, master) # merge them to add new words
                        #     for key1 in dictCounts:
                        #         if key1 not in master:
                        #             master[key1]= dictCounts[key1]
                        #         else:
                        #             for key2 in dictCounts[key1]:
                        #                 if key2 not in master:
                        #                     master[key1][key2]=dictCounts[key1][]

                        #                 dict2[key1]+dict1[key1]
                        #     #master = dict((key, doc_list) for key in master) #Adding that one document id for all keys(words)
                        #     #print((master["residence"]))
                        #     """Build inverted index
                        #     for outside of dir and file loop"""
            doc_id=doc_id+1
    sortedmaster= sorted(master.keys(), key=lambda x:x.lower())
    for key in sortedmaster:
        print(key)
    # print(master["which"])
                    # """Merging two dictionaries"""
                    # k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)

                    # list(OrderedDict.fromkeys('abracadabra'))
                    # keyvalpair= {el:1 for el in tokens} #Makes word key and value is frequency 1
                    #print(tokens)
                    # for token in tokens:
                    #     final_tokens.append(token)

                    # #print text
                    # stemmer = SnowballStemmer("english")
                    # tokens = nltk.word_tokenize(text)
                    # tokens = [stemmer.stem(i) for i in tokens]
                    # tokens = [i for i in tokens if i not in string.punctuation] #filters out punctuation as keywords
                    # for token in tokens:
                    #             final_tokens.append(token) 
               
    #                 """Build inverted index
    #                 Run for outside of dir and file loop"""
    #                 for i in range(len(final_tokens)):
    #                     pos = i+1
    #                     word = final_tokens[i]
    #                     #print word
    #                     index_found = 0
    #                     if word not in "''":
    #                         """index_list has len 0 so not looping"""
    #                         #print len(index_list)
    #                         for index in range(len(index_list)):
    #                             #Check if it already exists in index_list, shouldn't
    #                             if index_list[index][0]==word:
    #                                 item = index_list[index][1]
    #                                 item.append(["D"+str(doc_id), pos])
    #                                 index_list[index][1] = item
    #                                 index_found = 1
    #                                 break
    #                         if index_found == 0:
    #                             index_list.append([word,[["D"+str(doc_id),pos]]])
    #                         doc_info[doc_id] = (doc_id, len(final_tokens))              
    #                     doc_id=doc_id+1
            
    # if not os.path.exists(os.path.dirname("JSON index/indexD.json")):
    #     try:
    #         os.makedirs(os.path.dirname("JSON index/indexD.json"))
    #     except OSError as exc: # Guard against race condition
    #         if exc.errno != errno.EEXIST:
    #             raise
    #         print exc     
                            
    # #Store files to JSON Format
    # index_list.sort(key=operator.itemgetter(0,1)) #Sorts files according to key
    # with open('JSON index/indexD.json', 'w') as outfile:
    #     json.dump(index_list, outfile)                                    
                                                            
            
                                                
if __name__ == '__main__':
    #main()
    start_time = time.time()
    """Check Mbox or Mdir. Diverge the path depending on there being a subfolder """
    main(os.path.join("FINDMAIL/","XML_files"))
    print("--- %s seconds ---" % (time.time() - start_time))#Measure execution time of program