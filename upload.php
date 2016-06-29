<?php
if(sizeof($_FILES)==1){
  echo $_FILES['media']['tmp_name'];
  //file_put_contents("screenshot.png", file_get_contents($_FILES['media']['tmp_name']));
  file_put_contents("screenshot.jpg", file_get_contents($_FILES['media']['tmp_name']));
  $fc=file_get_contents("fc")*1+1;
  file_put_contents("fc",$fc);
}
?>