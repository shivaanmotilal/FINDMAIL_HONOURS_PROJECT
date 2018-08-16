// in-browser javascript IR system
// hussein suleman
// 26 october 2006

var query;
var terms;
var prefix;
var index;
var accum;
var filenames;
var filetitles;
var filesender;
var filesubject;
var fileDate;
function dosearch (aprefix)
{  //alert(aprefix);
	//console.log(aprefix);
   prefix = aprefix;

   //split query into terms and split out spaces
   query = document.forms["search"].elements["search"].value;
    //console.log(query);
   query = query.toLowerCase ();
   query = query.replace (/['"_\.]/g, " ");
   query = query.replace (/^ +/, "");
   query = query.replace (/ +$/, "");

   //turn extended unicode characters into simple numbers
   var i;
   var j = query.length;
   var newquery = '';
   for ( i=j-1; i>=0; i-- )
   {
      var achar = query.charAt (i);
      if (achar.match(/[a-zA-Z0-9]/))
      {
         newquery = achar+newquery;
      }
      else
      {
         //newquery = '_'+query.charCodeAt (i)+'_'+newquery;
      }
   }
   terms = newquery.split (/ +/);
   console.log(terms[0]);
//    
  // create array
   accum = new Array();
   filenames = new Array();
   filetitles = new Array();
   filesender= new Array();
   filesubject= new Array();
   fileDate= new Array();
    
   //read term frequency files
   for ( var i=0; i<terms.length; i++ )
   {
      var http_request = false;
      if (window.XMLHttpRequest) 
      { // Mozilla, Safari, ...
         http_request = new XMLHttpRequest();
         if (http_request.overrideMimeType) 
         {
            http_request.overrideMimeType('text/xml');
         }
      } 
      else if (window.ActiveXObject) 
      { // IE
         try {
            http_request = new ActiveXObject("Msxml2.XMLHTTP");
         } catch (e) {
            try {
               http_request = new ActiveXObject("Microsoft.XMLHTTP");
            } catch (e) {}
         }
      }

      if (!http_request) 
      {
         alert('Giving up :( Cannot create an XMLHTTP instance');
         return false;
      }

      //create and submit request
      http_request.open('GET',"index/"+terms[i]+".xml", false);
      try {
         http_request.send(null);
      }
      catch (e) {
         continue;
      }

      var index = http_request.responseXML;
      if (!index.documentElement && http_request.responseStream) 
      {
         index.load(http_request.responseStream);
      }

      var wordlist = index.getElementsByTagName ('tf');
      var df = wordlist.length;
      for ( var j=0; j<wordlist.length; j++ )
      {
         var value = wordlist.item(j).firstChild.data;
         var fileid = wordlist.item(j).getAttribute ('id');
         filenames[fileid] = wordlist.item(j).getAttribute ('file');
         filetitles[fileid] = wordlist.item(j).getAttribute ('title');
          
         filesender[fileid]=wordlist.item(j).getAttribute ('sender');
         filesubject[fileid]=wordlist.item(j).getAttribute ('subject');
         fileDate[fileid]=wordlist.item(j).getAttribute ('Date');
         if (isNaN (accum[fileid]))
            accum[fileid] = 0;
         accum[fileid] += parseFloat(value) / df;
      }
   }

   // selection sort based on weights, ignoring zero values
   var ranked = new Array();
   var weight = new Array();
   var k = 0;
   for ( var i=0; i<accum.length; i++ )
   {
      if (! isNaN (accum[i]))
      {
         ranked[k] = i;
         weight[k] = accum[i];
         k++;
      }
   }
   for ( var i=0; i<ranked.length; i++ )
   {
      var max = i;
      for ( var j=i+1; j<ranked.length; j++ )
         if (weight[j] > weight[max])
            max = j;
      if (max != i)
      {
         var swap = weight[i];
         weight[i] = weight[max];
         weight[max] = swap;
         swap = ranked[i];
         ranked[i] = ranked[max];
         ranked[max] = swap;
      }
   }
//   
//   //output results page
//   window.name = 'mainwin';
//   var resultwin = window.open ('', 'searchwindow', 'width=600,height=700,resizable=yes,scrollbars=yes,status=yes');
//   resultwin.document.open();
//   resultwin.focus();
//   resultwin.document.write ('<html><head><title>Search Results</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/></head><body>');
//   resultwin.document.write ('<h1>Search Results</h1><hr/>');
//   resultwin.document.write ('<p>Query: '+query+'</p><hr/>');
//   if (ranked.length > 0)
//   {
//      resultwin.document.write ('<ol>');
//      for ( var i=0; i<ranked.length; i++ )
//      {
//         resultwin.document.write ('<li><b><a href="'+prefix+filenames[ranked[i]]+'" target="'+resultwin.opener.name+'">'+filetitles[ranked[i]]+'</a></b><br/><i>'+filenames[ranked[i]]+'</i></li>');
//      }
//      resultwin.document.write ('</ol>');
//   }
//   else
//   {
//      resultwin.document.write ('<h2>No matching pages.</h2>');
//   }
//   resultwin.document.write ('</body></html>');
//   resultwin.document.close();
//  // call add item actually
//addItem(sender,email_subject,html_filePath,Date);
if (ranked.length > 0){
     for ( var i=0; i<ranked.length; i++ )
          {
         addItem(filesender[ranked[i]],filesubject[ranked[i]],filenames[ranked[i]],fileDate[ranked[i]]);
          }
}
else{
    // tell the user the is  no match.
}

}
 