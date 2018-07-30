import string
"""-Need to install NLTK first using Numpy and pip: 
https://davejingtian.org/2012/10/08/nltk-install-nltk-for-python2-7-on-64-bit-win-7/ """
import nltk
from nltk.stem.snowball import SnowballStemmer
import os
import json
import operator
import xml.etree.ElementTree as ETree #similar to cElementTree
import re

#nltk.download('all')
nltk.download('punkt')
path = "FINDMAIL/HTML files/"

"""If there are subfolders. Checks if MBOX or maildir."""
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    
def folders_in(path_to_parent):
    for dirname, subdirs, files in os.walk(path_to_parent):
        if not subdirs:
            return path_to_parent
        else:
            print subdirs[0]
            if RepresentsInt(subdirs[0]):
                return path_to_parent
            else:
                path_to_child= dirname+ subdirs[0]
                return path_to_child #first subdir in path
    #for fname in os.path.listdir(path_to_parent):
    #if os.path.isdir(os.path.join(path_to_parent,fname)):
    #yield os.path.join(path_to_parent,fname)
    
def walklevel(some_dir, level):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
def clean_html(html):
    """
    Copied from NLTK package.
    Remove HTML markup from the given string.
    :param html: the HTML string to be cleaned
    :type html: str
    :rtype: str
    """
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()

def main(path):
    doc_id=1
    index_list = []
    doc_info = {}            
    """One level means can only apply to Mbox"""
    for dirname, subdirs, files in walklevel(path, 1):
        #NB: Does not process files in order appearing in original folder
        for name in files:
            final_tokens=[] 
            if str(name).endswith('.html'):
                print name
                file_path = os.path.join(dirname, name)
                raw= None
                try: 
                    html = open(file_path).read().decode('utf-8')
                    raw = clean_html(html)                    
                except UnicodeDecodeError:
                    print "Decode error"        
                if not raw:
                    """No text in field.Can't add to token."""
                else:
                    """Tokenizing and stemming""" 
                    #print text
                    stemmer = SnowballStemmer("english")
                    tokens = nltk.word_tokenize(raw)
                    tokens = [stemmer.stem(i) for i in tokens]
                    tokens = [i for i in tokens if i not in string.punctuation] #filters out punctuation as keywords
                    for token in tokens:
                        final_tokens.append(token) 

                    """Build inverted index Run for outside of dir and file loop"""
                    for i in range(len(final_tokens)):
                        pos = i+1
                        word = final_tokens[i]
                        #print word
                        index_found = 0
                        if word not in "''":
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
                
                #try:
                    #self.doc = ETree.parse( file_path)
                    #print "Well Formed"                    
                    ## do stuff with it ...
                #except  ETree.ParseError :
                    #print( "ERROR in {0} : {1}".format( ETree.ParseError.filename, ETree.ParseError.msg ) )                
            #print 
            #print '***', file_path
            #print '*' * 40 

            #final_tokens=[]                      
            #"""Extract content from documents"""
            #tree = ET.parse(file_path)
            #root = tree.getroot()
            #for child in root:
                ##if child.tag != 'DOCNO': """If you want to filter by tag"""
                #text = child.text 
                ##print text
                #if not text:
                    #"""No text in field.Can't add to token."""
                #else:
                    #"""Tokenizing and stemming""" 
                    ##print text
                    #stemmer = SnowballStemmer("english")
                    #tokens = nltk.word_tokenize(text)
                    #tokens = [stemmer.stem(i) for i in tokens]
                    #tokens = [i for i in tokens if i not in string.punctuation] #filters out punctuation as keywords
                    #for token in tokens:
                        #final_tokens.append(token) 

                    #"""Build inverted index
                                                            #Run for outside of dir and file loop"""
                    #for i in range(len(final_tokens)):
                        #pos = i+1
                        #word = final_tokens[i]
                        ##print word
                        #index_found = 0
                        #if word not in "''":
                            #"""index_list has len 0 so not looping"""
                            ##print len(index_list)
                            #for index in range(len(index_list)):
                                ##Check if it already exists in index_list, shouldn't
                                #if index_list[index][0]==word:
                                    #item = index_list[index][1]
                                    #item.append(["D"+str(doc_id), pos])
                                    #index_list[index][1] = item
                                    #index_found = 1
                                    #break
                            #if index_found == 0:
                                #index_list.append([word,[["D"+str(doc_id),pos]]])
                            #doc_info[doc_id] = (doc_id, len(final_tokens))              
            #doc_id=doc_id+1

    if not os.path.exists(os.path.dirname("JSON index/indexE.json")):
        try:
            os.makedirs(os.path.dirname("JSON index/indexE.json"))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
            print exc     

    #Store files to JSON Format
    index_list.sort(key=operator.itemgetter(0,1))
    with open('JSON index/indexE.json', 'w') as outfile:
        json.dump(index_list, outfile)                                    



if __name__ == '__main__':
    start_time = time.time()
    """Check Mbox or Mdir. Diverge the path depending on there being a subfolder """
    path = folders_in("FINDMAIL/HTML files/")
    print path
    main(path)
    print("--- %s seconds ---" % (time.time() - start_time))#Measure execution time of program 