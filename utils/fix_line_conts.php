#!/usr/bin/php
<?php

define('ORIG_PATH', getcwd());
include_once("error_handler.include.php");

// Deal with the user inputs
$opts = getopt("f:dD:", array('help'));

$err = array();
$dryrun=false;
//print_var($opts, 'Opts');
do {
	// help
	if (array_key_exists('help', $opts)) {
		print <<<TOHERE
Transform EC code to standard Fortran.  This includes fixing line continuations
and other things.

-f     file
-d     dry-run, print out file rather than writing it
-D     Info level, 1=info, 2=debug

TOHERE;
		print "\n";

		exit(0);
	}

	// Process inputs
	if (array_key_exists('f', $opts)) {
		if (is_readable(ORIG_PATH.'/'.$opts['f']))
			$file = ORIG_PATH.'/'.$opts['f'];
		else
			$err[] = "Data file ". $opts['f'] . " is not readable." . " pwd: " . `pwd`;

		
		if (!is_writable(ORIG_PATH.'/'.$opts['f']))
			$err[] = "Data file ". $opts['f'] . " is not writable." . " pwd: " . `pwd`;

	} else {
		$err[] = "Must specify input file!";
	}
	if (array_key_exists('D', $opts)) {
		$LOG_LEV_level = $opts['D'];
	} else {
		$LOG_LEV_level = LOG_LEV_INFO;
	}
	if (array_key_exists('d', $opts)) {
		$dryrun = true;
	}
} while (false);
if (count($err)) {
	print "Errors:\n";
	foreach ($err as $e) {
		print "- $e\n";
	}
	exit(1);
}

define('LOG_LEV_INFO', 1);
define('LOG_LEV_DEBUG', 2);
function logInfo($mes, $lev = LOG_LEV_DEBUG) {
	global $LOG_LEV_level;

	if ($lev == LOG_LEV_INFO)
		$c = 'i';
	else
		$c = 'd';

	if ($lev <= $LOG_LEV_level) {
		printf("[%s] --> %s\n", $c, $mes);
	}
}

$contents = file_get_contents($file);

// Consolodate some of the line continuations
$contents = preg_replace("/\/\s*(\n\s*)[&%\$\d]/", "/ &$1", $contents);

//#//// Fine grain parser to fix line continuation issues./*{{{*/
//#//// If I go this route, I should split by /\W/, basically split to get every "word"
//#//$levels = array(
//#//   "par" => 0,
//#//   "slash" => 0,
//#//   "dquote" => 0,
//#//   "squote" => 0,
//#//   "line"   => 0
//#//  );
//#//for ($x=0; $x<count($lines); $x++) {
//#//
//#//	if ($x>0)
//#//		$prev = $lines[$x-1];
//#//	else
//#//		$prev = '';
//#//
//#//	$line = $lines[$x];
//#//
//#//	if ($x < count($lines))
//#//		$next = $lines[$x+1];
//#//	else
//#//		$next = '';
//#//
//#//	$chars = preg_split('//', $line);
//#//	for ($i=0; $i<count($chars); $i++) {
//#//
//#//		if ($i>0) $lc = $chars[$i-1];
//#//		else $lc = '';
//#//		if ($i<count($chars)-1) $nc = $chars[$i+1];
//#//		else $nc = '';
//#//
//#//		$c = $chars[$i];
//#//		switch ($i) {
//#//			case "(":
//#//				$levels['par']++;
//#//				break;
//#//			case ")":
//#//				$levels['par']--;
//#//				break;
//#//			case "\"":
//#//				if ($lc != "\\") $levels['dquote'] = xor($levels['dquote'], 1);
//#//				break;
//#//			case "'":
//#//				if ($lc != "\\") $levels['squote'] = xor($levels['squote'], 1);
//#//				break;
//#//			case "!":
//#//				// In a comment, skip this rest of the line
//#//				break 2;
//#//			case "/":
//#//				if (preg_match("/(data|namelist|common)/i", $line) {
//#//					// Not likely a line contnuation here
//#//					$levels['slash'] = xor($levels['slash'], 1);
//#//				}
//#//				break;
//#//			case "c":
//#//				if ($i<6 && !$levels["line"]) {
//#//					if (preg_match("/\s/", $nc)) {
//#//						// Probably a comment
//#//						break 2;
//#//					}
//#//				}
//#//			default:
//#//				if (!$levels["line"]) {
//#//					if (preg_match("/\w/", $c)) {
//#//						// Not yet "in line" and have a word character
//#//						$levels["line"] = 1;
//#//						if ($i == 0) {
//#//							// This should be indented..
//#//							$line = "\t".$line;
//#//							continue;
//#//						}
//#//					} elseif (preg_match("/(\W|\d)/", $c, $matches)) {
//#//						// Weird character but not in a continued line, must be a comment
//#//						// or there's a missing continuation line
//#//						trigger_error("[1] Not sure how to deal with this case ..");
//#//						break;
//#//					} else {
//#//						trigger_error("[2] Not sure how to deal with this case ..");
//#//					}
//#//				} else {
//#//					if (preg_match("/(\W|\d)/", $c)) {
//#//
//#//					}
//#//						
//#//				}
//#//		}
//#//	}
//#//
//#//	// Save changes
//#//	if ($x > 0)
//#//		$lines[$x-1] = $prev;
//#//
//#//	$lines[$x] = $line;
//#//	
//#//	if ($x < count($lines) - 1)
//#//		$lines[$x+1] = $next;
//#//}
//#//
//#//// Put everything back together
//#//$contents = join("\n", $lines);/*}}}*/

// Fix comment style
$contents = preg_replace("/\n(\*|c\s)/i", "\n!", $contents);
// Just incase...
$contents = preg_replace("/\n!(HARACTER|ALL|ONTINUE)/i", "\nC$1", $contents);

// A first try at weird continuation marks on the latter line
$contents = preg_replace("/\n(\s{1,5})[\$+%]\s/", " & \n$1  ", $contents);

// First, fix the continuation mark on any line that ends in a "/"
// but is continued by a symbol on the following line.  In this case
// it is a division.  Otherwise this will be really hard to deal
// with later.
$contents = preg_replace("/\/\s*(\n\s*)[&%\$\d]/", "/ &$1", $contents);

// Line by line parsing
$lines = preg_split("/\n/", $contents);
$conts = array();
for ($x=0; $x<count($conts); $x++)
	$conts[$x] = 0;

$in_block = false;
for ($x=0; $x<count($lines); $x++) {
	if ($x>0)
		$prev = $lines[$x-1];
	else
		$prev = '';

	$line = $lines[$x];

	if ($x < count($lines))
		$next = $lines[$x+1];
	else
		$next = '';

	$is_cont = 0;
	// Is this continued?
	// Won't work if "/" is the continuation character..
	$next = preg_replace("/^(\s*)([&\$%])/", "$1&", $next, -1, $count);
	if ($count) {
		$conts[$x]   |= 1;
		$conts[$x+1] |= 2;
	}

	$line = preg_replace("/([&\$%])\s*$/", "&", $line, -1, $count);
	if ($count) {
		$conts[$x]   |= 4;
		$conts[$x+1] |= 8;
	}

	
	if (preg_match("/&\s*$/", $prev)) {
		$conts[$x-1] |= 16;
		$conts[$x] |= 32;
	}

	// At this point, all continuation symbols except "/" should be the proper "&"

	// Get us out of in_block if the current line is not continued;
if ($in_block === true && $is_cont == 0) logInfo("Out of block at line ". ($x+1), LOG_LEV_DEBUG);
	$in_block = ($in_block&&($conts[$x]>0));

	// Right now, gambling that these don't use "/" as a continuation character
	// (so far, this assumption tends to be true.)	
	if (preg_match("/^\s*namelist/i", $line)) {
		// Nothing for now
	} elseif (preg_match("/^\s*common\s*\/\s*[a-zA-Z0-9_]+\s*\/\s*$/i", $line)) {
		// Add a continuation mark
		$line .= " &";
	} elseif (preg_match("/^\s*data/i", $line)) {
		$in_block = true;
		logInfo("in_block at line ". ($x+1), LOG_LEV_DEBUG);
	} else {

		if (!$in_block) {
			// Check to see if it ends with "/", and change to "&" if it does
			$line = preg_replace("/^[^\s!].*\/\s*$/", "&", $line);
		}

	}

	// Now, deal with using numbers as line continuations in the wrong spot.
	// Usually it's only one number starting at 1
	if (preg_match("/^(\s+)\d(\s+)(.*)/", $line, $matches)) {
		if (!preg_match("/^(continue|format|do)/i", $matches[3])) {
			// This is probably a line continuation
			$line = preg_replace("/(\s*)\d(\s*)(.*)/", "$1&$2$3", $line);
			$conts[$x] |= 64;
			//// Now, place a continuation line at the end of the first line
			//$prev = $prev . " &";
		}
	}

	// Save changes
	if ($x > 0)
		$lines[$x-1] = $prev;

	$lines[$x] = $line;
	
	if ($x < count($lines) - 1)
		$lines[$x+1] = $next;

}

$contents = join("\n", $lines);

// Now where the symbol is on the continued line
$contents = preg_replace('/\n(!\$omp\s*|\s*)[\$%&]/i', " &\n$1", $contents);
// Do the same on OpenMP lines

// Make sure there are never two line continuations ending a line
$contents = preg_replace('/&\s*&([\n]+)/', "&$1", $contents);

// Fix open parenthesises lines.. Mostly for acid_3df_dynp.f90
$contents = preg_replace("@(\n[^\n]+\()\s*\n@", "$1 &\n", $contents);
$contents = preg_replace("@format\([\s\n&]*\+(\d+X),@i", "format($1,", $contents);

// Fix typos in operans..
$contents = preg_replace("/\. (or|gt)\. /i", ".$1.", $contents);

// Fix double comma typos
$contents = preg_replace("/(,\s*&\n\s*),/", "$1", $contents);

if (preg_match("/.cdk90$/", $file)) {
	// fixed format fortran

	// Make sure we can indent
	$contents = preg_replace("/\n([^\s!\n])/", "\n\t$1", $contents);
}

if ($dryrun) {
	$lines = preg_split("/\n/", $contents);
	for ($x=0; $x<count($lines); $x++) {
		printf("%s %3d: %s\n", deconstructBin($conts[$x]), $x+1, $lines[$x]);
	}
} else {
	$fo=fopen($file, 'w');
	fwrite($fo,$contents);
	fclose($fo);
}

function deconstructBin($bin) {
	$str = "";
	for ($i=7; $i>0; $i--) {
		if ($bin&pow(2,$i)) $str .= sprintf("%2d", pow(2, $i));
		else $str .= "00";
		if ($i>1) $str .= ",";
	}
	return sprintf("%02d = %s", $bin, $str);
}
