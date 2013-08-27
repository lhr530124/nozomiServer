<?php 
// read the post from PayPal system and add 'cmd' 
$req = 'cmd=' . urlencode('_notify-validate');

//$myFile = "PaymentRecord.txt"; 
//$fh = fopen($myFile, 'w+') or die("can't open file");

foreach ($_POST as $key => $value) 
{  
    $value = urlencode(stripslashes($value));  
    $req .= "\n&$key=$value"; 
}

//fwrite($fh, $req);

$ch = curl_init(); 
curl_setopt($ch, CURLOPT_URL, 'https://www.sandbox.paypal.com/cgi-bin/webscr'); 
curl_setopt($ch, CURLOPT_HEADER, 0); 
curl_setopt($ch, CURLOPT_POST, 1); 
curl_setopt($ch, CURLOPT_RETURNTRANSFER,1); 
curl_setopt($ch, CURLOPT_POSTFIELDS, $req); 
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE); 
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE); 
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Host: www.sandbox.paypal.com')); 
$res = curl_exec($ch); 
curl_close($ch);

//fwrite($fh, $res);

// assign posted variables to local variables 
$item_name = $_POST['item_name']; 
$item_number = $_POST['item_number']; 
$payment_status = $_POST['payment_status']; 
$payment_amount = $_POST['mc_gross']; 
$payment_currency = $_POST['mc_currency']; 
$txn_id = $_POST['txn_id']; 
$receiver_email = $_POST['receiver_email']; 
$payer_email = $_POST['payer_email'];
$invoice = $_POST['invoice'];

if (strcmp ($res, "VERIFIED") == 0) {  
// check the payment_status is Completed  
if($payment_status == "Completed") {
    $con = mysqli_connect("localhost", "root", "2e4n5k2w2x", "nozomi" );
    if(mysqli_connect_errno($con)) {
        echo "Failed to connect to:" . mysqli_connect_error();
    } else {
        $sql = "insert into buyRecord (txn_id, mc_gross, mc_currency, item_name, payer_email, receiver_email, invoice) values ('$txn_id', '$payment_amount', '$payment_currency', '$item_name', '$payer_email', '$receiver_email', '$invoice')";
        if(!mysqli_query($con, $sql)) {
            echo "Error" . mysqli_error($con);
        }
        mysqli_commit($con);
    }
    mysqli_close($con);
}
// check that txn_id has not been previously processed  
// check that receiver_email is your Primary PayPal email  
// check that payment_amount/payment_currency are correct  
// process payment  
    //fwrite($fh, $req."\n&IPN_Status=Verified"); 
} 
else if (strcmp ($res, "\n&IPN_Status=INVALID") == 0) {  
// log for manual investigation  
    //fwrite($fh, $req."Invalid"); 
}
else{     
    //fwrite($fh, $req."\n&IPN_Status=Error"); 
}

fclose($fh); 
?>


