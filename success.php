
<title>success</title>
<body>
<?php
//sandboxxx mode 
//sandbox token
//sandbox business user liyonghelpme4@qq.com
//user  liyonghelpme1@qq.com
$pp_hostname="www.sandbox.paypal.com"; //change to paypal when product
$req = 'cmd=_notify-synch';
$tx_token=$_GET['tx'];
$st = $_GET['st'];
$amt = $_GET['amt'];
$cc = $_GET['cc'];
$cm = $_GET['cm'];

//$auth_token="30T_5bQvYO0OJqgYtANaRSgidX5e95kZ5KeDGvVXIGRe5ZCNyOKy-hWqCii";
$auth_token="UyLisw-tftaVLrgTboT0szTf2UNREd0edJ_54vBJy_O3HgQ0hf_p3PctZmG";

$req .= "&tx=$tx_token&at=$auth_token";
//echo("<br>request $tx_token $st")
echo("<br> exis $tx_token $req");

$logfile = fopen('php://temp', 'rw+');
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "https://$pp_hostname/cgi-bin/webscr");
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $req);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
curl_setopt($ch, CURLOPT_CAINFO, "/usr/share/doc/libssl-doc/demos/cms/cacert.pem");
curl_setopt($ch, CURLOPT_VERBOSE, true);
curl_setopt($ch, CURLOPT_STDERR, $logfile);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_HTTPHEADER, array("Host: $pp_hostname"));

$res = curl_exec($ch);
curl_close($ch);
!rewind($logfile);
$con = stream_get_contents($logfile);
echo "<br>verbose:\n<pre>", htmlspecialchars($con), '</pre>\n';
fclose($logfile);

extract(curl_getinfo($ch));
$metrics = <<<EOD
URL....: $url
Code...: $http_code ($redirect_count redirect(s) in $redirect_time secs)
Content: $content_type Size: $download_content_length (Own: $size_download) Filetime: $filetime
Time...: $total_time Start @ $starttransfer_time (DNS: $namelookup_time Connect: $connect_time Request: $pretransfer_time)
Speed..: Down: $speed_download (avg.) Up: $speed_upload (avg.)
Curl...: v{$curlVersion['version']}
EOD;

echo("<br>response is what $res");
if(!$res) {
    echo ("<br><b>error</b>");
} else {
    $lines = explode("\n", $res);
    $keyarray = array();
    if (strcmp ($lines[0], "SUCCESS") == 0) {
        for ($i=1; $i<count($lines);$i++){
        list($key,$val) = explode("=", $lines[$i]);
        $keyarray[urldecode($key)] = urldecode($val);
    }
    // check the payment_status is Completed
    // check that txn_id has not been previously processed
    // check that receiver_email is your Primary PayPal email
    // check that payment_amount/payment_currency are correct
    // process payment
    $firstname = $keyarray['first_name'];
    $lastname = $keyarray['last_name'];
    $itemname = $keyarray['item_name'];
    $amount = $keyarray['payment_gross'];
    $currency = $keyarray['mc_currency'];
    $invoice = $keyarray['invoice'];
     
    echo ("<p><h3>Thank you for your purchase!</h3></p>");
     
    echo ("<b>Payment Details</b><br>\n");
    echo ("<li>Name: $firstname $lastname</li>\n");
    echo ("<li>Item: $itemname</li>\n");
    echo ("<li>Amount: $amount</li>\n");
    echo ("");

    /*
    //wait ipn to verify
    $con = mysqli_connect("localhost", "root", "2e4n5k2w2x", "nozomi" );
    
    if(mysqli_connect_errno($con)) {
        echo("Failed to connect to:" . mysqli_connect_error()+'\n');
    } else {
        $sql = "insert into buyRecord (txn_id, mc_gross, mc_currency, item_name, payer_email, receiver_email, invoice) values ('$tx_token', '$amount', '$currency', '$itemname', 'test@test.com', 'test2@test.com', '$invoice')";
        if(!mysqli_query($con, $sql)) {
            echo("Error" . mysqli_error($con)+'\n');
        }
        mysqli_commit($con);
    }
    mysqli_close($con);
    */

}
else if (strcmp ($lines[0], "FAIL") == 0) {
    // log for manual investigation
}
}
?>

<br>Thank you for your payment. Your transaction has been completed, and a receipt for your purchase has been emailed to you. You may log into your account at<a href="http://www.paypal.com/us"> www.paypal.com/us </a> to view details of this transaction.
<br><a href="close.php">"close Page"</a>
</body>

