<html >
<head>
<meta content="text/html; charset=UTF-8">
</head>
<body>
<br> crystal 500
<form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method='post'>
<input type="hidden" name="cmd" value="_xclick">
<input type="hidden" name="business" value="liyonghelpme4@qq.com">
<input type="hidden" name="item_name" value="crystal 500">
<input type="hidden" name="item_number" value="1">
<input type="hidden" name="amount" value="399.00">
<input type="hidden" name="currency_code" value="USD">
<?php
$invoice=$_GET["invoice"];
echo "<input type='hidden' name='invoice' value='$invoice'>";
?>
<input type="hidden" name="return" value="http://www.caesarsgame.com/success.php">
<input type="hidden" name="cancel_return" value="http://www.caesarsgame.com/cancel.html">
<input type="hidden" name="custom" value="12345">
<input type="image" src="https://www.paypal.com/en_US/i/btn/btn_buynow_LG.gif" border="0" name="submit" alt="Pay with PayPal">
<input type="hidden" name="cmd" value="_xclick">
</form>
</body>
</html>
