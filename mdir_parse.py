#Shivaan Motilal
#Programme that parses Maildir Mailboxes with MIME Messages to create indices

#!/usr/bin/env python

## Open Sourced by - FINDMAIL App, UCT
## (c) 2018 FINDMAIL (UCT)
## https://github.com/FINDMAIL

import mailbox
import argparse
import os
import errno
import email.utils
import xml.etree.cElementTree as ET

"""imports for JSON Conversion"""
import sys, urllib2, email, re, csv, StringIO, base64, json, datetime, pprint
from optparse import OptionParser

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
        #print message #Does not comply with RFC 2822 is rfc 822
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
        print len(message.get_payload())
        if message.is_multipart():
            for part in message.walk():
                if part.is_multipart():
                    for subpart in part.walk():
                        if subpart.get_content_type() == 'text/html': #can also use .get_filename() to get ...
                            attach.append(subpart.get_payload(decode=True))
                        if subpart.get_content_type() == 'image/png':
                            attach.append(subpart.get_payload(decode=True))  
                            self.hasImage= True                            
                elif part.get_content_type() == 'text/plain':
                    continue
        elif message.get_content_type() == 'text/plain':
            #Do nothing
            print "no attachment"
        return attach   
        
        #attachments = []
        #parts = []
        #for part in self.msg.walk():
            #if part.is_multipart():
                #continue
    
            #content_disposition = part.get("Content-Disposition", None)
            #if content_disposition:
                ## we have attachment
                #r = filename_re.findall(content_disposition)
                #if r:
                    #filename = sorted(r[0])[1]
                #else:
                    #filename = "undefined"
    
                #a = { "filename": filename, "content": base64.b64encode(part.get_payload(decode = True)), "content_type": part.get_content_type() }
                #attachments.append(a)
            #else:
                #try:
                    #p = { "content_type": part.get_content_type(), "content": unicode(part.get_payload(decode = 1), self._get_content_charset(part, "utf-8"), "ignore").encode(self.encoding), "headers": self._get_part_headers(part) }
                    #parts.append(p)
                    #self.raw_parts.append(part)
                #except LookupError:
                    ## Sometimes an encoding isn't recognised - not much to be done
                    #pass
      
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
            """Get from, to and subject field from email"""
            msgFrom= message["from"]
            msgTo= message["to"]
            msgSubject= message["subject"]
            msgID= message["message-id"]
            msgTime= message["date"]
            
            #"""Convert date-time to usable time format"""
            #print "From: ", msgFrom
            #print "To: ", msgTo
            #print "Subject: ", msgSubject
            #print "Message-ID: ", msgID
            #print "Date-time: ", msgTime 
            
            #REMOTE_TIME_ZONE_OFFSET = -2 * 60 * 60  #Take into account local time difference
            #varTime= (time.mktime(email.utils.parsedate(msgTime)) +time.timezone - REMOTE_TIME_ZONE_OFFSET)            
            #print "Time: ", time.strftime('%Y/%m/%d --- Time %H:%M:%S', time.localtime(varTime)) 
            strBody = str(self.getbody(message))   
            
            """Derive attachment part of HTML File"""  
            msgATT=""""""
            for att in self.getAttachment(message):
                strAttach= str(att)
                msgATT=msgATT+ """<p>"""+strAttach+"""</p>"""
            #print getAttachment(message)
            
            if msgATT=="""""":
                msgATT="""<p> NO ATTACHMENTS</p>"""
            
            #print msgATT
            
            """Create html message"""
            msgHTML = """<html>
            <head> FINDMAIL</head>
            <body>
            <p id= FROM>"""+msgFrom +""" </p>
            <p id= SUBJECT>"""+msgSubject+"""</p>
            <p id= TO>"""+msgTo+"""</p>
            <p id= MESSAGE-ID>"""+msgID+"""</p>
            <p id= DATE-TIME>"""+msgTime+"""</p>
            <p id= BODY >"""+ strBody+"""</p>
            """+msgATT+"""</body> 
            </html>"""        
            
            """File paths"""
            filename = "FINDMAIL/MDIR HTML indices/"+ str(count2)+".html"
            
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                    print exc 
                    
            with open(filename, "w") as f: #Write message to single file
                f.write(msgHTML )   
            f.close()  
            count2= count2+1
            
    """Other type refers to maildirs that do not have the traditional
    new, cur and tmp folders. For emails that comply with RFC 2822"""
    def otherTypePrintToHTMLfiles(self,path):
        for dirname, subdirs, files in os.walk(path):
            print (dirname)
            print ('\tDirectories:', subdirs)
            count=1
            for name in files:
                fullname = os.path.join(dirname, name)
                print ()
                print ('***', fullname)
                #print (open(fullname).read())
                self.printToHTMLfiles(count,fullname)
                count=count+1
                print ('*' * 40)        
        
    """TO-DO: Prints to JSON files and stores all mails as a list"""
    def printToJSONfiles(self,count2,file):
        data = {}
        data['key'] = 'value'
        json_data = json.dumps(data)    
        """-Is it over-writing files of same name eg 1,2?"""
        mailbox.Maildir.colon = '!' #Another character to use as colon in mdir files
        mdir =mailbox.Maildir(file, factory=None)
        #print file
        for message in mdir:
            #message = mailbox.mboxMessage(file) # has to comply with RFC 2822
            #print message
            """Get from, to and subject field from email"""
            msgFrom= message["from"]
            msgTo= message["to"]
            msgSubject= message["subject"]
            msgID= message["message-id"]
            msgTime= message["date"]
            
    """Create directory of all emails in mdir as XML files. 
    Specify path to mdir directory"""
    def printToXMLFiles(self, path):
        #Set default encoding to UTF-8 so system can parse email body
        reload(sys)  
        sys.setdefaultencoding('utf8')   
        count4=1
        for dirname, subdirs, files in os.walk(path):
            for name in files:
                print dirname
                sublist= dirname.split("\\")
                subdir=sublist[len(sublist)-1]
                pathlist=path.split("/")
                maindir= pathlist[len(pathlist)-1]
                print subdir
                filename = os.path.join(dirname, name)
                fullname = os.path.join("FINDMAIL/XML files/"+maindir+"/"+subdir, str(count4)+".xml")
                print fullname
                if not os.path.exists(os.path.dirname(fullname)):
                    try:
                        os.makedirs(os.path.dirname(fullname))
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                        print exc 
                data=""
                with open(filename, 'r') as myfile:
                    data=myfile.read()  #.replace('\n', '')  to remove newline
                message=  email.message_from_string(data)
                root = ET.Element("doc")
                #doc = ET.SubElement(root, "doc")
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
                #with open(fullname, "w") as f: #Write message to single file
                    #f.write(msgHTML )   
                #f.close()                      
                
        #count4=1;
        #for message in mbox:  
            ##print message
            #"""Get from, to and subject fields etc. from email"""  
            #root = ET.Element("doc")
            ##doc = ET.SubElement(root, "doc")
            #ET.SubElement(root, "from", name="FROM").text = message["from"]
            #ET.SubElement(root, "to", name="TO").text = message["to"]
            #ET.SubElement(root, "subject", name="SUBJECT").text = message["subject"]
            #ET.SubElement(root, "message-id", name="MESSAGE-ID").text = message["message-id"]        
            #ET.SubElement(root, "date", name="DATE").text = message["date"]
            #if self.getbody(message):
                #ET.SubElement(root, "body", name="BODY").text = self.getbody(message).encode('utf-8')
            #else:
                #ET.SubElement(root, "body", name="BODY").text =""
            #self.hasImage= False #Re-initialise to false
            #filename = "FINDMAIL/XML files/"+ str(count4)+".xml"
            #if not os.path.exists(os.path.dirname(filename)):
                #try:
                    #os.makedirs(os.path.dirname(filename))
                #except OSError as exc: # Guard against race condition
                    #if exc.errno != errno.EEXIST:
                        #raise
                    #print exc           
            #tree = ET.ElementTree(root)
            #tree.write(filename) 
            #count4=count4+1    
            
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
    def main(self):
        #for dirname, subdirs, files in os.walk('FINDMAIL/mailboxes/maildir/test1'):
            #print (dirname)
            #print ('\tDirectories:', subdirs)
            #count=1
            #for name in files:
                #fullname = os.path.join(dirname, name)
                #print ()
                #print ('***', fullname)
                ##print (open(fullname).read())
                #printToHTMLfiles(count,fullname)
                #count=count+1
                #print ('*' * 40) 
        print self.isPureMaildir("FINDMAIL/mailboxes/maildir/test1")
        #self.printToHTMLfiles("FINDMAIL/mailboxes/maildir/test1")
        self.printToXMLFiles("FINDMAIL/mailboxes/maildir/test1")

if __name__ == '__main__':
    maildir= parseMDIR()
    maildir.main(maildir)
