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

"""imports for JSON Conversion"""
import sys, urllib2, email, csv, StringIO, base64, json, datetime, pprint
from optparse import OptionParser

class parseMbox:
    def __init__(self, content = None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8" # output encoding 
        self.hasImage = False
     
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
        
        print (open('FINDMAIL/mailboxes/mbox/example.mbox', 'r').read())
        
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
                                        filename = path+subsubpart.get_filename()
                                        # Save the file.
                                        if payload and filename:
                                            if not os.path.exists(os.path.dirname(filename)):
                                                try:
                                                    os.makedirs(os.path.dirname(filename))
                                                except OSError as exc: # Guard against race condition
                                                    if exc.errno != errno.EEXIST:
                                                        raise
                                                    print(exc)                                     
                                            with open(filename, 'wb') as f:
                                                f.write(payload) 
                        elif subpart.get_content_type() == 'image/png':
                            attach.append(subpart.get_payload(decode=True)) 
                            self.hasImage= True
                        else:
                            payload = subpart.get_payload(decode=True)
                            attach.append(payload)
                            if not subpart.get_filename():
                                continue
                            else:
                                filename = path+subpart.get_filename()
                                # Save the file.
                                if payload and filename:
                                    if not os.path.exists(os.path.dirname(filename)):
                                        try:
                                            os.makedirs(os.path.dirname(filename))
                                        except OSError as exc: # Guard against race condition
                                            if exc.errno != errno.EEXIST:
                                                raise
                                            print(exc)                                     
                                    with open(filename, 'wb') as f:
                                        f.write(payload)                                
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
                            if not os.path.exists(os.path.dirname(filename)):
                                try:
                                    os.makedirs(os.path.dirname(filename))
                                except OSError as exc: # Guard against race condition
                                    if exc.errno != errno.EEXIST:
                                        raise
                                    print(exc)                             
                            with open(filename, 'wb') as f:
                                f.write(payload)                     
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
                                    if not os.path.exists(os.path.dirname(filename)):
                                        try:
                                            os.makedirs(os.path.dirname(filename))
                                        except OSError as exc: # Guard against race condition
                                            if exc.errno != errno.EEXIST:
                                                raise
                                            print(exc) 
                                    try:
                                        with open(filename, 'wb') as f:
                                            f.write(payload)
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
                            if not os.path.exists(os.path.dirname(filename)):
                                try:
                                    os.makedirs(os.path.dirname(filename))
                                except OSError as exc: # Guard against race condition
                                    if exc.errno != errno.EEXIST:
                                        raise
                                    print(exc)                             
                            try:
                                with open(filename, 'wb') as f:
                                    f.write(payload)
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
            filename = "FINDMAIL/Plain text files/"+ str(count1)+".txt"
            body= "FINDMAIL/Plain text files/body/"+ str(count1)+".txt"
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print(exc)        
            if not os.path.exists(os.path.dirname(body)):
                try:
                    os.makedirs(os.path.dirname(body))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print(exc)
            
            with open(filename, "w") as f: #Write message to single file
                f.write(str(message) )   
            f.close()
            
            with open(body, "w") as b: #Write body to single file
                #print message.get_content_type()
                #if message.is_multipart():
                    #content = ''.join(part.get_payload(decode=True) for part in message.get_payload())
                #else:
                    #content = message.get_payload(decode=True)            
                b.write(str(self.getbody(message) ))         
            b.close()
            #print getbody(message)
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
            """Convert date-time to usable time format"""
            #REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
            #varTime= (time.mktime(email.utils.parsedate(msgTime)) +time.timezone - REMOTE_TIME_ZONE_OFFSET)            
            #print "Time: ", time.strftime('%Y/%m/%d --- Time %H:%M:%S', time.localtime(varTime))
            strBody= str("""""")
            strBody = strBody+str(self.getbody(message))
            strBody= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(strBody))
            """Derive attachment part of HTML File"""
            msgATT="""<p>ATTACHMENTS:</p>"""
            embedHTML=""""""
            for att in self.get_undecoded_attachment(message, "FINDMAIL/HTML files/Attachments/"+ str(count2)+"/"):
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
            filename = "FINDMAIL/HTML files/"+ str(count2)+".html"
            
            newpath = "All.txt"
            if count2==1:
                open(newpath, 'w').close() 
                with open(newpath, "a") as g: #Write message to single file
                    g.write(filename+"\n" )   
                g.close()                                
            else:
                with open(newpath, "a") as g: #Write message to single file
                    g.write(filename+"\n" )   
                g.close()                                            
            
            if count2==1:
                self.clearFolder("FINDMAIL/HTML files/")            
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print(exc) 
                    
            with open(filename, "w") as f: #Write message to single file
                f.write(msgHTML )   
            f.close() 
            count2= count2+1
            
    """-Prints to JSON files but some attachments are an issue eg. video, pictures and audio"""
    def printToJSONFiles(self,path):
        count3=1;
        mbox = mailbox.mbox(path)
        for message in mbox.iteritems():  
            """Get from, to and subject field from email"""
            self.data['from']= message["from"]
            self.data['to']= message["to"]
            self.data['subject']= message["subject"]
            self.data['message-id']= message["message-id"]
            self.data['date']= message["date"]  
            if self.getbody(message):
                self.data['body']= self.getbody(message)
            else:
                self.data['body']= ""
            self.data['attachment']= self.getAttachment(message)
            json_data = json.dumps(self.data, ensure_ascii=False)
            filename = "FINDMAIL/JSON files/"+ str(count3)+".json"
            
            
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print(exc) 
        
            with open(filename, "w") as f: #Write message to single file
                f.write(json_data )   
            f.close()  
            count3= count3+1            
        
       #json_val = json.load(open('file.json'))
       
    """Create directory of all emails in mbox as XML files"""
    def printToXMLFiles(self, path):
        #Set default encoding to UTF-8 so system can parse email body
        reload(sys)  
        sys.setdefaultencoding('utf8')        
        
        count4=1;
        mbox = mailbox.mbox(path)
        for message in mbox:  
            """Get from, to and subject fields etc. from email"""  
            root = ET.Element("doc")   
            ET.SubElement(root, "from", name="FROM").text = message["from"]
            ET.SubElement(root, "to", name="TO").text = message["to"]
            ET.SubElement(root, "subject", name="SUBJECT").text = message["subject"]
            ET.SubElement(root, "message-id", name="MESSAGE-ID").text = message["message-id"]        
            ET.SubElement(root, "date", name="DATE").text = message["date"]
            if self.getbody(message):
                ET.SubElement(root, "body", name="BODY").text = self.getbody(message).encode('utf-8')
            else:
                ET.SubElement(root, "body", name="BODY").text =""
            
            """Derive attachment part of XML File"""
            attachCount=0
            for att in self.get_undecoded_attachment(message):
                if att==None:
                    pass #Skip all attachments for that email if it has attachments 
                elif self.hasImage==True: 
                    pass #Cannot encode image file as UTF-8
                else:
                    ET.SubElement(root, "attachment"+str(attachCount), name="ATTACHMENT"+ str(attachCount)).text =att.as_string()
                attachCount= attachCount+1  
            
            self.hasImage= False #Re-initialise to false
            
            filename = "FINDMAIL/XML files/"+ str(count4)+".xml"
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print(exc)        
                    
            tree = ET.ElementTree(root)
            tree.write(filename) 
            count4=count4+1            
    
    @staticmethod
    def main(self,path):
        
        """FINDMAIL/mailboxes/mbox/test.mbox"""
        #mbox = mailbox.mbox(path)       
        #self.printToTextFiles(path)
        self.printToHTMLFiles(path)
        #self.printToJSONFiles(path)
        #self.printToXMLFiles(path) 

class parseMDIR:
    def __init__(self, content = None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8" # output encoding 
        self.hasImage= False
        
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
        print(len(message.get_payload()))
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
                                    if not os.path.exists(os.path.dirname(filename)):
                                        try:
                                            os.makedirs(os.path.dirname(filename))
                                        except OSError as exc: # Guard against race condition
                                            if exc.errno != errno.EEXIST:
                                                raise
                                            print(exc) 
                                    try:
                                        with open(filename, 'wb') as f:
                                            f.write(payload)
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
                            if not os.path.exists(os.path.dirname(filename)):
                                try:
                                    os.makedirs(os.path.dirname(filename))
                                except OSError as exc: # Guard against race condition
                                    if exc.errno != errno.EEXIST:
                                        raise
                                    print(exc)                            
                            try:
                                with open(filename, 'wb') as f:
                                    f.write(payload)
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
    
    """For emails that comply with RFC 2822"""
    def printToHTMLfiles(self,file):
        """-Is it over-writing files of same name eg 1,2?"""
        mailbox.Maildir.colon = '!' #Another character to use as colon in mdir files
        mdir =mailbox.Maildir(file, factory=None)
        #print file
        count2=1
        for message in mdir:
            #message = mailbox.mboxMessage(file) # has to comply with RFC 2822
            #print message
            """Get from, to and subject field etc from email"""
            msgFrom= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["from"]))
            msgTo= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["to"]))
            msgSubject= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["subject"]))
            msgID= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["message-id"]))
            msgTime= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["date"]))
            
            #"""Convert date-time to usable time format"""
            #print "From: ", msgFrom
            #print "To: ", msgTo
            #print "Subject: ", msgSubject
            #print "Message-ID: ", msgID
            #print "Date-time: ", msgTime 
            
            #REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
            #varTime= (time.mktime(email.utils.parsedate(msgTime)) +time.timezone - REMOTE_TIME_ZONE_OFFSET)            
            #print "Time: ", time.strftime('%Y/%m/%d --- Time %H:%M:%S', time.localtime(varTime)) 
            strBody=u""""""
            strBody = str(self.getbody(message))   
            
            """Derive attachment part of HTML File"""
            msgATT="""<p>ATTACHMENTS:</p>"""
            embedHTML=""""""
            for att in self.get_undecoded_attachment(message, "FINDMAIL/HTML files/Attachments/"+ str(count2)+"/"):
                content_type=att.get_content_type()
                #print content_type
                strAttach= str(att)
                if content_type=='text/html':
                    embedHTML= embedHTML+att.get_payload(decode=True) 
                elif not att.get_filename():
                    continue                
                else:
                    #print att.get_filename()
                    decodeFilename= self.decodeHeader(att.get_filename())
                    msgATT=msgATT+ """<p><a target= "_blank" href= "Attachments/ """+ str(count2)+"""/"""+decodeFilename+""" "><img src="Attachments/ """+ str(count2)+"""/"""+att.get_filename()+""" " alt= " """+ decodeFilename+ """ " style="width:150px"></a></p>"""
            msgHTML=self.createHTMLString(count2, msgFrom, msgTo, msgSubject, msgTime, strBody, embedHTML, msgATT)
            
            """File paths"""
            filename = os.path.join("FINDMAIL/PURE MDIR HTML files/", str(count2)+".html")
            newpath= "All.txt"
            if count2==1:
                open(newpath, 'w').close() 
                with open(newpath, "a") as g: #Write message to single file
                    g.write(filename+"\n" )   
                g.close()                                
            else:
                with open(newpath, "a") as g: #Write message to single file
                    g.write(filename+"\n" )   
                g.close() 
                
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print(exc) 
                    
            with open(filename, "w") as f: #Write message to single file
                f.write(msgHTML )   
            f.close()  
            count2= count2+1
    
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
                
    """Other type refers to maildirs that do not have the traditional
    new, cur and tmp folders. For emails that comply with RFC 2822"""
    def otherTypePrintToHTMLfiles(self,path):
        count5=1;
        for dirname, subdirs, files in os.walk(path):
            for name in files:               
                sublist= dirname.split("\\")
                subdir=sublist[len(sublist)-1]
                pathlist=path.split("/")
                maindir= pathlist[len(pathlist)-1]                
                fullname = os.path.join(dirname, name)
                with open(fullname, 'r') as myfile:
                    text=myfile.read()  #.replace('\n', '')  to remove newline
                message=  email.message_from_string(text)
                msgFrom= message["from"]
                msgTo= message["to"]
                msgSubject= message["subject"]
                msgID= message["message-id"]
                msgTime= message["date"]
                #strBody = str(self.getbody(message))
                #"""Derive attachment part of HTML File"""  
                #msgATT=""""""
                #for att in self.getAttachment(message):
                    #strAttach= str(att)
                    #msgATT=msgATT+ """<p>"""+strAttach+"""</p>"""
                #if msgATT=="""""":
                    #msgATT="""<p> NO ATTACHMENTS</p>"""   
                #"""Create html message"""
                #msgHTML = """<html>
                #<head> FINDMAIL</head>
                #<body>
                #<p id= FROM>"""+msgFrom +""" </p>
                #<p id= SUBJECT>"""+msgSubject+"""</p>
                #<p id= TO>"""+msgTo+"""</p>
                #<p id= MESSAGE-ID>"""+msgID+"""</p>
                #<p id= DATE-TIME>"""+msgTime+"""</p>
                #<p id= BODY >"""+ strBody+"""</p>
                #"""+msgATT+"""</body> 
                #</html>"""        
                
                strBody=""""""
                strBody = str(self.getbody(message))   
                
                """Derive attachment part of HTML File"""
                msgATT="""<p>ATTACHMENTS:</p>"""
                embedHTML=""""""
                for att in self.get_undecoded_attachment(message, "FINDMAIL/HTML files/Attachments/"+ str(count5)+"/"):
                    content_type=att.get_content_type()
                    #print content_type
                    strAttach= str(att)
                    if content_type=='text/html':
                        embedHTML= embedHTML+att.get_payload(decode=True) 
                    elif not att.get_filename():
                        continue                
                    else:
                        #print att.get_filename()
                        msgATT=msgATT+ """<p><a target= "_blank" href= "../Attachments/"""+ str(count5)+"""/"""+att.get_filename()+""" "><img src=" ../Attachments/"""+ str(count5)+"""/"""+att.get_filename()+""" " alt= " """+ att.get_filename()+ """ " style="width:150px"></a></p>"""
                        
                msgHTML=self.createHTMLString(count5, msgFrom, msgTo, msgSubject, msgTime, strBody, embedHTML, msgATT)                                   
                        
                """File paths"""
                filename = os.path.join("FINDMAIL/HTML files/",subdir, str(count5)+".html")
                newpath= "All.txt"
                if count5==1:
                    open(newpath, 'w').close() 
                    with open(newpath, "a") as g: #Write message to single file
                        g.write(filename+"\n" )   
                    g.close()                                
                else:
                    with open(newpath, "a") as g: #Write message to single file
                        g.write(filename+"\n" )   
                    g.close() 
                    
                
                if count5==1:
                    self.clearFolder("FINDMAIL/HTML files/")
                if not os.path.exists(os.path.dirname(filename)):
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                        print(exc)                    
                    
                with open(filename, "w") as f: #Write message to single file
                    f.write(msgHTML )   
                f.close()  
                count5= count5+1                
                
    def printToJSONFiles(self,path):
        count3=1;
        for dirname, subdirs, files in os.walk(path):
            count=1
            for name in files:
                sublist= dirname.split("\\")
                subdir=sublist[len(sublist)-1]
                pathlist=path.split("/")
                maindir= pathlist[len(pathlist)-1]                
                fullname = os.path.join(dirname, name)
                with open(fullname, 'r') as myfile:
                    text=myfile.read()  #.replace('\n', '')  to remove newline
                message=  email.message_from_string(text)                
                """Get from, to and subject field etc.from email"""
                self.data['folder']= subdir
                self.data['from']= message["from"]
                self.data['to']= message["to"]
                self.data['subject']= message["subject"]
                self.data['message-id']= message["message-id"]
                self.data['date']= message["date"]  
                if self.getbody(message):
                    self.data['body']= self.getbody(message)
                else:
                    self.data['body']= ""
                self.data['attachment']= self.getAttachment(message)
                json_data = json.dumps(self.data, ensure_ascii=False)
                filename = "FINDMAIL/MDIR JSON files/"+ str(count3)+".json"
                if not os.path.exists(os.path.dirname(filename)):
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                        print(exc) 
            
                with open(filename, "w") as f: #Write message to single file
                    f.write(json_data )   
                f.close()  
                count3= count3+1                  
              
            
    """Create directory of all emails in mdir as XML files. 
    Specify path to mdir directory"""
    def printToXMLFiles(self, path):
        #Set default encoding to UTF-8 so system can parse email body
        reload(sys)  
        sys.setdefaultencoding('utf8')   
        count4=1
        for dirname, subdirs, files in os.walk(path):
            for name in files:
                sublist= dirname.split("\\")
                subdir=sublist[len(sublist)-1]
                pathlist=path.split("/")
                maindir= pathlist[len(pathlist)-1]
                filename = os.path.join(dirname, name)
                fullname = os.path.join("FINDMAIL/XML files/"+maindir+"/"+subdir, str(count4)+".xml")
                if not os.path.exists(os.path.dirname(fullname)):
                    try:
                        os.makedirs(os.path.dirname(fullname))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                        print(exc) 
                data=""
                with open(filename, 'r') as myfile:
                    data=myfile.read()  #.replace('\n', '')  to remove newline
                message=  email.message_from_string(data)
                root = ET.Element("doc")
                ET.SubElement(root, "from", name="FROM").text = message["from"]
                ET.SubElement(root, "to", name="TO").text = message["to"]
                ET.SubElement(root, "subject", name="SUBJECT").text = message["subject"]
                ET.SubElement(root, "message-id", name="MESSAGE-ID").text = message["message-id"]        
                ET.SubElement(root, "date", name="DATE").text = message["date"]
                if self.getbody(message):
                    ET.SubElement(root, "body", name="BODY").text = self.getbody(message).encode('utf-8')
                else:
                    ET.SubElement(root, "body", name="BODY").text =""
                self.hasImage= False #Re-initialise to false   
                
                tree = ET.ElementTree(root)
                tree.write(fullname)
                count4= count4+1
            
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
        
    @staticmethod        
    def main(self, path):
        """FINDMAIL/mailboxes/maildir/test1"""
        #self.isPureMaildir(args.path)
        #self.printToHTMLfiles("FINDMAIL/mailboxes/maildir/test1")
        #self.printToXMLFiles("FINDMAIL/mailboxes/maildir/test1")
        self.otherTypePrintToHTMLfiles(args.path)
        #self.printToJSONFiles("FINDMAIL/mailboxes/maildir/test1")
        
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