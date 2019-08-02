
console.log('helloworld');

// const form=document.querySelector('.exl');

function showResult(str) {
  if (str.length==0) {
    document.getElementById("livesearch").innerHTML="";
    document.getElementById("livesearch").style.border="0px";
    return;
  }
  if (window.XMLHttpRequest) {
    // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  } else {  // code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  xmlhttp.onreadystatechange=function() {
    if (this.readyState==4 && this.status==200) {
      document.getElementById("livesearch").innerHTML=this.responseText;
      document.getElementById("livesearch").style.border="1px solid #A5ACB2";
    }
  }
  xmlhttp.open("GET","livesearch.php?q="+str,true);
  xmlhttp.send();
}









function showResult(str){
  if (str.length==0) {
    document.getElementById("livesearch").innerHTML="";
    document.getElementById("livesearch").style.border="0px";
    return;
}
}





var form = document.getElementsByClassName('exl');

// document.addEventListener('click', (event)=> {
//   console.log(event);
// });

form.addEventListener('click', (event)=> {
  // document.getElementById('').innerHTML= 'The emergency services at that location are not in the database. Search again'
  console.log(event);

});


//query call eventual consistency
//key.getkey strong consistency


//if search has no results, leave message
