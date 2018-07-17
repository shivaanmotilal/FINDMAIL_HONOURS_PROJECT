#Shivaan Motilal
#Indexer converts mailbox to plain xml files

#!/usr/bin/env python

'''--Go through files recursively and process them'''
def recurse_files(curdir, pattern, exclusions, func=echo_fname, *args, **kw):
    "Recursively process file pattern"
    subdirs, files = [],[]
    level = kw.get('level',0)

    for name in os.listdir(curdir):
        fname = os.path.join(curdir, name)
        if name[-4:] in exclusions:
            pass            # do not include binary file type
        elif os.path.isdir(fname) and not os.path.islink(fname):
            subdirs.append(fname)
        # is it a regular expression?
        elif type(pattern)==type(re.compile('')):
            if pattern.match(name):
                files.append(fname)
        elif type(pattern) is StringType:
            if fnmatch.fnmatch(name, pattern):
                files.append(fname)

    for fname in files:
        apply(func, (fname,)+args)
    for subdir in subdirs:
        recurse_files(subdir, pattern, exclusions, func, level=level+1)

'''--Might be unnecessary or could actually be the parser stage'''    
#-- Data bundle for index dictionaries
class Index:
    def __init__(self, words, files, fileids):
        if words is not None:   self.WORDS = words
        if files is not None:   self.FILES = files
        if fileids is not None: self.FILEIDS = fileids

#-- "Split plain text into words" utility function
class TextSplitter:
    def initSplitter(self):
        prenum  = string.join(map(chr, range(0,48)), '')
        num2cap = string.join(map(chr, range(58,65)), '')
        cap2low = string.join(map(chr, range(91,97)), '')
        postlow = string.join(map(chr, range(123,256)), '')
        nonword = prenum + num2cap + cap2low + postlow
        self.word_only = string.maketrans(nonword, " "*len(nonword))
        self.nondigits = string.join(map(chr, range(0,48)) + map(chr, range(58,255)), '')
        self.alpha = string.join(map(chr, range(65,91)) + map(chr, range(97,123)), '')
        self.ident = string.join(map(chr, range(256)), '')
        self.init = 1

    def splitter(self, text, ftype):
        "Split the contents of a text string into a list of 'words'"
        if ftype == 'text/plain':
            words = self.text_splitter(text, self.casesensitive)
        else:
            raise NotImplementedError
        return words

    def text_splitter(self, text, casesensitive=0):
        """Split text/plain string into a list of words

        In version 0.20 this function is still fairly weak at
        identifying "real" words, and excluding gibberish
        strings.  As long as the indexer looks at "real" text
        files, it does pretty well; but if indexing of binary
        data is attempted, a lot of gibberish gets indexed.
        Suggestions on improving this are GREATLY APPRECIATED.
        """
        # Initialize some constants
        if not hasattr(self,'init'): self.initSplitter()

        # Speedup trick: attributes into local scope
        word_only = self.word_only
        ident = self.ident
        alpha = self.alpha
        nondigits = self.nondigits
        # 1.52: translate = string.translate

        # Let's adjust case if not case-sensitive
        if not casesensitive: text = string.upper(text)

        # Split the raw text
        allwords = string.split(text)

        # Finally, let's skip some words not worth indexing
        words = []
        for word in allwords:
            if len(word) > 25: continue         # too long (probably gibberish)

            # Identify common patterns in non-word data (binary, UU/MIME, etc)
            num_nonalpha = len(word.translate(ident, alpha))
            numdigits    = len(word.translate(ident, nondigits))
            # 1.52: num_nonalpha = len(translate(word, ident, alpha))
            # 1.52: numdigits    = len(translate(word, ident, nondigits))
            if numdigits > len(word)-2:         # almost all digits
                if numdigits > 5:               # too many digits is gibberish
                    continue                    # a moderate number is year/zipcode/etc
            elif num_nonalpha*3 > len(word):    # too much scattered nonalpha = gibberish
                continue

            word = word.translate(word_only)    # Let's strip funny byte values
            # 1.52: word = translate(word, word_only)
            subwords = word.split()             # maybe embedded non-alphanumeric
            # 1.52: subwords = string.split(word)
            for subword in subwords:            # ...so we might have subwords
                if len(subword) <= 2: continue  # too short a subword
                words.append(subword)
        return words

'''--Seems to split email text on certain conjunctions.
    Words length 25 or less considered acceptable'''
class  ZopeTextSplitter:
    def initSplitter(self):
        import Splitter
        stop_words=(
            'am', 'ii', 'iii', 'per', 'po', 're', 'a', 'about', 'above', 'across',
            'after', 'afterwards', 'again', 'against', 'all', 'almost', 'alone',
            'along', 'already', 'also', 'although', 'always', 'am', 'among',
            'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any',
            'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around',
            'as', 'at', 'back', 'be', 'became', 'because', 'become', 'becomes',
            'becoming', 'been', 'before', 'beforehand', 'behind', 'being',
            'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both',
            'bottom', 'but', 'by', 'can', 'cannot', 'cant', 'con', 'could',
            'couldnt', 'cry', 'describe', 'detail', 'do', 'done', 'down', 'due',
            'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else',
            'elsewhere', 'empty', 'enough', 'even', 'ever', 'every', 'everyone',
            'everything', 'everywhere', 'except', 'few', 'fifteen', 'fifty',
            'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly',
            'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get',
            'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her',
            'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers',
            'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'i',
            'ie', 'if', 'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it',
            'its', 'itself', 'keep', 'last', 'latter', 'latterly', 'least',
            'less', 'made', 'many', 'may', 'me', 'meanwhile', 'might', 'mill',
            'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must',
            'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless',
            'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not',
            'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once',
            'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our',
            'ours', 'ourselves', 'out', 'over', 'own', 'per', 'perhaps',
            'please', 'pre', 'put', 'rather', 're', 'same', 'see', 'seem',
            'seemed', 'seeming', 'seems', 'serious', 'several', 'she', 'should',
            'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some',
            'somehow', 'someone', 'something', 'sometime', 'sometimes',
            'somewhere', 'still', 'such', 'take', 'ten', 'than', 'that', 'the',
            'their', 'them', 'themselves', 'then', 'thence', 'there',
            'thereafter', 'thereby', 'therefore', 'therein', 'thereupon', 'these',
            'they', 'thick', 'thin', 'third', 'this', 'those', 'though', 'three',
            'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too',
            'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under',
            'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well',
            'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where',
            'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon',
            'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever',
            'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without',
            'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves',
            )
        self.stop_word_dict={}
        for word in stop_words: self.stop_word_dict[word]=None
        self.splitterobj = Splitter.getSplitter()
        self.init = 1

    def goodword(self, word):
        return len(word) < 25

    def splitter(self, text, ftype):
        """never case-sensitive"""
        if not hasattr(self,'init'): self.initSplitter()
        return filter(self.goodword, self.splitterobj(text, self.stop_word_dict))

'''--Basis or parent for all indexers used'''
#-- "Abstract" parent class for inherited indexers
#   (does not handle storage in parent, other methods are primitive)

class GenericIndexer:
    def __init__(self, **kw):
        apply(self.configure, (), kw)

    def whoami(self):
        return self.__class__.__name__

    def configure(self, REINDEX=0, CASESENSITIVE=0,
                        INDEXDB=os.environ.get('INDEXER_DB', 'TEMP_NDX.DB'),
                        ADD_PATTERN='*', QUIET=5):
        "Configure settings used by indexing and storage/retrieval"
        self.indexdb = INDEXDB
        self.reindex = REINDEX
        self.casesensitive = CASESENSITIVE
        self.add_pattern = ADD_PATTERN
        self.quiet = QUIET
        self.filter = None

    def add_files(self, dir=os.getcwd(), pattern=None, descend=1):
        self.load_index()
        exclusions = ('.zip','.pyc','.gif','.jpg','.dat','.dir')
        if not pattern:
            pattern = self.add_pattern
        recurse_files(dir, pattern, exclusions, self.add_file)

    def add_file(self, fname, ftype='text/plain'):
        "Index the contents of a regular file"
        if self.files.has_key(fname):   # Is file eligible for (re)indexing?
            if self.reindex:            # Reindexing enabled, cleanup dicts
                self.purge_entry(fname, self.fileids, self.files, self.words)
            else:                   # DO NOT reindex this file
                if self.quiet < 5: print "Skipping", fname
                return 0

        # Read in the file (if possible)
        try:
            if fname[-3:] == '.gz':
                text = gzip.open(fname).read()
            else:
                text = open(fname).read()
            if self.quiet < 5: print "Indexing", fname
        except IOError:
            return 0
        words = self.splitter(text, ftype)

        # Find new file index, and assign it to filename
        # (_TOP uses trick of negative to avoid conflict with file index)
        self.files['_TOP'] = (self.files['_TOP'][0]-1, None)
        file_index =  abs(self.files['_TOP'][0])
        self.files[fname] = (file_index, len(words))
        self.fileids[file_index] = fname

        filedict = {}
        for word in words:
            if filedict.has_key(word):
                filedict[word] = filedict[word]+1
            else:
                filedict[word] = 1

        for word in filedict.keys():
            if self.words.has_key(word):
                entry = self.words[word]
            else:
                entry = {}
            entry[file_index] = filedict[word]
            self.words[word] = entry

    def add_othertext(self, identifier):
        """Index a textual source other than a plain file

        A child class might want to implement this method (or a similar one)
        in order to index textual sources such as SQL tables, URLs, clay
        tablets, or whatever else.  The identifier should uniquely pick out
        the source of the text (whatever it is)
        """
        raise NotImplementedError

    def save_index(self, INDEXDB=None):
        raise NotImplementedError

    def load_index(self, INDEXDB=None, reload=0, wordlist=None):
        raise NotImplementedError

    def find(self, wordlist, print_report=0):
        "Locate files that match ALL the words in wordlist"
        self.load_index(wordlist=wordlist)
        entries = {}
        hits = copy.copy(self.fileids)      # Copy of fileids index
        for word in wordlist:
            if not self.casesensitive:
                word = string.upper(word)
            entry = self.words.get(word)    # For each word, get index
            entries[word] = entry           #   of matching files
            if not entry:                   # Nothing for this one word (fail)
                return 0
            for fileid in hits.keys():      # Eliminate hits for every non-match
                if not entry.has_key(fileid):
                    del hits[fileid]
        if print_report:
            self.print_report(hits, wordlist, entries)
        return hits

    def print_report(self, hits={}, wordlist=[], entries={}):
        # Figure out what to actually print (based on QUIET level)
        output = []
        for fileid,fname in hits.items():
            message = fname
            if self.quiet <= 3:
                wordcount = self.files[fname][1]
                matches = 0
                countmess = '\n'+' '*13+`wordcount`+' words; '
                for word in wordlist:
                    if not self.casesensitive:
                        word = string.upper(word)
                    occurs = entries[word][fileid]
                    matches = matches+occurs
                    countmess = countmess +`occurs`+' '+word+'; '
                message = string.ljust('[RATING: '
                                       +`1000*matches/wordcount`+']',13)+message
                if self.quiet <= 2: message = message +countmess +'\n'
            if self.filter:     # Using an output filter
                if fnmatch.fnmatch(message, self.filter):
                    output.append(message)
            else:
                output.append(message)

        if self.quiet <= 5:
            print (string.join(output,'\n'))
        sys.stderr.write('\n'+`len(output)`+' files matched wordlist: '+
                         `wordlist`+'\n')
        return output

    def purge_entry(self, fname, file_ids, file_dct, word_dct):
        "Remove a file from file index and word index"
        try:        # The easy part, cleanup the file index
            file_index = file_dct[fname]
            del file_dct[fname]
            del file_ids[file_index[0]]
        except KeyError:
            pass    # We'll assume we only encounter KeyError's
        # The much harder part, cleanup the word index
        for word, occurs in word_dct.items():
            if occurs.has_key(file_index):
                del occurs[file_index]
                word_dct[word] = occurs

    def index_loaded(self):
        return ( hasattr(self,'fileids') and
                 hasattr(self,'files')   and
                 hasattr(self,'words')      )

'''--Easy to transform to different programming language'''
class FlatIndexer(GenericIndexer, TextSplitter):
    """Concrete Indexer utilizing flat-file for storage

    See the comments in the referenced article for details; in
    brief, this indexer has about the same timing as the best in
    -creating- indexes and the storage requirements are
    reasonable.  However, actually -using- a flat-file index is
    more than an order of magnitude worse than the best indexer
    (ZPickleIndexer wins overall).

    On the other hand, FlatIndexer creates a wonderfully easy to
    parse database format if you have a reason to transport the
    index to a different platform or programming language.  And
    should you perform indexing as part of a long-running
    process, the overhead of initial file parsing becomes
    irrelevant.
    """
    def load_index(self, INDEXDB=None, reload=0, wordlist=None):
        # Unless reload is indicated, do not load twice
        if self.index_loaded() and not reload: return 0
        # Ok, now let's actually load it
        INDEXDB = INDEXDB or self.indexdb
        self.words = {}
        self.files = {'_TOP':(0,None)}
        self.fileids = {}
        try:                            # Read index contents
            for line in open(INDEXDB).readlines():
                fields = string.split(line)
                if fields[0] == '-':    # Read a file/fileid line
                    fileid = eval(fields[2])
                    wordcount = eval(fields[3])
                    fname = fields[1]
                    self.files[fname] = (fileid, wordcount)
                    self.fileids[fileid] = fname
                else:                   # Read a word entry (dict of hits)
                    entries = {}
                    word = fields[0]
                    for n in range(1,len(fields),2):
                        fileid = eval(fields[n])
                        occurs = eval(fields[n+1])
                        entries[fileid] = occurs
                    self.words[word] = entries
        except:
            pass                    # New index

    def save_index(self, INDEXDB=None):
        INDEXDB = INDEXDB or self.indexdb
        tab, lf, sp = '\t','\n',' '
        indexdb = open(INDEXDB,'w')
        for fname,entry in self.files.items():
            indexdb.write('- '+fname +tab +`entry[0]` +tab +`entry[1]` +lf)
        for word,entry in self.words.items():
            indexdb.write(word +tab+tab)
            for fileid,occurs in entry.items():
                indexdb.write(`fileid` +sp +`occurs` +sp)
            indexdb.write(lf)
            
class PickleIndexer(GenericIndexer, TextSplitter):
    def load_index(self, INDEXDB=None, reload=0, wordlist=None):
        # Unless reload is indicated, do not load twice
        if self.index_loaded() and not reload: return 0
        # Ok, now let's actually load it
        import cPickle
        INDEXDB = INDEXDB or self.indexdb
        try:
            pickle_str =  open(INDEXDB,'rb').read()
            db = cPickle.loads(pickle_str)
        except:                     # New index
            db = Index({}, {'_TOP':(0,None)}, {})
        self.words, self.files, self.fileids = db.WORDS, db.FILES, db.FILEIDS

    def save_index(self, INDEXDB=None):
        import cPickle
        INDEXDB = INDEXDB or self.indexdb
        db = Index(self.words, self.files, self.fileids)
        open(INDEXDB,'wb').write(cPickle.dumps(db, 1))

class XMLPickleIndexer(PickleIndexer):
    """Concrete Indexer utilizing XML for storage

    While this is, as expected, a verbose format, the possibility
    of using XML as a transport format for indexes might be
    useful.  However, [xml_pickle] is in need of some redesign to
    avoid gross inefficiency when creating very large
    (multi-megabyte) output files (fixed in [xml_pickle] version
    0.48 or above)
    """
    def load_index(self, INDEXDB=None, reload=0, wordlist=None):
        # Unless reload is indicated, do not load twice
        if self.index_loaded() and not reload: return 0
        # Ok, now let's actually load it
        from gnosis.xml.pickle import XML_Pickler
        INDEXDB = INDEXDB or self.indexdb
        try:                        # XML file exists
            xml_str = open(INDEXDB).read()
            db = XML_Pickler().loads(xml_str)
        except:                     # New index
            db = Index({}, {'_TOP':(0,None)}, {})
        self.words, self.files, self.fileids = db.WORDS, db.FILES, db.FILEIDS

    def save_index(self, INDEXDB=None):
        from gnosis.xml.pickle import XML_Pickler
        INDEXDB = INDEXDB or self.indexdb
        db = Index(self.words, self.files, self.fileids)
        open(INDEXDB,'w').write(XML_Pickler(db).dumps())

class ZPickleIndexer(PickleIndexer):
    def load_index(self, INDEXDB=None, reload=0, wordlist=None):
        # Unless reload is indicated, do not load twice
        if self.index_loaded() and not reload: return 0
        # Ok, now let's actually load it
        import cPickle, zlib
        INDEXDB = INDEXDB or self.indexdb
        try:
            pickle_str =  zlib.decompress(open(INDEXDB+'!','rb').read())
            db = cPickle.loads(pickle_str)
        except:                     # New index
            db = Index({}, {'_TOP':(0,None)}, {})
        self.words, self.files, self.fileids = db.WORDS, db.FILES, db.FILEIDS

    def save_index(self, INDEXDB=None):
        import cPickle, zlib
        INDEXDB = INDEXDB or self.indexdb
        db = Index(self.words, self.files, self.fileids)
        pickle_fh = open(INDEXDB+'!','wb')
        pickle_fh.write(zlib.compress(cPickle.dumps(db, 1)))

'''From here onwards, so called best indexer'''
class SlicedZPickleIndexer(ZPickleIndexer):
    segments = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#-!"
    def load_index(self, INDEXDB=None, reload=0, wordlist=None):
        # Unless reload is indicated, do not load twice
        if self.index_loaded() and not reload: return 0
        # Ok, now let's actually load it
        import cPickle, zlib
        INDEXDB = INDEXDB or self.indexdb
        db = Index({}, {'_TOP':(0,None)}, {})
        # Identify the relevant word-dictionary segments
        if not wordlist:
            segments = self.segments
        else:
            segments = ['-','#']
            for word in wordlist:
                segments.append(string.upper(word[0]))
        # Load the segments
        for segment in segments:
            try:
                pickle_str = zlib.decompress(open(INDEXDB+segment,'rb').read())
                dbslice = cPickle.loads(pickle_str)
                if dbslice.__dict__.get('WORDS'):   # If it has some words, add them
                    for word,entry in dbslice.WORDS.items():
                        db.WORDS[word] = entry
                if dbslice.__dict__.get('FILES'):   # If it has some files, add them
                    db.FILES = dbslice.FILES
                if dbslice.__dict__.get('FILEIDS'): # If it has fileids, add them
                    db.FILEIDS = dbslice.FILEIDS
            except:
                pass    # No biggie, couldn't find this segment
        self.words, self.files, self.fileids = db.WORDS, db.FILES, db.FILEIDS

    def julienne(self, INDEXDB=None):
        import cPickle, zlib
        INDEXDB = INDEXDB or self.indexdb
        segments = self.segments       # all the (little) indexes
        for segment in segments:
            try:        # brutal space saver... delete all the small segments
                os.remove(INDEXDB+segment)
            except OSError:
                pass    # probably just nonexistent segment index file
        # First write the much simpler filename/fileid dictionaries
        dbfil = Index(None, self.files, self.fileids)
        open(INDEXDB+'-','wb').write(zlib.compress(cPickle.dumps(dbfil,1)))
        # The hard part is splitting the word dictionary up, of course
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        segdicts = {}                           # Need batch of empty dicts
        for segment in letters+'#':
            segdicts[segment] = {}
        for word, entry in self.words.items():  # Split into segment dicts
            initchar = string.upper(word[0])
            if initchar in letters:
                segdicts[initchar][word] = entry
            else:
                segdicts['#'][word] = entry
        for initchar in letters+'#':
            db = Index(segdicts[initchar], None, None)
            pickle_str = cPickle.dumps(db, 1)
            pickle_fh = open(INDEXDB+initchar,'wb')
            pickle_fh.write(zlib.compress(pickle_str))

    save_index = julienne

PreferredIndexer = SlicedZPickleIndexer




