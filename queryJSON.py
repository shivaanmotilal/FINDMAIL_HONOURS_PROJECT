
import string
import nltk
from nltk.stem.snowball import SnowballStemmer
import re #imports regex expressions
import json
from pprint import pprint
import create_inverted_index
import os
import time

def main():
    query=raw_input("Enter query below:\n") 
    with open('JSON index/indexC.json') as f:
        index_data = json.load(f)
    
    #pprint(index_data)  
    final_list=[]
    merged_list=[]
    score={} #Stubs
    pattern = '\".+?\"|\w+'
    flag_AND = 0
    query = query.rstrip('\n')
    stemmer = SnowballStemmer("english")
    for token in re.findall(pattern,query):
        token = token.strip()
        token = token.lower()
        token = stemmer.stem(token)            
        if not token:
            continue 
        if token == 'AND':
            flag_AND = 1
            continue
        if re.match('\".+?\"',token):
            #process phrase terms in the query
            token = token.strip('"') 
            phrase_tokens = token.split() #we need to split the phrase terms because the regex would not split the phrase terms.              
            phrase_list = []
            phrase_tokens = token.split()
            for phrase_token in phrase_tokens:
                doc_list = []
                temp_list = []
                phrase_token = stemmer.stem(phrase_token )# process each stemmed phrase token            
                for item in index_data:
                    if item[0] == phrase_token:
                        doc_list = item[1]
                if phrase_list:
                    for doc,pos in doc_list:
                        val = [doc,pos-1]
                        if val in phrase_list:
                            temp_list.append(val)
                    phrase_list = temp_list
                    temp_list = [val[0] for val in phrase_list]
                    for doc in temp_list:
                        if doc in score:
                            score[doc] += n #n is number terms in query
                        else:
                            score[doc] = n                                             
                else:
                    phrase_list = doc_list                
                    temp_list = [val[0] for val in phrase_list]
                    for doc in temp_list:
                        if doc in score:
                            score[doc] += n #n is number terms in query
                        else:
                            score[doc] = n                        
                        
                #for item in index_data:
                    #if item[0] == token:
                        #doc_list = item[1]
                        #break
                    #temp_list = [val[0] for val in doc_list]
                    
            if flag_AND == 0:
                #process the query term against the prev terms with Boolean AND logic
                merged_list = final_list
                for val in temp_list:
                    if val not in merged_list:
                        merged_list.append(val)                                
                
            else:
                #process the query term against the prev terms with Boolean OR logic
                merged_list = [val for val in temp_list if val in final_list]
        else:
            #process non-phrase query terms
            doc_list = []
            for item in index_data:
                #print item[0], token
                if item[0] == token:
                    doc_list = item[1]
                    """TO:DO Get position of word"""
                    #print item[1]
                    #break
                #print "DOC LIST: ",doc_list
                temp_list = [val[0] for val in doc_list]
                #print "TEMP LIST: ",temp_list
                for doc in temp_list:
                    if doc in score:
                        score[doc] += 1 #n is number terms in query
                    else:
                        score[doc] = 1                       
            if not final_list:
                final_list = temp_list
                #print "FINAL LIST: ",temp_list
                merged_list= final_list
                """ The continue statement skips below AND OR checks"""
                continue 
            #print "flag_AND: ",flag_AND
            if flag_AND == 0:
                #process the query term against the prev terms with Boolean AND logic
                merged_list = final_list
                #print temp_list,"|||||", final_list
                for val in temp_list:
                    if val not in merged_list:
                        merged_list.append(val)    
                print "MERGED LIST: ",temp_list
            else:
                #print temp_list,"|||||", final_list
                #process the query term against the prev terms with Boolean OR logic 
                merged_list = [val for val in temp_list if val in final_list]
                
    print "Documents in which words appear:"           
    for item in merged_list:
        print item
    
    print "These are the scores:"
    for sc in score:
        #Rank is if there are multiple words, which doc has most
        print "DOC: "+sc, " RANK: "+str(score[sc])
        
def find_doc(name):
    print name
    doc_list= name.split(" ")
    for doc in doc_list:
        doc_num= doc[1:]
        path= create_inverted_index.folders_in("FINDMAIL/XML files/")
        for dirname, subdirs, files in os.walk(path):
            for filename in files:
                if filename==(doc_num+".xml"):
                    print ('*' * 40),filename,('*' * 40) 
                    fullpath= dirname+"/"+filename
                    with open(fullpath, 'r') as myfile:
                        data=myfile.read() 
                    print data
                    print ('*' * 86)
                    print 
                    print
        
    
if __name__ == '__main__':
    start_time = time.time()
    main()
    choice= raw_input("Would you like to open certain documents?y/n\n")
    if(choice.lower() =="y"):
        docs= raw_input("Enter name of docs you want to open separated by space. ie. \"D1 D2\" :\n")
        find_doc(docs)
    else:
        print "Bye!"
    print("--- %s seconds ---" % (time.time() - start_time))#Measure execution time of program 
    