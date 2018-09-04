#Shivaan Motilal
#Programme to parse MBOX and Maildir Mailboxes
from __future__ import print_function, division
from __future__ import unicode_literals
from __future__ import absolute_import
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
import urllib2, email, csv, StringIO, base64, json, pprint
from optparse import OptionParser
import collections
from multiprocessing import Process
import urllib
import sys
#Check that version of python >= 2.7
major, minor, micro, releaselevel, serial = sys.version_info
if (major,minor) <= (2,6):
    # provide advice on getting version 2.7 or higher.
    print("You need need Python version > 2.7. Download from here: https://www.python.org/")
    sys.exit(2)
from sys import platform

class parseMbox:
    def __init__(self, content = None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8" # output encoding
        self.hasImage = False
        self.prePath= "FINDMAIL/HTML_files"
        self.strBody=""
        self.chainedmsg=[]
        self.attach=[]

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
    def getbody(self,message, path): #getting plain text 'email body'
        self.strBody = None
        self.chainedmsg=[]
        self.attach = []
        if message.is_multipart():
            for part in message.walk():
                #print part.get_content_type()
                if part.is_multipart():
                    for subpart in part.walk():
                        #print subpart.get_content_type()
                        if subpart.get_content_type() == 'text/plain':
                            self.strBody = subpart.get_payload(decode=True)
                            self.chainedmsg.append(self.strBody)
                        else:
                            #Must be an attachment
                            payload = subpart.get_payload(decode=True)
                            self.attach.append(subpart)
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
                    self.strBody = part.get_payload(decode=True)
                    self.chainedmsg.append(self.strBody)
                else:
                    # When decode=True, get_payload will return None if part.is_multipart()
                    # and the decoded content otherwise.
                    payload = part.get_payload(decode=True)
                    self.attach.append(part)
                    # Default filename can be passed as an argument to get_filename()
                    if not part.get_filename():
                        continue
                    else:
                        decodePart= self.decodePart(part.get_filename())
                        decodePart= self.decodeHeader(decodePart)
                        filename = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", decodePart)
                        filename = os.path.join(path, decodePart)
                        # Save the file.
                        self.attach.append(part)
                        if payload and filename:
                            self.createDirs(filename)
                            try:
                                self.append_to_file(filename,payload ,"wb")
                            except  IOError:
                                print('An error occured trying to read the file.')
        elif message.get_content_type() == 'text/plain':
            self.strBody = message.get_payload(decode=True)
            self.chainedmsg.append(self.strBody)
        return self.chainedmsg

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

    def createHTMLString(self, Count, From, To, Subject, Time, Body, Embedded, Attach, Cc):
        fullbody=""""""
        if Subject is None:
            Subject= """ """
        else:
           Subject= """<p class="subject_content"><b>Subject: </b>"""+Subject+"""</p> """
        if From is None:
            From= """ """
        else:
            From= """<pre  id="sender_content"><b>FROM:</b> """+From+"""</pre>"""
        if To is None:
            To= """ """
        else:
            To= """<p><b>To: </b>"""+To+"""</p>"""
        if Body==str(""""""):
            Body= """ """
        if Time is None:
            Time= """ """
        else:
            Time="""<pre id="datetime_content"><b>"""+Time+"""</b></pre>"""
        if Cc is None:
            Cc= """ """
        else:
            Cc= """<p><b>Cc: </b>"""+Cc+"""</p>"""
        if Body==[]:
            Body= str("""""")
        else:
            for body in Body:
                if body:
                    body= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(body))
                    fullbody= fullbody+"""<div class="middle_content">"""+body+"""</div>"""
                else:
                    fullbody= fullbody+""""""
        msgHTML= """<div class="content_content">
        <div class="Content_topNav">
            <div class="st_line">
               """+From+"""
                """+Time+"""
            </div>
            """+Subject+"""
            """+To+"""
            """+Cc+"""
            </div>
            """+fullbody+"""
            """+Embedded+"""</div>
            """+Attach+"""
        </div>"""
        return msgHTML

    """removes all xml files in current directory"""
    def removeXML(self):
        dir_name = os.getcwd()
        test = os.listdir(dir_name)

        for item in test:
            if item.endswith(".xml"):
                os.remove(os.path.join(dir_name, item))

    """-Prints emails to html files"""
    def printToHTMLFiles(self,path):
        reload(sys)  # Reload does the trick!
        sys.setdefaultencoding('UTF8')
        unsortedArray = []
        date={}
        #self.clearFolder(os.path.join("FINDMAIL","XML_files/"))
        count2=1;
        data= {}
        newpath="";
        formatTime=None
        mbox = mailbox.mbox(path)
        msgCC=""

        self.removeXML()
        if os.path.exists(os.path.join("FINDMAIL","XML_files")):
            #self.clearFolder(os.path.join("FINDMAIL","XML_files"))
            shutil.rmtree(os.path.join("FINDMAIL","XML_files"))
        for message in mbox:
            #print message
            """Get from, to and subject field etc from email"""
            if not message["cc"]:
                msgCC=""
            if not message["from"]:
                msgFrom="No Sender"
            else:
                msgFrom= re.sub('[<>]', '',re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["from"])))
                # print(msgFrom)
            if not message["to"]:
                msgTo= "No Receiver"
            else:
                msgTo= re.sub('[<>]', '',re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["to"])))
            if not message["subject"]:
                msgSubject="No Subject"
            else:
                msgSubject= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["subject"]))
            if not message["date"]:
                msgTime=""
            else:
                msgTime= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["date"]))
                """Convert date-time to usable time format"""
                REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
                varTime= (time.mktime(email.utils.parsedate(message["date"])) +time.timezone - REMOTE_TIME_ZONE_OFFSET)
                formatTime=  time.strftime('%Y/%m/%d %H:%M', time.localtime(varTime))
            chainBody= None
            chainBody = self.getbody(message, os.path.join("FINDMAIL/HTML_files/Attachments/"+ str(count2)+"/"))
            msgATT="""<div class="attachments_group">"""
            embedHTML=""""""
            for att in self.attach:
                content_type=att.get_content_type()
                #print content_type
                strAttach= str(att)
                if content_type=='text/html':
                    embedHTML= str(embedHTML)+str(att.get_payload(decode=True))
                elif not att.get_filename():
                    continue
                else:
                    if content_type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        file_image= "icons/word.jpeg"
                    elif content_type=="image/gif" or content_type=="image/gif" or content_type=="image/png":
                        file_image= "icons/image.jpeg"
                    elif content_type=="application/pdf":
                        file_image= "icons/pdf.jpeg"
                    elif "audio" in content_type:
                        file_image= "icons/audio.jpeg"
                    elif "video" in content_type:
                        file_image= "icons/video.jpeg"
                    else:
                        file_image=" "+self.prePath+"/Attachments/"+ str(count2)+"/"+att.get_filename()+""
                    # print(content_type)
                    #print att.get_filename()
                    decodeFilename= self.decodeHeader(att.get_filename())
                    msgATT=msgATT+ """
                    <a id ="attachmentItem" target="_blank" href=" """+self.prePath+"""/Attachments/"""+ str(count2)+"""/"""+decodeFilename+""" ">
                    <img src=" """+file_image+""" " alt=" """+ att.get_filename()+ """ " width="40" height="40">
                    <pre class="attachment_Name"><i>"""+ att.get_filename()+ """ &nbsp;</i></pre>
                    </a>"""
                    #<p><a target= "_blank" href= "Attachments/"""+ str(count2)+"""/"""+decodeFilename+""" "><img src="./icons/"""+ str(count2)+"""/"""+decodeFilename+""" " alt= " """+ att.get_filename()+ """ " style="width:150px"></a></p>"""
            msgATT=msgATT+"""</div>"""
            msgHTML=self.createHTMLString(count2, msgFrom, msgTo, msgSubject, formatTime, chainBody, embedHTML, msgATT, msgCC)

            """-File paths"""
            filename = os.path.join(self.prePath,str(count2)+".txt")

            """TO-DO REMOVE LATER- Adds to file All.txt"""
            newpath = "All.txt"
            if count2==1:
                open(newpath, 'w').close()
                self.append_to_file(newpath,filename+"\n","a" )
            else:
                self.append_to_file(newpath,filename+"\n","a")

            #NB: Comment Out these two lines on first time run Update- might not matter
            if count2==1:
                #self.clearFolder(self.prePath)
                shutil.rmtree(self.prePath)
            self.createDirs(filename)
            self.append_to_file(filename,msgHTML,"w")

            #XML PrintToFile
            root = ET.Element("doc")
            filepath=os.path.join("FINDMAIL/HTML_files/",str(count2)+".txt")
            ET.SubElement(root, "from", name="FROM").text = msgFrom.decode('utf-8','ignore').encode("utf-8")
            ET.SubElement(root, "to", name="TO").text = msgTo.decode('utf-8','ignore').encode("utf-8")
            ET.SubElement(root, "subject", name="SUBJECT").text = msgSubject
            ET.SubElement(root, "doc_id", name="DOC_ID").text =str(count2)
            date={ 'sender': msgFrom ,'subject': msgSubject,'id': str(count2),'file': filepath, 'date': str(formatTime)}
            unsortedArray.append(date)
            ET.SubElement(root, "date", name="DATE").text = formatTime
            if chainBody:
                ET.SubElement(root, "body", name="BODY").text = re.sub('[^A-Za-z0-9]+', ' ', self.strBody).encode('utf-8')
            else:
                ET.SubElement(root, "body", name="BODY").text =""
            #f for some reason file can not be decoded
            try:
                filename2 = os.path.join("FINDMAIL/XML_files/"+ str(count2)+".xml")
                self.createDirs(filename2)
                tree = ET.ElementTree(root)
                tree.write(filename2)
            except UnicodeDecodeError:
                root3 = ET.Element("doc")
                tree = ET.ElementTree(root3)
                self.createDirs(filename)
                tree.write(filename)
            
            count2= count2+1

        #Add to "All" directory
        data["Root"]= [os.path.join("All")]
        json_data = json.dumps(data)
        open('dir.json', 'w').close()
        self.append_to_file('dir.json',json_data,'a') #TO-D0 REMOVE Unecessary code last 4 lines
        open('dir.txt', 'w').close()
        self.append_to_file('dir.txt',"All",'a') #Add to dir.txt file
        #XML Processing
        sortedArrayDate = sorted(unsortedArray,key=lambda x: datetime.strptime(x['date'], '%Y/%m/%d %H:%M'), reverse=True)
        sortedArraySubject = sorted(unsortedArray,key=lambda x: x['subject'], reverse=False)
        sortedArraySender = sorted(unsortedArray,key=lambda x: x['sender'], reverse=False)
        rootDate = ET.Element("email")
        rootSubject= ET.Element("email")
        rootSender= ET.Element("email")
        leftoverDate=[]
        for item in sortedArrayDate:
            if str(item["date"]) :
                ET.SubElement(rootDate, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
            else:
                leftoverDate.append(item)
        for last in leftoverDate:
            ET.SubElement(rootDate, "tf",sender= last["sender"] ,subject= last["subject"],id= last["id"], file=str(last["file"]),date=str(last["date"]) ).text = str(0.001)
        leftoverSubject=[]
        for item in sortedArraySubject:
            if str(item["subject"]) :
                ET.SubElement(rootSubject, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
            else:
                leftoverSubject.append(item)
        for last in leftoverSubject:
            ET.SubElement(rootSubject, "tf",sender= last["sender"] ,subject= last["subject"],id= last["id"], file=str(last["file"]),date=str(last["date"]) ).text = str(0.001)
        leftoverSender=[]
        for item in sortedArraySender:
            if str(item["sender"]) :
                ET.SubElement(rootSender, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
            else:
                leftoverSender.append(item)
        for last in leftoverSender:
            ET.SubElement(rootSender, "tf",sender= last["sender"] ,subject= last["subject"],id= last["id"], file=str(last["file"]),date=str(last["date"]) ).text = str(0.001)
        tree2 = ET.ElementTree(rootDate)
        tree3 = ET.ElementTree(rootSubject)
        tree4 = ET.ElementTree(rootSender)

        filepath2=os.path.join("All_Date.xml")
        filepath3=os.path.join("All_Subject.xml")
        filepath4=os.path.join("All_From.xml")
        tree2.write(filepath2)
        tree3.write(filepath3)
        tree4.write(filepath4)
        print("Size of Archive: "+str(count2-1))
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

    @staticmethod
    def main(self,path):
        """Multiprocessing allowed here as if _name_='main' not applicable"""
        self.printToHTMLFiles(path)
        p = Process(target=self.printToHTMLFiles, args=( path,))
        p.start()
        p.join()

class parseMDIR:
    def __init__(self, content = None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8" # output encoding
        self.hasImage= False
        self.prePath= "FINDMAIL/HTML_files"
        self.inboxname= ""
        self.strBody=""
        self.chainedmsg=[]
        self.attach=[]

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
    def getbody(self,message, path): #getting plain text 'email body'
        self.strBody = None
        self.chainedmsg=[]
        self.attach = []
        if message.is_multipart():
            for part in message.walk():
                #print part.get_content_type()
                if part.is_multipart():
                    for subpart in part.walk():
                        #print subpart.get_content_type()
                        if subpart.get_content_type() == 'text/plain':
                            self.strBody = subpart.get_payload(decode=True)
                            self.chainedmsg.append(self.strBody)
                        else:
                            #Must be an attachment
                            payload = subpart.get_payload(decode=True)
                            self.attach.append(subpart)
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
                    self.strBody = part.get_payload(decode=True)
                    self.chainedmsg.append(self.strBody)
                    # #TO-DO!!!!- Verify the below line does something
                    # self.attach.append(subpart) #part of attachment method
                else:
                    # When decode=True, get_payload will return None if part.is_multipart()
                    # and the decoded content otherwise.
                    payload = part.get_payload(decode=True)
                    self.attach.append(part)
                    # Default filename can be passed as an argument to get_filename()
                    if not part.get_filename():
                        continue
                    else:
                        decodePart= self.decodePart(part.get_filename())
                        decodePart= self.decodeHeader(decodePart)
                        filename = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", decodePart)
                        filename = os.path.join(path, decodePart)
                        # Save the file.
                        self.attach.append(part)
                        if payload and filename:
                            self.createDirs(filename)
                            try:
                                self.append_to_file(filename,payload ,"wb")
                            except  IOError:
                                print('An error occured trying to read the file.')
        elif message.get_content_type() == 'text/plain':
            self.strBody = message.get_payload(decode=True)
            self.chainedmsg.append(self.strBody)
        return self.chainedmsg

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

    def createHTMLString(self, Count, From, To, Subject, Time, Body, Embedded, Attach, Cc):
        fullbody=""""""
        if Subject is None:
            Subject= """ """
        else:
           Subject= """<p class="subject_content"><b>Subject: </b>"""+Subject+"""</p> """
        if From is None:
            From= """ """
        else:
            From= """<pre  id="sender_content"><b>FROM:</b> """+From+"""</pre>"""
        if To is None:
            To= """ """
        else:
            To= """<p><b>To: </b>"""+To+"""</p>"""
        if Body==str(""""""):
            Body= """ """
        if Time is None:
            Time= """ """
        else:
            Time="""<pre id="datetime_content"><b>"""+Time+"""</b></pre>"""
        if Cc is None:
            Cc= """ """
        else:
            Cc= """<p><b>Cc: </b>"""+Cc+"""</p>"""
        if Body==[]:
            Body= str("""""")
        else:
            for body in Body:
                if body:
                    body= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(body))
                    fullbody= fullbody+"""<div class="middle_content">"""+body+"""</div>"""
                else:
                    fullbody= fullbody+""""""
        msgHTML= """<div class="content_content">
        <div class="Content_topNav">
            <div class="st_line">
               """+From+"""
                """+Time+"""
            </div>
            """+Subject+"""
            """+To+"""
            """+Cc+"""
            </div>
            """+fullbody+"""
            """+Embedded+"""
            """+Attach+"""
        </div>"""
        return msgHTML

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

    """removes all xml files in current directory"""
    def removeXML(self):
        dir_name = os.getcwd()
        test = os.listdir(dir_name)

        for item in test:
            if item.endswith(".xml"):
                os.remove(os.path.join(dir_name, item))

    def xmlProcessFileUncreated(self,sortedArrayDate, sortedArraySubject, sortedArraySender, prevFolder):
        rootDate = ET.Element("email")
        rootSubject= ET.Element("email")
        rootSender= ET.Element("email")

        for item in sortedArrayDate:
            if str(item["date"]) :
                ET.SubElement(rootDate, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
        for item in sortedArraySubject:
            if str(item["subject"]) :
                ET.SubElement(rootSubject, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
        for item in sortedArraySender:
            if str(item["sender"]) :
                ET.SubElement(rootSender, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
        tree2 = ET.ElementTree(rootDate)
        tree3 = ET.ElementTree(rootSubject)
        tree4 = ET.ElementTree(rootSender)

        filepath2=os.path.join(prevFolder+"_Date.xml")
        filepath3=os.path.join(prevFolder+"_Subject.xml")
        filepath4=os.path.join(prevFolder+"_From.xml")

        tree2.write(filepath2)
        tree3.write(filepath3)
        tree4.write(filepath4)

    def xmlProcessFileCreated(self,sortedArrayDate, sortedArraySubject, sortedArraySender, prevFolder):
        with open(prevFolder+"_Date.xml", 'r') as myfile:
            text2=myfile.read()
        with open(prevFolder+"_Subject.xml", 'r') as myfile:
            text3=myfile.read()
        with open(prevFolder+"_From.xml", 'r') as myfile:
            text4=myfile.read()
        rootDate= ET.fromstring(text2)
        rootSubject= ET.fromstring(text3)
        rootSender= ET.fromstring(text4)
        for item in sortedArrayDate:
            if str(item["date"]) :
                ET.SubElement(rootDate, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
        for item in sortedArraySubject:
            if str(item["subject"]) :
                ET.SubElement(rootSubject, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
        for item in sortedArraySender:
            if str(item["sender"]) :
                ET.SubElement(rootSender, "tf",sender= item["sender"] ,subject= item["subject"],id= item["id"], file=str(item["file"]),date=str(item["date"]) ).text = str(0.001)
        tree2 = ET.ElementTree(rootDate)
        tree3 = ET.ElementTree(rootSubject)
        tree4 = ET.ElementTree(rootSender)

        filepath2=os.path.join(prevFolder+"_Date.xml")
        filepath3=os.path.join(prevFolder+"_Subject.xml")
        filepath4=os.path.join(prevFolder+"_From.xml")

        tree2.write(filepath2)
        tree3.write(filepath3)
        tree4.write(filepath4)

    """Other type refers to maildirs that do not have the traditional
    new, cur and tmp folders. For emails that comply with RFC 2822"""
    def otherTypePrintToHTMLfiles(self,path):
        reload(sys)  # Reload does the trick!
        sys.setdefaultencoding('UTF8')
        data= {}
        data = collections.OrderedDict(data)
        folder_lst=[]
        count5=1;
        firstpass=True;
        prevFolder=""
        unsortedArray=[]
        curr_folderpath= ""
        curr_foldername=""
        formatTime=None
        msgCC=None
        tree2=None
        self.removeXML()
        ##Actually recursively traverses file system even with for structure
        if os.path.exists(os.path.join("FINDMAIL","XML_files")):
            #self.clearFolder(os.path.join("FINDMAIL","XML_files"))
            shutil.rmtree(os.path.join("FINDMAIL","XML_files"))
        for dirname, subdirs, files in os.walk(path):
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
                specdirs= os.path.normpath(specpath).split(os.path.sep)
                with open(fullname, 'r') as myfile:
                    text=myfile.read()  #.replace('\n', '')  to remove
                message=  email.message_from_string(text)
                #print message
                """Get from, to and subject field etc from email"""
                if not message["cc"]:
                    msgCC="No CC"
                if not message["from"]:
                    msgFrom="No Sender"
                else:
                    msgFrom= re.sub('[<>]', '',re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["from"])))
                if not message["to"]:
                    msgTo= "No Receiver"
                else:
                    msgTo= re.sub('[<>]', '',re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["to"])))
                if not message["subject"]:
                    msgSubject="No Subject"
                else:
                    msgSubject= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["subject"]))
                if not message["date"]:
                    msgTime=""
                    formatTime= "1970/01/01 00:00"
                else:
                    msgTime= re.sub(r"(=\?.*\?=)(?!$)", r"\1 ",self.decodeHeader(message["date"]))
                    """Convert date-time to usable time format"""
                    REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
                    varTime= (time.mktime(email.utils.parsedate(message["date"])) +time.timezone - REMOTE_TIME_ZONE_OFFSET)
                    formatTime=  time.strftime('%Y/%m/%d %H:%M', time.localtime(varTime))
                Body= None
                Body = self.getbody(message,os.path.join("FINDMAIL/HTML_files/Attachments/"+ str(count5)+"/"))
                """Derive attachment part of HTML File"""
                msgATT="""<div class="attachments_group">"""
                embedHTML=""""""
                for att in self.attach:
                    content_type=att.get_content_type()
                    strAttach= str(att)
                    if content_type=='text/html':
                        embedHTML= str(embedHTML)+str(att.get_payload(decode=True))
                    elif not att.get_filename():
                        continue
                    else:
                        if content_type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                            file_image= "icons/word.jpeg"
                        elif content_type=="image/gif" or content_type=="image/gif" or content_type=="image/png":
                            file_image= "icons/image.jpeg"
                        elif content_type=="application/pdf":
                            file_image= "icons/pdf.jpeg"
                        elif "audio" in content_type:
                            file_image= "icons/audio.jpeg"
                        elif "video" in content_type:
                            file_image= "icons/video.jpeg"
                        else:
                            file_image=" "+self.prePath+"/Attachments/"+ str(count2)+"/"+att.get_filename()+""
                        # print(content_type)
                        #print att.get_filename()
                        decodeFilename= self.decodeHeader(att.get_filename())
                        msgATT=msgATT+ """
                        <a id ="attachmentItem" target="_blank" href=" """+self.prePath+"""Attachments/"""+ str(count5)+"""/"""+decodeFilename+""" ">
                        <img src=" """+file_image+""" " alt=" """+ att.get_filename()+ """ " width="40" height="40">
                        <pre class="attachment_Name"><i>"""+ att.get_filename()+ """ &nbsp;</i></pre>
                        </a>"""
                msgATT=msgATT+"""</div>"""
                msgHTML=self.createHTMLString(count5, msgFrom, msgTo.decode('utf-8','ignore').encode("utf-8"), msgSubject, msgTime, Body, embedHTML, msgATT, msgCC)
                """File paths"""
                filenamehtml = os.path.join(self.prePath,specpath, str(count5)+".txt")
                newpath= "All.txt"
                if count5==1:
                    open(newpath, 'w').close()
                    self.append_to_file(newpath, filenamehtml+'\n','a')
                else:
                    self.append_to_file(newpath, filenamehtml+'\n','a')

                 #NB: Comment Out these two lines on first time run
                if count5==1:
                    #self.clearFolder(self.prePath)
                    if os.path.exists(self.prePath):
                        shutil.rmtree(self.prePath)
                    open("dir.txt", 'w').close()
                self.createDirs(filenamehtml)
                self.append_to_file(filenamehtml,msgHTML,"w")

                #XML Processing
                splitspecpath = filter(lambda name: name.strip(), specdirs) #Removes empty spaces
                middlepath=",".join(splitspecpath)
                file = open("dir.txt")
                strings = file.read()

                if middlepath not in strings:
                    if not "."==middlepath: #if middlepath not current directory
                        self.append_to_file("dir.txt",middlepath+"\n",'a')
                file.close()

                for i in range(0,(len(splitspecpath))):
                    root = ET.Element(splitspecpath[i])
                    if((i+1)==(len(splitspecpath))):
                        curr_foldername=  ','.join(splitspecpath)
                        break
                    else:
                        data[splitspecpath[i]] = [splitspecpath[i+1]]

                filename = os.path.join("FINDMAIL/XML_files/",specpath, str(count5)+".xml")
                root2 = ET.Element("doc")
                ET.SubElement(root2, "path", name="PATH").text = filenamehtml
                if not msgFrom:
                    msgFrom= "No Sender"
                ET.SubElement(root2, "from", name="FROM").text = msgFrom.decode('utf-8','ignore').encode("utf-8")

                ET.SubElement(root2, "to", name="TO").text = msgTo.decode('utf-8','ignore').encode("utf-8")
                if not message["subject"]:
                    msgSubject="No Subject"
                else:
                    msgSubject= re.sub('[^A-Za-z0-9]+', ' ', msgSubject)
                ET.SubElement(root2, "subject", name="SUBJECT").text = msgSubject.decode('utf-8','ignore').encode("utf-8")
                ET.SubElement(root2, "doc_id", name="DOC_ID").text = str(count5)
                ET.SubElement(root2, "date", name="DATE").text = formatTime
                if(count5==1):
                    prevFolder=curr_foldername
                    date={ 'sender': msgFrom ,'subject': msgSubject,'id': str(count5),'file': filenamehtml, 'date': str(formatTime)}
                    unsortedArray.append(date)
                else:
                    #Continue  adding to dictionary if same folder
                    if(prevFolder==curr_foldername):
                        date={ 'sender': msgFrom ,'subject': msgSubject,'id': str(count5),'file': filenamehtml, 'date': str(formatTime)}
                        unsortedArray.append(date)
                    #Sort dictionary and add to xml
                    else:
                        #XML Sorting Processing
                        sortedArrayDate = sorted(unsortedArray,key=lambda x: datetime.strptime(x['date'], '%Y/%m/%d %H:%M'), reverse=True)
                        sortedArraySubject = sorted(unsortedArray,key=lambda x: x['subject'], reverse=False)
                        sortedArraySender = sorted(unsortedArray,key=lambda x: x['sender'], reverse=False)
                        unsortedArray=[]
                        #If the xml structure file was not created
                        if not os.path.exists(prevFolder+"_Date.xml") :
                            self.xmlProcessFileUncreated(sortedArrayDate, sortedArraySubject, sortedArraySender, prevFolder)
                            date={ 'sender': msgFrom ,'subject': msgSubject,'id': str(count5),'file': filenamehtml, 'date': str(formatTime)}
                            unsortedArray.append(date)
                            prevFolder=curr_foldername

                        #XML Structure file already created
                        else:
                            self.xmlProcessFileCreated(sortedArrayDate, sortedArraySubject, sortedArraySender, prevFolder)
                            date={ 'sender': msgFrom ,'subject': msgSubject,'id': str(count5),'file': filenamehtml, 'date': str(formatTime)}
                            unsortedArray.append(date)
                            prevFolder=curr_foldername
                
                try:
                    tree = ET.ElementTree(root2)
                    self.createDirs(filename)
                    tree.write(filename)
                except UnicodeDecodeError:
                    print("error")
                    print(msgTo.decode('utf-8','ignore').encode("utf-8"))
                    root3 = ET.Element("doc")
                    tree = ET.ElementTree(root3)
                    self.createDirs(filename)
                    tree.write(filename)
                count5= count5+1
        #Needs to be done one more time for last level
        if(prevFolder==curr_foldername):
            #XML Sorting Processing
            sortedArrayDate = sorted(unsortedArray,key=lambda x: datetime.strptime(x['date'], '%Y/%m/%d %H:%M'), reverse=True)
            sortedArraySubject = sorted(unsortedArray,key=lambda x: x['subject'], reverse=False)
            sortedArraySender = sorted(unsortedArray,key=lambda x: x['sender'], reverse=False)
            unsortedArray=[]
            #If the xml structure file was not created
            if not os.path.exists(prevFolder+"_Date.xml") :
                self.xmlProcessFileUncreated(sortedArrayDate, sortedArraySubject, sortedArraySender, prevFolder)
                prevFolder=curr_foldername
            #XML Structure file created
            else:
                self.xmlProcessFileCreated(sortedArrayDate, sortedArraySubject, sortedArraySender, prevFolder)
                prevFolder=curr_foldername
        json_data = json.dumps(collections.OrderedDict(data))
        open('dir.json', 'w').close()
        self.append_to_file('dir.json',json_data,'a')
        print("Size of Archive: "+str(count5-1))
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

    @staticmethod
    def main(self, path):
        """Multiprocessing allowed here as if _name_='main' not applicable"""
        alldir= os.path.normpath(path).split(os.path.sep) 
        self.inboxname= alldir[-1] #Getting the name of the maildir
        p = Process(target=self.otherTypePrintToHTMLfiles, args=( path,))
        p.start()
        p.join()

if __name__ == '__main__': #On windows, when multiprocessing is invoked this needs to hold
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="specify path to archive from home directory")
    args = parser.parse_args()
    if args.path[-5:]== ".mbox":
        mbox=parseMbox()
        if platform == "linux" or platform == "linux2":
            # linux
            p = Process(target=mbox.main, args=( mbox, args.path,))
            p.start()
            p.join()
        elif platform == "darwin":
            # OS X
            p = Process(target=mbox.main, args=( mbox, args.path,))
            p.start()
            p.join()
        elif platform == "win32": #Windows can't compile the multiprocessing module written in c, infinite recursion would occur
            # Windows...
            mbox.main(mbox, args.path)
       
    else:
        #TO-DO Put else clause if filepath does not exist
        maildir= parseMDIR()
        if platform == "linux" or platform == "linux2":
            # linux
            p = Process(target=maildir.main, args=( maildir, args.path,))
            p.start()
            p.join()
        elif platform == "darwin":
            # OS X
            p = Process(target=maildir.main, args=( maildir, args.path,))
            p.start()
            p.join()
        elif platform == "win32":
            # Windows...
            maildir.main(maildir, args.path)  
    print("--- %s seconds ---" % (time.time() - start_time))#Measure execution time of program
