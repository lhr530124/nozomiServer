<html >
<head>
<meta content="text/html; charset=UTF-8">
</head>
<body>
<?php
$item_name=$_GET["item_name"];
echo "<br> $item_name";
$host="www.sandbox.paypal.com";
echo "<form action='https://$host/cgi-bin/webscr' method='post'>";
?>

<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="liyonghelpme4@qq.com">

<input type="hidden" name="item_number" value="1">

<?php
$invoice=$_GET["invoice"];
$item_name=$_GET["item_name"];
$amount=$_GET["amount"];
$currency_code=$_GET["currency_code"];
echo "<input type='hidden' name='item_name' value='$item_name'>";
echo "<input type='hidden' name='invoice' value='$invoice'>";
echo "<input type='hidden' name='amount' value='$amount'>";
echo "<input type='hidden' name='currency_code' value='$currency_code'>";

<<<<<<< HEAD
$domainHost="http://www.caesarsgame.com";
=======
$domainHost="http://23.21.135.42";

>>>>>>> 2f0e93b1c31271499dbb6412e9628ebd859dd769
echo "<input type='hidden' name='return' value='$domainHost/success.php'>";
echo "<input type='hidden' name='cancel_return' value='$domainHost/cancel.html'>";
?>

<input type="hidden" name="custom" value="12345">
<input type="image" src="https://www.paypal.com/en_US/i/btn/btn_buynow_LG.gif" border="0" name="submit" alt="Pay with PayPal">
<input type="hidden" name="cmd" value="_xclick">
</form>
</body>
</html>
