/*=============================
            GLOBALS
  =============================*/
var winW,winH;
var renderer;
var stage;
var drawTarg;
var active=1;
var deactivate=false;

/*=============================
           INITIALIZE
  =============================*/
window.onload=loader;
window.onresize=resize;
window.onblur=function(){ deactivate=true; active=0; }
window.onfocus=function(){ active=1; }
document.onselectstart=function(){ return false; };
document.onunload=function(){
  send({x:0,y:0,l:0,r:0,k:0,req:0});
  alert("!");
}
//document.addEventListener("touchstart", touchstart, false);
//document.addEventListener("touchmove", touchmove, false);
//document.addEventListener("touchend", touchend, false);

function makeCanvas(append){
  c={};
  c.canv = document.createElement('canvas');  
  c.ctx=c.canv.getContext("2d");
  if(append) document.body.appendChild(c.canv);
  return c;
}

function loader(){
  initStage();
}

function resize(){
  winW=Math.floor(window.innerWidth);
  winH=Math.floor(window.innerHeight);

  renderer.width=800;
  renderer.height=480;
  renderer.style.left=winW/2-400+"px";
  renderer.style.top=winH/2-240+"px";
}

function initStage(){
  c=makeCanvas(true); renderer=c.canv; stage=c.ctx;
  drawTarg=stage;
  resize();
}


/*=============================
              ENGINE
  =============================*/
var img=new Image();
setInterval(function(){
  try{
    drawTarg.globalAlpha=.5;
    //img.src="/zerog/screenshot.png?t=" + new Date().getTime();
    img.src="/zerog/screenshot.jpg?t=" + new Date().getTime();
    img.onload=function(){
      drawTarg.drawImage(img,0,0);
    }
  }
  catch(e){}
},1000);

/*=============================
              MOUSE
  =============================*/

mx=0;
my=0;
ml=0;
mr=0;
kc=0;
document.onmousemove  =function(e){ 
  if(e.srcElement.tagName=="CANVAS"){
    mx=e.offsetX;
    my=e.offsetY;
  }
}

var share=1
setInterval(function(){ send({x:mx,y:my,l:ml,r:mr,k:kc,req:active*share}); if(active==-1) setTimeout("active=0",5000); kc=0; }, 500);

var ee=0;
document.onkeyup      =function(e){ kc=e.keyCode; }
document.onmousedown  =function(e){ if(e.srcElement.tagName!="CANVAS") return; if(e.button==0) ml=1; else mr=1; }
document.onmouseup    =function(e){ if(e.srcElement.tagName!="CANVAS") return; if(e.button==0) ml=0; else mr=0; }
document.oncontextmenu=function(e){ e.preventDefault(); return false; }

//document.onmousedown=function(e){ md=true; document.onmousemove(e); }
//document.onmouseup=function(){ md=false; }


/*=============================
              TOUCH
  =============================*/
function touchmove(e){ 
   e.offsetX=e.touches[0].offsetX;
   e.offsetY=e.touches[0].offsetY;
   document.onmousemove(e); 
   e.preventDefault(); 
   return false; 
}
function touchstart(e){ e.button=0; document.onmousedown(e); e.preventDefault();  alert('left/t/='); return false; }
function touchend(e){ e.button=0; document.onmouseup(e); e.preventDefault();  alert('left/t/='); return false; }

var objx={}
var protection="**********************************************************************************************************************************";
protection=protection+protection; protection=protection+protection; protection=protection+protection;

//ip_bak="99.89.185.120";
//ip="99.89.185.120";
target="SantaCruz-DEVI1";
target="SantaCruz-DEVI2";
target="Portland-DEVI1";
target="Harmony-DEVI";
ignore=false;

function send(data){
  var xhr=new XMLHttpRequest();
  xhr.open('GET','getgui.php?'+paramify(data),true);
  xhr.onreadystatechange= function() {
    if (this.readyState!==4) return;
    if (this.status!==200) return;
    
    try{ objx=JSON.parse(xhr.responseText); }
    catch(e){ console.log(protection+" I can't make sense of this JSON object "+protection+
         xhr.responseText+protection+" I can't make sense of this JSON object "+protection); }
    
    //if (objx.ip!=ip){ console.log(objx.ip); return; }
    ts=Date.now()+"";
    ts=ts.substr(-7)+">";
    match=objx.print.substr(0,target.length);
    if(match==target || ignore){
      if(objx.print.substr(-4)=="<br>") objx.print=objx.print.substr(0,objx.print.length-4);
      if(objx.print) console.log(ts+objx.print.replace(/<br>/g, "\n"+ts));
    }
    //document.write(xhr.responseText);
  };
  xhr.send();
}

function paramify(d){
  var p="mode=s";
  for(var i in d){
    p+="&"+i+"=";
    p+=d[i];
  }
  //console.log(p);
  return p;
}