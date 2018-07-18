#from pyspark import SparkContext    
#sc = SparkContext("local", "app")

#path = '/FINDMAIL/XML files/'
#rdd = sc.wholeTextFiles(path)

#output = rdd.flatMap(lambda (file,contents):contents.lower().split())\
            #.map(lambda file,word: (word,file))\
            #.reduceByKey(lambda a,b: a+b)
#print output.take(10)
"""To use nltk need to install anaconda(bundles python etc) or pip and then pypy """


import xml.etree.cElementTree as ET
import string
"""-Need to install NLTK first using Numpy and pip: 
https://davejingtian.org/2012/10/08/nltk-install-nltk-for-python2-7-on-64-bit-win-7/ """

import nltk
from nltk.stem.snowball import SnowballStemmer
import os
import json
import operator

#nltk.download('all')
nltk.download('punkt')
path = "FINDMAIL/XML files/"

def main():
            doc_id=1
            index_list = []
            doc_info = {}            
            for dirname, subdirs, files in os.walk(path):
                        #NB: Does not process files in order appearing in original folder
                        for name in files:
                                    file_path = os.path.join(dirname, name)
                                    #print 
                                    #print '***', file_path
                                    #print '*' * 40 
                                    
                                    final_tokens=[]
                                                                        
                                    """Extract content from documents"""
                                    tree = ET.parse(file_path)
                                    root = tree.getroot()
                                    for child in root:
                                                #if child.tag != 'DOCNO': """If you want to filter by tag"""
                                                text = child.text 
                                                #print text
                                                if not text:
                                                            """No text in field.Can't add to token."""
                                                else:
                                                            """Tokenizing and stemming""" 
                                                            #print text
                                                            stemmer = SnowballStemmer("english")
                                                            tokens = nltk.word_tokenize(text)
                                                            tokens = [stemmer.stem(i) for i in tokens]
                                                            tokens = [i for i in tokens if i not in string.punctuation] #filters out punctuation as keywords
                                                            for token in tokens:
                                                                        final_tokens.append(token) 
                                                       
                                                            """Build inverted index
                                                            Run for outside of dir and file loop"""
                                                            for i in range(len(final_tokens)):
                                                                        pos = i+1
                                                                        word = final_tokens[i]
                                                                        #print word
                                                                        index_found = 0
                                                                        """index_list has len 0 so not looping"""
                                                                        #print len(index_list)
                                                                        for index in range(len(index_list)):
                                                                                    #Check if it already exists in index_list, shouldn't
                                                                                    if index_list[index][0]==word:
                                                                                                item = index_list[index][1]
                                                                                                item.append(["D"+str(doc_id), pos])
                                                                                                index_list[index][1] = item
                                                                                                index_found = 1
                                                                                                break
                                                                        if index_found == 0:
                                                                                    index_list.append([word,[["D"+str(doc_id),pos]]])
                                                                        doc_info[doc_id] = (doc_id, len(final_tokens))              
                                    doc_id=doc_id+1
                                    
            #Store files to JSON Format
            index_list.sort(key=operator.itemgetter(0,1))
            with open('indexA.json', 'w') as outfile:
                        json.dump(index_list, outfile)                                    
                                                            
            
                                                
if __name__ == '__main__':
            main()

        ##D1 : red red blue black red
        ##D2 : white red white white
        ##Index : [["red",[["D1",1], ["D1", 2], ["D1", 5], ["D2", 2]]], ["blue", [["D1", 4]]], ["black", [["D1", 4]]], ["white", [["D2", 1], ["D2", 3], ["D2", 4]]]]
        
        #index_list = []
        #doc_info = {}
        #for i in range(len(final_tokens)):
            #pos = i+1
            #word = final_tokens[i]
            #index_found = 0
            #for index in range(len(index_list)):
                #if index_list[index][0]==word:
                    #item = index_list[index][1]
                    #item.append([str(doc_id), pos])
                    #index_list[index][1] = item
                    #index_found = 1
                    #break
                #if index_found == 0:
                    #index_list.append([word,[[str(doc_id),pos]]])
                #doc_info[doc_id] = (doc_num, doc_size)
        
#"""Run this(above) for all the files in a loop which will complete the inverted index. 
#Once we have our inverted index, sort the index and store it on disk in JSON format. 
#We will use this file to run our queries against."""


