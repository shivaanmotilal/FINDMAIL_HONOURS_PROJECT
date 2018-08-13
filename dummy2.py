#Shivaan Motilal
#Programme to parse MBOX and Maildir Mailboxes
from __future__ import print_function, division
#from __future__ import unicode_literals
#from __future__ import absolute_imports
import mailbox
import argparse
import os
import errno
import webbrowser #for testing purposes
import email.utils #REDUNDANT because of below JSON imports
import xml.etree.cElementTree as ET
import time
from email.header import decode_header
import re
import shutil
from datetime import datetime
"""imports for JSON Conversion"""
import sys, urllib2, email, csv, StringIO, base64, json, pprint
from optparse import OptionParser

class parseMbox:
    def __init__(self, content = None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8" # output encoding 
        self.hasImage = False
        self.prePath= "FINDMAIL/HTML_files"
        
    def create_mbox(self,path):
        from_addr = email.utils.formataddr(('Author', 'author@example.com'))
        to_addr = email.utils.formataddr(('Recipient', 'recipient@example.com'))
        
        #Note Re-running this method adds more mails to the existing mbox file
        mbox = mailbox.mbox(path)
        """Prepare messages to be removed from existing mbox file"""
        to_remove = []
        for key, msg in mbox.iteritems():
            if not msg['subject'] == None: #Tag every existing message with subject in mbox
                print('Removing:', key)
                to_remove.append(key)
                
        mbox.lock()
        try:
            """-Delete items pre-specified to be removed"""
            for key in to_remove:
                mbox.remove(key)
                
            msg = mailbox.mboxMessage()
            msg.set_unixfrom('author Sat Feb  7 01:05:34 2009')
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = 'Sample message 1'
            msg.set_payload('This is the body.\nFrom (should be escaped).\nThere are 3 lines in this body.\n')
            mbox.add(msg)
            mbox.flush()
        
            msg = mailbox.mboxMessage()
            msg.set_unixfrom('author')
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = 'Sample message 2'
            msg.set_payload('This is the second body.\n')
            mbox.add(msg)
            mbox.flush()
        finally:
            mbox.unlock()
        
        print (open(path, 'r').read())
        
    '''-Specifically gets message body for each mail in mbox'''
    def getbody(self,message): #getting plain text 'email body'
        body = None
        if message.is_multipart():
            for part in message.walk():
                #print part.get_content_type()
                if part.is_multipart():
                    for subpart in part.walk():
                        #print subpart.get_content_type()
                        if subpart.get_content_type() == 'text/plain':
                            body = subpart.get_payload(decode=True)
                elif part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)
        elif message.get_content_type() == 'text/plain':
            body = message.get_payload(decode=True)
        return body
                    
    '''-Gets attachment from an email of html and png types'''
    def getAttachment(self,message, path): 
        #What if there are multiple attachments?
        attach = []
        #print len(message.get_payload())
        if message.is_multipart():
            for part in message.walk():               
                if part.is_multipart():
                    for subpart in part.walk():
                        if subpart.is_multipart():
                            for subsubpart in subpart.walk():
                                if subsubpart.get_content_type() == 'image/png':
                                    attach.append(subsubpart.get_payload(decode=True)) 
                                    self.hasImage= True
                                else:
                                    payload = subsubpart.get_payload(decode=True)
                                    attach.append(payload)
                                    if not subsubpart.get_filename():
                                        continue
                                    else:
                                        filename = os.path.join(path,subsubpart.get_filename())
                                        # Save the file.
                                        if payload and filename:
                                            self.createDirs(filename)
                                            self.append_to_file(filename,payload ,'wb')
                        elif subpart.get_content_type() == 'image/png':
                            attach.append(subpart.get_payload(decode=True)) 
                            self.hasImage= True
                        else:
                            payload = subpart.get_payload(decode=True)
                            attach.append(payload)
                            if not subpart.get_filename():
                                continue
                            else:
                                filename = os.path.join(path,subpart.get_filename())
                                # Save the file.
                                if payload and filename:                                     
                                    self.createDirs(filename)
                                    self.append_to_file(filename,payload ,'wb')
                elif part.get_content_type() == 'text/plain':
                    continue
                else:
                    # When decode=True, get_payload will return None if part.is_multipart()
                    # and the decoded content otherwise.
                    payload = part.get_payload(decode=True)
                    # Default filename can be passed as an argument to get_filename()
                    if not part.get_filename():
                        continue
                    else:
                        filename = path+part.get_filename()
                        # Save the file.
                        if payload and filename:
                            self.createDirs(filename)    
                            self.append_to_file(filename,payload ,'wb')
        elif message.get_content_type() == 'text/plain':
            #Do nothing
            pass
        return attach   
    
    """-Retrieves undecoded non-plain-text parts of email as list of attachments"""
    def get_undecoded_attachment(self, message, path):
        #What if there are multiple attachments?
        attach = []
        #print len(message.get_payload())
        if message.is_multipart():
            for part in message.walk():               
                if part.is_multipart():
                    for subpart in part.walk():
                        if part.get_content_type() == 'text/plain':
                            attach.append(subpart)
                        else:
                            payload = subpart.get_payload(decode=True)
                            attach.append(subpart)
                            if not subpart.get_filename():
                                continue
                            else:
                                decodePart= self.decodePart(subpart.get_filename())
                                decodePart= self.decodeHeader(decodePart)
                                filename = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", decodePart)
                                filename = os.path.join(path, decodePart)
                                if payload and filename:
                                    self.createDirs(filename)
                                    try:
                                        self.append_to_file(filename,payload ,"wb")   
                                    except  IOError:
                                        print('An error occured trying to read the file.')
                    break                    
                elif part.get_content_type() == 'text/plain':
                    continue
                else:
                    # When decode=True, get_payload will return None if part.is_multipart()
                    # and the decoded content otherwise.
                    payload = part.get_payload(decode=True)
                    attach.append(part)
                    # Default filename can be passed as an argument to get_filename()
                    if not part.get_filename():
                        continue
                    else:
                        decodePart= self.decodePart(part.get_filename())  
                        decodePart= self.decodeHeader(decodePart)
                        filename = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", decodePart) 
                        filename = os.path.join(path, decodePart)
                        # Save the file.
                        attach.append(part)
                        if payload and filename:
                            self.createDirs(filename)                           
                            try:
                                self.append_to_file(filename,payload ,"wb")
                            except  IOError:
                                print('An error occured trying to read the file.')                        
        elif message.get_content_type() == 'text/plain':
            #Do nothing
            pass
        return attach    
    
    """-Prints all output as plain text for each email"""
    def printToTextFiles(self,path):
        count1=1;
        mbox = mailbox.mbox(path)
        for message in mbox:
            """File paths"""
            filename = os.path.join("FINDMAIL/Plain text files/",str(count1)+".txt")
            body= os.path.join("FINDMAIL/Plain text files/body/", str(count1)+".txt")
            self.createDirs(filename)   
            self.createDirs(os.path.dirname(body))
            self.append_to_file(filename,str(message) ,"w")
            self.append_to_file(filename,str(self.getbody(message)) ,"w")
            count1=count1+1    
    
    def decodePart(self,part):
        dh= decode_header(part)
        default_charset = 'ASCII'
        decodePart= ''.join([ unicode(t[0], t[1] or default_charset) for t in dh ])
        return decodePart
    
    def decodeHeader(self,part):
        if not part:
            return None
        else:
            strippedPart= part.replace('"', '') #Remove quote so decode_header can recognise encoding
            bytes, encoding = decode_header(strippedPart)[0]
            if not encoding:
                return part
            else: 
                decoded=bytes.decode(encoding)
                return decoded.encode('utf8')       
     
    def createHTMLString(self, Count, From, To, Subject, Time, Body, Embedded, Attach):
        if Attach== """<p>ATTACHMENTS:</p>""":
            Attach= """<p> No Attachments</p>"""
        if Subject is None:
            Subject= """No Subject"""
        if From is None:
            From= """No From"""
        if To is None:
            To= """No Time"""
        if Body==str(""""""):
            Body= """No Body"""
        if Time is None:
            Time= """No Time"""
        msgHTML = """<!DOCTYPE html><html>
        <head> 
            <meta name="email_"""+str(Count)+ """ " content="width=device-width, initial-scale=1">
            <link href="../../email_style.css" rel= "stylesheet" type= "text/css"> 
        </head>
        <body>
        <pre id= "subject"><font size="4">"""+Subject+"""<font></pre>
        <div class="top">
            <img src="../../profile.png" alt="Profile"  height="42" width="42"">
            <table style="width:100%">
                <tr>
                  <td><p id="sender"> <b>"""+From +""" </b></p></td>
                  <td><p id="datetime"><b>"""+Time+"""</b></p></td>
                </tr>
                <tr>
                  <td><p id="to"><b> To: """+To+"""</b></p></td>
                </tr>
              </table>
        </div>
        <section id="body">
              <!-- put the body together with embedded html--> 
            <pre> No body</pre>
                <!--the embedded html--> 
                """+Embedded+"""
        </section>
         <!--attachments--> 
        <div class="attachments">
            <!-- put the body together with embedded html -->
            """+Attach+"""
        </div>
        </html>"""
        return msgHTML
    
    """-Deletes all files or directories in directory of path passed in"""
    def clearFolder(self, folder):
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
                
    """-Prints emails to html files"""
    def printToHTMLFiles(self,path):
        #reload(sys)  # Reload does the trick!
        #sys.setdefaultencoding('UTF8')        
        count2=1;
        data= {}
        newpath="";
        mbox = mailbox.mbox(path)
        for message in mbox:  
            #print message
            """Get from, to and subject field etc from email"""
            msgFrom= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["from"]))
            msgTo= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["to"]))
            msgTo= re.sub('[<>]', '', msgTo)
            msgSubject= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["subject"]))
            msgTime= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["date"]))
            # """Convert date-time to usable time format"""
            # REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
            # varTime= (time.mktime(email.utils.parsedate(msgTime)) +time.timezone - REMOTE_TIME_ZONE_OFFSET)            
            # print("Time: ", time.strftime('%Y/%m/%d --- Time %H:%M:%S', time.localtime(varTime)))
            strBody= str("""""")
            strBody = strBody+str(self.getbody(message))
            strBody= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(strBody))
            """Derive attachment part of HTML File"""
            msgATT="""<p>ATTACHMENTS:</p>"""
            embedHTML=""""""
            for att in self.get_undecoded_attachment(message, os.path.join("FINDMAIL/HTML_files/Attachments/"+ str(count2)+"/")):
                content_type=att.get_content_type()
                #print content_type
                strAttach= str(att)
                if content_type=='text/html':
                    embedHTML= str(embedHTML)+str(att.get_payload(decode=True)) 
                elif not att.get_filename():
                    continue                
                else:
                    #print att.get_filename()
                    decodeFilename= self.decodeHeader(att.get_filename())
                    msgATT=msgATT+ """<p><a target= "_blank" href= "Attachments/"""+ str(count2)+"""/"""+decodeFilename+""" "><img src="Attachments/"""+ str(count2)+"""/"""+decodeFilename+""" " alt= " """+ att.get_filename()+ """ " style="width:150px"></a></p>"""
                    
            msgHTML=self.createHTMLString(count2, msgFrom, msgTo, msgSubject, msgTime, strBody, embedHTML, msgATT)                             
            
            """-File paths"""
            filename = os.path.join(self.prePath,str(count2)+".html")
            
            newpath = "All.txt"
            if count2==1:
                open(newpath, 'w').close() 
                self.append_to_file(newpath,filename+"\n","a" )                               
            else:
                self.append_to_file(newpath,filename+"\n","a")
            if count2==1:
                self.clearFolder(self.prePath)            
            self.createDirs(filename)
            self.append_to_file(filename,msgHTML,"w")
            count2= count2+1  
        json_data = json.dumps(data)
        open('all.json', 'w').close() 
        self.append_to_file('all.json',json_data,'a')
        return json_data 
            
    def createDirs(self,path):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
                print(exc)  

    def append_to_file(self, newpath, msg, op):
        with open(newpath, op) as g: #Write message to single file
            g.write(msg)   
        g.close() 

    """Create directory of all emails in mbox as XML files"""
    def printToXMLFiles(self, path):
        #Set default encoding to UTF-8 so system can parse email body
        reload(sys)  
        sys.setdefaultencoding('utf8')
        unsortedArray = []        
        date={}
        count4=1
        mbox = mailbox.mbox(path)
        self.clearFolder(os.path.join("FINDMAIL","XML_files/"))
        for message in mbox:  
            """Get from, to and subject fields etc. from email"""  
            root = ET.Element("doc") 
            filepath=os.path.join("FINDMAIL/HTML_files/",str(count4)+".html") 
            ET.SubElement(root, "path", name="PATH").text =  filepath
            ET.SubElement(root, "from", name="FROM").text = message["from"]
            ET.SubElement(root, "to", name="TO").text = message["to"]
            ET.SubElement(root, "subject", name="SUBJECT").text = re.sub('[^A-Za-z0-9]+', ' ', message["subject"])
            ET.SubElement(root, "message-id", name="MESSAGE-ID").text = message["message-id"]        
            """Convert date-time to usable time format"""
            REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
            varTime= (time.mktime(email.utils.parsedate(message["date"])) +time.timezone - REMOTE_TIME_ZONE_OFFSET) 
            formatTime=  time.strftime('%Y/%m/%d %H:%M', time.localtime(varTime)) 
            # datetime_object = datetime.strptime(formatTime, '%Y/%m/%d %H:%M')
            # print("DateTime: ", message["date"])        
            # print("Time: ",formatTime)
            date={ 'sender': message["from"] ,'subject': re.sub('[^A-Za-z0-9]+', ' ', message["subject"]),'id': message["message-id"],'file': filepath, 'date': str(formatTime)}
            unsortedArray.append(date)
            # timeObj= time.mktime(email.utils.parsedate(message["date"]))
            # formatTime= time.strftime('%Y/%m/%d --- Time %H:%M:%S', timeObj)
            # print(formatTime+'\n')
            ET.SubElement(root, "date", name="DATE").text = formatTime
            #dateObj.append()
            if self.getbody(message):
                ET.SubElement(root, "body", name="BODY").text = re.sub('[^A-Za-z0-9]+', ' ', self.getbody(message)).encode('utf-8')
            else:
                ET.SubElement(root, "body", name="BODY").text ="" 
            filename = os.path.join("FINDMAIL/XML_files/"+ str(count4)+".xml")
            self.createDirs(filename)      
            tree = ET.ElementTree(root)
            tree.write(filename) 
            count4=count4+1  
        sortedArray = sorted(unsortedArray,key=lambda x: datetime.strptime(x['date'], '%Y/%m/%d %H:%M'), reverse=True)
        root = ET.Element("All")
        for item in sortedArray:
            ET.SubElement(root, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
        tree = ET.ElementTree(root)
        filepath2=os.path.join("Structure","All.xml")
        self.createDirs(filepath2)
        tree.write(filepath2)
        print(sortedArray)

    @staticmethod
    def main(self,path):
        """FINDMAIL/mailboxes/mbox/test.mbox"""
        #mbox = mailbox.mbox(path)       
        #self.printToTextFiles(path)
        self.printToHTMLFiles(path)
        self.printToXMLFiles(path)

class parseMDIR:
    def __init__(self, content = None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8" # output encoding 
        self.hasImage= False
        self.prePath= "FINDMAIL/HTML_files"
        self.inboxname= ""
        
    def make_message(
                self,
                subject='subject',
                from_addr='from@example.com',
                to_addr='to@example.com'):
        mbox = mailbox.Maildir(self._path)
        mbox.lock()
        try:
            msg = mailbox.MaildirMessage()
            msg.set_unixfrom('author Sat Jul 23 15:35:34 2017')
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = subject
            msg['Date'] = email.utils.formatdate()
            msg.set_payload(textwrap.dedent('''
            This is the body.
            There are 2 lines.
            '''))
            mbox.add(msg)
            mbox.flush()
        finally:
            mbox.unlock()
        return msg 
    
    '''-Specifically gets message body for each mail in mbox'''
    def getbody(self,message): #getting plain text 'email body'
        body = None
        if message.is_multipart():
            for part in message.walk():
                #print part.get_content_type()
                if part.is_multipart():
                    for subpart in part.walk():
                        #print subpart.get_content_type()
                        if subpart.get_content_type() == 'text/plain':
                            body = subpart.get_payload(decode=True)
                elif part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)
        elif message.get_content_type() == 'text/plain':
            body = message.get_payload(decode=True)
        return body
    
    '''-Gets attachment from an email of html and png types'''
    def getAttachment(self,message): 
        #What if there are multiple attachments?
        attach = []
        if message.is_multipart():
            for part in message.walk():
                if part.is_multipart():
                    for subpart in part.walk():
                        #if subpart.get_content_type() == 'text/html': #can also use .get_filename() to get ...
                            #attach.append(subpart.get_payload(decode=True))
                        if subpart.get_content_type() == 'image/png':
                            attach.append(subpart.get_payload(decode=True))
                        else:
                            attach.append(subpart.get_payload(decode=True))
                elif part.get_content_type() == 'text/plain':
                    continue
        elif message.get_content_type() == 'text/plain':
            #Do nothing
            pass
        return attach   
    
    """-Retrieves undecoded non-plain-text parts of email as list of attachments"""
    def get_undecoded_attachment(self, message, path):
        #What if there are multiple attachments?
        attach = []
        #print len(message.get_payload())
        if message.is_multipart():
            for part in message.walk():               
                if part.is_multipart():
                    for subpart in part.walk():
                        if part.get_content_type() == 'text/plain':
                            attach.append(subpart)
                        else:
                            payload = subpart.get_payload(decode=True)
                            attach.append(subpart)
                            if not subpart.get_filename():
                                continue
                            else:
                                decodePart= self.decodePart(subpart.get_filename())  
                                decodePart= self.decodeHeader(decodePart)                                  
                                filename = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", decodePart) #remove any unwanted characters
                                filename = os.path.join(path, filename)
                                if payload and filename:
                                    self.createDirs(filename) 
                                    try:
                                        self.append_to_file(filename,payload,"wb")
                                    except  IOError:
                                        print('An error occured trying to read the file.')
                    break                    
                elif part.get_content_type() == 'text/plain':
                    continue
                else:
                    # When decode=True, get_payload will return None if part.is_multipart()
                    # and the decoded content otherwise.
                    payload = part.get_payload(decode=True)
                    attach.append(part)
                    # Default filename can be passed as an argument to get_filename()
                    if not part.get_filename():
                        continue
                    else:
                        decodePart= self.decodePart(part.get_filename())  
                        decodePart= self.decodeHeader(decodePart)                                             
                        filename = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", filename)
                        filename = os.path.join(path, filename)
                        # Save the file.
                        attach.append(part)
                        if payload and filename:
                            self.createDirs(filename)                         
                            try:
                                self.append_to_file(filename,payload,"wb")
                            except  IOError:
                                print('An error occured trying to read the file.')                        
        elif message.get_content_type() == 'text/plain':
            #Do nothing
            pass
        return attach
    
    def decodePart(self,part):
        dh= decode_header(part)
        default_charset = 'ASCII'
        decodePart= ''.join([ unicode(t[0], t[1] or default_charset) for t in dh ])
        return decodePart
    
    def decodeHeader(self,part):
        if not part:
            return None
        else:
            strippedPart= part.replace('"', '') #Remove quote so decode_header can recognise encoding
            bytes, encoding = decode_header(strippedPart)[0]
            if not encoding:
                return part
            else: 
                decoded=bytes.decode(encoding)
                return decoded.encode('utf8')
    
    def createHTMLString(self, Count, From, To, Subject, Time, Body, Embedded, Attach):
        if Attach== """<p>ATTACHMENTS:</p>""":
            Attach= """<p> No Attachments</p>"""
        if Subject is None:
            Subject= """No Subject"""
        if From is None:
            From= """No From"""
        if To is None:
            To= """No Time"""
        if Body==str(""""""):
            Body= """No Body"""
        if Time is None:
            Time= """No Time"""
        msgHTML = """<!DOCTYPE html><html>
        <head> 
            <meta name="email_"""+str(Count)+ """ " content="width=device-width, initial-scale=1">
            <link href="../../email_style.css" rel= "stylesheet" type= "text/css"> 
        </head>
        <body>
        <pre id= "subject"><font size="4">"""+Subject+"""<font></pre>
        <div class="top">
            <img src="../../profile.png" alt="Profile"  height="42" width="42"">
            <table style="width:100%">
                <tr>
                  <td><p id="sender"> <b>"""+From +""" </b></p></td>
                  <td><p id="datetime"><b>"""+Time+"""</b></p></td>
                </tr>
                <tr>
                  <td><p id="to"><b> To: """+To+"""</b></p></td>
                </tr>
              </table>
        </div>
        <section id="body">
              <!-- put the body together with embedded html--> 
            <pre> No body</pre>
                <!--the embedded html--> 
                """+Embedded+"""
        </section>
         <!--attachments--> 
        <div class="attachments">
            <!-- put the body together with embedded html -->
            """+Attach+"""
        </div>
        </html>"""
        return msgHTML
    
    """-Deletes all files or directories in directory of path passed in"""
    def clearFolder(self, folder):
        if not os.path.exists(folder):
            pass #No directory so nothing to clear
        else:
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e) 
    
    def addToJSON(self, folder, data, folder_lst,fullname):
        if folder not in data:##No Key
            self.append_to_file(folder+'.txt',fullname+'.\n','a')
            folder_lst.append(fullname)
            data[folder] = folder_lst
            folder_lst=[]
        else:
            if not data[folder]: #No value
                self.append_to_file(folder+'.txt',fullname+'\n','a')
                folder_lst.append(fullname)
                data[folder] = folder_lst
                folder_lst=[]
            else:
                #Check value exists
                curr_lst=data[folder]
                if fullname not in curr_lst:
                    self.append_to_file(folder+'.txt',fullname+'\n','a')
                    curr_lst.append(fullname)
                data[folder] = curr_lst
        return data
                
    """Other type refers to maildirs that do not have the traditional
    new, cur and tmp folders. For emails that comply with RFC 2822"""
    def otherTypePrintToHTMLfiles(self,path):
        data= {}
        folder_lst=[]
        count5=1;
        firstpass=True;
        ##Actually recursively goes through file system even with for
        for dirname, subdirs, files in os.walk(path):
            #Filepath method-ineffiecient
            if firstpass:
                open("Dirs.txt", 'w').close() 
                for firstlvl in subdirs:
                    self.append_to_file("Dirs.txt",firstlvl+'.txt'+'\n','a')
                    folder_lst.append(firstlvl)
                firstpass=False;
                data["Root"] = folder_lst
            ##Actual for loop
            for name in files:                
                fullname = os.path.join(dirname, name)
                alldir= os.path.normpath(fullname).split(os.path.sep)
                for i in range(0,len(alldir)-1):
                    #Assumes you don't have inboxname duplicated earlier(leftmost) in path  
                    if alldir[0]==self.inboxname:
                        del alldir[0]
                        break
                    del alldir[0]
                #Gets directories within mailbox
                nesting= (len(alldir)-1) #To cater for file name romove 1
                fpath=os.path.join(*alldir)
                specpath, file = os.path.split(fpath)
                #print("specpath",specpath)
                #Filepath method inefficient
                specdirs= os.path.normpath(specpath).split(os.path.sep)
                folder_lst=[] ##Clear the list
                for i, folder in reversed(list(enumerate(specdirs))): 
                    if i==len(specdirs)-1:
                        #open(folder+'.txt', 'w').close()
                        ##self.append_to_file(folder+'.txt',fullname+'\n','a')
                        self.addToJSON(folder, data, folder_lst,fullname)
                    else:
                        #open(folder+'.txt', 'w').close()
                        #Check key exists
                        self.addToJSON(folder, data, folder_lst,specdirs[i+1]+'.txt')
                with open(fullname, 'r') as myfile:
                    text=myfile.read()  #.replace('\n', '')  to remove newline
                message=  email.message_from_string(text)
                msgFrom= message["from"]
                msgTo= message["to"]
                msgSubject= message["subject"]
                msgID= message["message-id"]
                msgTime= message["date"]
                strBody=""""""
                strBody = str(self.getbody(message))   
                
                """Derive attachment part of HTML File"""
                msgATT="""<p>ATTACHMENTS:</p>"""
                embedHTML=""""""
                for att in self.get_undecoded_attachment(message, os.path.join(self.prePath,"Attachments/", str(count5)+"/")):
                    content_type=att.get_content_type()
                    #print content_type
                    strAttach= str(att)
                    if content_type=='text/html':
                        embedHTML= embedHTML+att.get_payload(decode=True) 
                    elif not att.get_filename():
                        continue                
                    else:
                        msgATT=msgATT+ """<p><a target= "_blank" href= " """+ nesting * """../"""+"""Attachments/"""+ str(count5)+"""/"""+att.get_filename()+""" "><img src=" ../Attachments/"""+ str(count5)+"""/"""+att.get_filename()+""" " alt= " """+ att.get_filename()+ """ " style="width:150px"></a></p>"""
                        
                msgHTML=self.createHTMLString(count5, msgFrom, msgTo, msgSubject, msgTime, strBody, embedHTML, msgATT)                                   
                """File paths"""
                filename = os.path.join(self.prePath,specpath, str(count5)+".html")
                newpath= "All.txt"
                if count5==1:
                    open(newpath, 'w').close() 
                    self.append_to_file(newpath, filename+'\n','a')                                    
                else:
                    self.append_to_file(newpath, filename+'\n','a')
                if count5==1:
                    self.clearFolder(self.prePath)
                self.createDirs(filename) 
                self.append_to_file(filename,msgHTML,"w")
                count5= count5+1  
        json_data = json.dumps(data)
        open('all.json', 'w').close() 
        self.append_to_file('all.json',json_data,'a')
        return json_data
                
    def createDirs(self,path):
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
                print(exc)  
    
    def append_to_file(self, newpath, msg,op):
        with open(newpath, op) as g: #Write message to single file
            g.write(msg)   
        g.close() 
        
    """determine if mailbox is purely maildir with new, cur and tmp directories"""
    def isPureMaildir(self,path):
        counter=0;
        for dirname, subdirs, files in os.walk(path):
            for directory in subdirs:
                if (directory=="new"):
                    counter=counter+1
                if (directory=="tmp"):
                    counter=counter+1
                if (directory=="cur"):
                    counter= counter+1
        if counter==3:
            return True
        else:
            return False
    """Create directory of all emails in mdir as XML files. 
    Specify path to mdir directory"""
    def printToXMLFiles(self, path):
        count4=1;
        prevFolder=""
        unsortedArray=[]
        for dirname, subdirs, files in os.walk(path):
            # if count4==1:
            #     for firstlvl in subdirs:
            #         open("Dirs.txt", 'w').close() 
            #         self.append_to_file("Dirs.txt",firstlvl,"a")
            for name in files:          
                fullname = os.path.join(dirname, name)
                alldir= os.path.normpath(fullname).split(os.path.sep)
                for i in range(0,len(alldir)-1):
                    #Assumes you don't have inboxname duplicated earlier(leftmost) in path
                    if alldir[0]==self.inboxname:
                        del alldir[0]
                        break
                    del alldir[0]
                #Gets directories within mailbox
                nesting= (len(alldir)-1) #To cater for file name romove 1
                fpath=os.path.join(*alldir)
                specpath, file = os.path.split(fpath)
                splitspecpath= os.path.normpath(specpath).split(os.path.sep)
                curr_folderpath= ""
                curr_foldername=""
                splitspecpath = filter(lambda name: name.strip(), splitspecpath)
                for i in range(0,len(splitspecpath)-1):
                    print(splitspecpath[i])
                    foldername=os.path.join("Structure/",splitspecpath[i]+".xml")
                    self.createDirs(foldername)
                    root = ET.Element(splitspecpath[i])
                    print(str(i+1)+" "+str(len(splitspecpath)-1))
                    if((i+1)==(len(splitspecpath)-1)):
                        #reached last level of nesting
                        curr_folderpath=foldername
                        curr_foldername= splitspecpath[i]
                        print("got in!",splitspecpath[i])
                    else:
                        ET.SubElement(root, "tf",subfolder= splitspecpath[i+1] ).text = str(0.001)
                        # self.append_to_file(foldername, "",wb)
                        tree = ET.ElementTree(root)
                        tree.write(foldername)
                filename = os.path.join("FINDMAIL/XML_files/",specpath, str(count4)+".xml")
                with open(fullname, 'r') as myfile:
                    data=myfile.read()  #.replace('\n', '')  to remove newline
                message=  email.message_from_string(data)
                root = ET.Element("doc")
                # root2= ET.Element(curr_foldername)
                filepath=os.path.join("FINDMAIL/HTML_files/",specpath,str(count4)+".html")
                ET.SubElement(root, "path", name="PATH").text = filepath
                ET.SubElement(root, "from", name="FROM").text = message["from"]
                ET.SubElement(root, "to", name="TO").text = message["to"]
                if not message["subject"]:
                    msgSubject = message["subject"]
                else:
                    msgSubject= re.sub('[^A-Za-z0-9]+', ' ', message["subject"])
                ET.SubElement(root, "subject", name="SUBJECT").text = msgSubject
                ET.SubElement(root, "message-id", name="MESSAGE-ID").text = message["message-id"]        
                """Convert date-time to usable time format"""
                if not message["date"]:
                    msgDate = ""
                else:
                    REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
                    varTime= (time.mktime(email.utils.parsedate(message["date"])) +time.timezone - REMOTE_TIME_ZONE_OFFSET) 
                    formatTime=  time.strftime('%Y/%m/%d %H:%M', time.localtime(varTime)) 
                    msgDate= formatTime
                ET.SubElement(root, "date", name="DATE").text = msgDate
                if self.getbody(message):
                    msgBody= re.sub('[^A-Za-z0-9]+', ' ', self.getbody(message)).encode('utf-8')
                else:
                    msgBody=""
                ET.SubElement(root, "body", name="BODY").text =msgBody
                if(count4==1):
                    prevFolder=curr_foldername
                    date={ 'sender': message["from"] ,'subject': msgSubject,'id': message["message-id"],'file': filepath, 'date': str(formatTime)}
                    unsortedArray.append(date)
                    print(prevFolder)
                else:
                    #Continue  adding to dictionary if same folder
                    if(prevFolder==curr_foldername):
                        date={ 'sender': message["from"] ,'subject': msgSubject,'id': message["message-id"],'file': filepath, 'date': str(formatTime)}
                        unsortedArray.append(date)
                    #Sort dictionary and add to xml 
                    else:
                        #sort dictionary
                        sortedArray = sorted(unsortedArray,key=lambda x: datetime.strptime(x['date'], '%Y/%m/%d %H:%M'), reverse=True)
                        #Add sorted to xml file
                        root = ET.Element(prevFolder)
                        for item in sortedArray:
                            ET.SubElement(root, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
                        tree = ET.ElementTree(root)
                        #self.createDirs(curr_folderpath)
                        tree.write(curr_folderpath)
                        #reinitialise unsorted array
                        unsortedArray=[]
                        #reset prevFolder to new Folder
                        prevFolder=curr_foldername
                tree = ET.ElementTree(root)
                self.createDirs(filename)
                tree.write(filename)
                count4= count4+1

    @staticmethod        
    def main(self, path):
        """FINDMAIL/mailboxes/maildir/test1"""
        #self.isPureMaildir(args.path)
        alldir= os.path.normpath(path).split(os.path.sep)
        self.inboxname= alldir[-1]
        self.otherTypePrintToHTMLfiles(path)
        self.printToXMLFiles(path)
        
if __name__ == '__main__':
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="specify path to archive from home directory")
    args = parser.parse_args()
    if args.path[-5:]== ".mbox":
        mbox=parseMbox()
        #mbox.create_mbox('FINDMAIL/mailboxes/mbox/example.mbox')
        mbox.main(mbox, args.path)
    else:
        maildir= parseMDIR()
        maildir.main(maildir, args.path)    
    print("--- %s seconds ---" % (time.time() - start_time))#Measure execution time of program