<?php
// Change the url as appropriate.
$url = "http://pt.nvda-community.org/ws/LastSnapshot/main";
$snapshot = json_decode(file_get_contents($url), true) or die("Can't access webservice");
print "Revision: ". $snapshot["revision"]."\n";
print "Installer link: ".$snapshot["installer"]."\n";
?>
