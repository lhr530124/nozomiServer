<html >
<head>
<meta content="text/html; charset=UTF-8">
</head>
<body>
<?php
$item_name=$_GET["item_name"];
echo "<br> $item_name";
?>
<form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method='post'>
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
?>
<input type="hidden" name="return" value="http://www.caesarsgame.com/success.php">
<input type="hidden" name="cancel_return" value="http://www.caesarsgame.com/cancel.html">
<input type="hidden" name="custom" value="12345">
<input type="image" src="https://www.paypal.com/en_US/i/btn/btn_buynow_LG.gif" border="0" name="submit" alt="Pay with PayPal">
<input type="hidden" name="cmd" value="_xclick">
</form>
</body>
</html>
