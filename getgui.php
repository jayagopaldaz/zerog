<?php
if($_GET['mode']=='r'){
  //$ip=get_client_ip();
  //if($ip=='99.89.185.120') return;
  $x=file_get_contents("x");
  $y=file_get_contents("y");
  $l=file_get_contents("l");
  $r=file_get_contents("r");
  $k=file_get_contents("k");
  $req=file_get_contents("req");
  echo '{"x":"'.$x.'","y":"'.$y.'","l":"'.$l.'","k":"'.$k.'","r":"'.$r.'","req":"'.$req.'"}';
  file_put_contents('k','0');
}

if($_GET['mode']=='s'){
  //$ip=get_client_ip();
  //if($ip=='99.89.185.120') return;
  if(array_key_exists('x',$_GET)) file_put_contents('x',$_GET['x']);
  if(array_key_exists('y',$_GET)) file_put_contents('y',$_GET['y']);
  if(array_key_exists('l',$_GET)) file_put_contents('l',$_GET['l']);
  if(array_key_exists('r',$_GET)) file_put_contents('r',$_GET['r']);
  if(array_key_exists('k',$_GET)) file_put_contents('k',$_GET['k']);
  if(array_key_exists('req',$_GET)) file_put_contents('req',$_GET['req']);
  
  $x=file_get_contents("x");
  $y=file_get_contents("y");
  $l=file_get_contents("l");
  $k=file_get_contents("k");
  $r=file_get_contents("r");
  $fc=file_get_contents("fc");
  $req=file_get_contents("req");
  $print=file_get_contents("print");
  //echo '{"id":"'.$id.'","print":"'.$print.'","x":"'.$x.'","y":"'.$y.'","l":"'.$l.'","r":"'.$r.'","req":"'.$req.'","fc":"'.$fc.'"}';
  echo '{"print":"'.$print.'","k":"'.$k.'","x":"'.$x.'","y":"'.$y.'","l":"'.$l.'","r":"'.$r.'","req":"'.$req.'","fc":"'.$fc.'"}';
  file_put_contents("print","");
}

if($_GET['mode']=='print'){
  if(array_key_exists('s',$_GET)){
    $data = $_GET['s']."<br>";
    //$f = fopen('print', 'a');
    //fwrite($f, $data);
    file_put_contents("print",$data);
    //echo "successful print";
  }
}

function get_client_ip() {
    $ipaddress = '';
    if (getenv('HTTP_CLIENT_IP'))
        $ipaddress = getenv('HTTP_CLIENT_IP');
    else if(getenv('HTTP_X_FORWARDED_FOR'))
        $ipaddress = getenv('HTTP_X_FORWARDED_FOR');
    else if(getenv('HTTP_X_FORWARDED'))
        $ipaddress = getenv('HTTP_X_FORWARDED');
    else if(getenv('HTTP_FORWARDED_FOR'))
        $ipaddress = getenv('HTTP_FORWARDED_FOR');
    else if(getenv('HTTP_FORWARDED'))
       $ipaddress = getenv('HTTP_FORWARDED');
    else if(getenv('REMOTE_ADDR'))
        $ipaddress = getenv('REMOTE_ADDR');
    else
        $ipaddress = 'UNKNOWN';
    return $ipaddress;
}

?>