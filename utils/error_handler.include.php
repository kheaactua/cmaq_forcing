<?php
/////////////////////////////////////////////////////////////////////////
//		_
//	 <' )_,  Copyright RealDecoy 
//	 (	 )			 2003
//	~~~~~~~~ 
// This file is subject to a license agreement and cannot be used 
// or sold without without the written approval of RealDecoy Inc.
// Information about licensing can be found on the RealDecoy website
// at www.realdecoy.com.
//
// Description:  
// This file is the master configuration file used to define the constants
// used within the website.
//
// $Author: Matthew Russell $ 
// $Date: 2007/07/27 15:25:08 $
// $Revision: 1.6 $
// $Source: /var/cvs/gtb/master/includes/error_handler.include.php,v $
//
/////////////////////////////////////////////////////////////////////////

if (!function_exists('userErrorHandler')) {

/*
This file is intended to handle all the error handling on the site.
Whenever an error occures anywhere on the site, this file writes that
error into a file in an XML format. This makes errors far easier to
trace, debug, and a user will never see them.
*/

if (!defined("ERROR_LOG_FILE"))
	define("ERROR_LOG_FILE", "/tmp/aurams.txt"); // The error logging file
if (!defined("SHOW_ERRORS"))
	define("SHOW_ERRORS", false);

define("TRUNCATE_REQUEST_LENGTH", 256);	// The maximum length of any request value that is logged.
										// the point of this is that we don't need an uploaded file
										// for example, to be logged.
define("ERROR_DATE_FORMAT", "Y-m-d H:i:s (T)");

if (!defined('E_DEPRECATED'))
	define("E_DEPRECATED", 8192);

require_once("request.class.php");

// we will do our own error handling
error_reporting(E_ALL);

// user defined error handling function
function userErrorHandler($errno, $errmsg, $filename, $linenum, $vars) {

	// define an assoc array of error string
	// in reality the only entries we should
	// consider are E_WARNING, E_NOTICE, E_USER_ERROR,
	// E_USER_WARNING and E_USER_NOTICE
	$errortype =	array (
						E_ERROR		=> "Error",
						E_WARNING		=> "Warning",
						E_PARSE		=> "Parsing Error",
						E_NOTICE		=> "Notice",
						E_CORE_ERROR	=> "Core Error",
						E_CORE_WARNING	=> "Core Warning",
						E_COMPILE_ERROR  	=> "Compile Error",
						E_COMPILE_WARNING => "Compile Warning",
						E_USER_ERROR	=> "User Error",
						E_USER_WARNING	=> "User Warning",
						E_USER_NOTICE	=> "User Notice",
						E_RECOVERABLE_ERROR => "Recoverable error",
						E_STRICT        => "Deprecated", // Also deprecated errors
						E_DEPRECATED	=> "Deprecated",
					);
	// set of errors for which a var trace will be saved
	$user_errors = array(E_USER_ERROR, E_USER_WARNING, E_USER_NOTICE, E_DEPRECATED);

	$err = "";
/*
	$err .= "\t<errornum>" . $errno . "</errornum>\n";
	$err .= "\t<errortype>" . $errortype[$errno] . "</errortype>\n";
	$err .= "\t<errormsg>" . $errmsg . "</errormsg>\n";
	$err .= "\t<scriptname>" . $filename . "</scriptname>\n";
	$err .= "\t<scriptlinenum>" . $linenum . "</scriptlinenum>\n";
*/
	$err .= "Error Type: " . $errortype[$errno] . " ($errno) (".E_DEPRECATED.")\n";
	$err .= "Script Name: " . $filename . "\n";
	$err .= "Error Message: " . $errmsg . "\n";
	$err .= "Scriptlinenum: " . $linenum . "\n";

	if (strpos($filename, "PEAR")
	   || ( strpos($filename, "log4php") && $errno&(E_STRICT|E_DEPRECATED|E_USER_NOTICE) )
	   || strpos($errmsg, "getLogger") || strpos($errmsg, "DB::isError()")
	   || (strpos($filename, "htmlMimeMail5") && $errno&(E_NOTICE|E_STRICT|E_DEPRECATED))
	   || ( strpos($filename, "Log.php") && $errno&(E_STRICT|E_DEPRECATED|E_USER_NOTICE) )
	   || (strpos($filename, "CreoleTypes") && $errno&(E_NOTICE|E_STRICT|E_DEPRECATED))
	   || ( strpos($filename, "Propel.php") && $errno&(E_STRICT|E_DEPRECATED|E_USER_NOTICE) )
	   || ( strpos($filename, "config-gtb.php") && $errno&(E_STRICT|E_DEPRECATED|E_USER_NOTICE) && strstr($errmsg, 'Log::'))
	   || ( strpos($filename, "MySQLResultSet.php") && $errno&(E_WARNING) )
	   || ( strpos($filename, "DB.php") && $errno&(E_STRICT|E_DEPRECATED) )	//stroefinder
	   || ( strpos($filename, "database.class.php") && $errno&(E_STRICT|E_DEPRECATED) )	//storefuinder
	   ||  (strpos($filename, "common.php") && $errno&(E_STRICT|E_DEPRECATED) )	   //storefinder
	   ||  (strpos($filename, "aboutImages.lib.php") && strstr($errmsg, 'chmod') !== false && $errno&(E_WARNING) )	   //storefinder
	   ) {
		// do nothing
	} else {
		generalErrorHandler("Run-time Error", $err);
	}

}

/*	This function is meant for any general error. It was built to handle Pear errors.
	The $xml parameter is to pass additional information to this function that will
	not be parsed or formatted in anyway. The intention of that is our custom php error
	handler can call this function and add a little information to the error.
*/
	

function generalErrorHandler($msg, $xml = "") {

	$r = new Request(); // This will slow things down is there are lots
						// of errors, but if things are done properly
						// that should never happen.

	if (is_object($msg))
		$msg = $msg->userinfo;
	// else, leave it alone..

	/*// Protect the input..
	$msg = ereg_replace("]]>", "]]&gt;", $msg); // Protection from a closing CDATA tag.
	$msg = htmlspecialchars("<![CDATA[$msg]]>"); */

					
	// timestamp for the error entry
	$dt = date(ERROR_DATE_FORMAT);

	/* $err = "<errorentry>\n";
	$err .= "\t<datetime>" . $dt . "</datetime>\n";
	$err .= "\t<time>" . mktime() . "</time>\n"; */

	$err = "Error: \n";
	$err .= "Date Time: " . $dt . "\n";
	$err .= "Time: " . time() . "\n";


	// Lets get the request variables in here.
	// Truncate any value to less than 256 characters.. No need to log an entire
	// uploaded file or something like that.
	// $err .= "\t<request>\n";
	$err .= "Request Variables: \n";
	$request_vars = $r->getParamArray();
	foreach ($request_vars as $key => $val) {
		if (is_array($val))
			$val = "array(" . join(", ", $val) . ")";
		if (strlen($val) > TRUNCATE_REQUEST_LENGTH)
			$val = substr($val, 0, TRUNCATE_REQUEST_LENGTH);


		//$val = ereg_replace("]]>", "]]&gt;", $val); // Protection fmro a closing CDATA tag.
		//$err .= "\t\t<request_variable name=\"$key\"><![CDATA[$val]]></request_variable>\n";
		$err .= "\t$key = $val\n";
	}
	//$err .= "\t</request>\n";

	// Add any xml that was sent by another function.
	$err .= $xml;

	// Lets put a traceback in this
	//$err .= "\t<traceback>\n";
	$err .= "Traceback:\n";
	foreach(debug_backtrace() as $t) {
		if(isset($t['file'])) {
			//$err .=  "\t\t" . "<line file=\"". $t['file'] ."\" line=\"". $t['line'] . "\">";
			$err .=  "\t" . $t['file'] .":". $t['line'] . " --> ";
		} else {
			// if file was not set, I assumed the function call
			// was from PHP compiled source (ie XML-callbacks).
			$err .=  "\tPHPinner-code: ";
		}

		if(isset($t['class']))
			$err .=  $t['class'] . $t['type'];

		$err .=  $t['function'];
	
		if(isset($t['args']) && sizeof($t['args']) > 0)
			$err .=  '(...)';
		else
			$err .=  '()';
	
		/*if(isset($t['file']))
			$err .=  "</line>\n";
		else
			$err .= "</PHPinner-code>\n"; */
		$err .= "\n";
	}
	//$err .= "\t</traceback>\n";
	$err .= "END OF TRACEBACK\n";
	//$err .= "\t<message>$msg</message>\n";
	$err .= "\n";
	$err .= "Message: $msg\n";
	
	$err .= "\n\n";

	//$err .= "</errorentry>\n\n";

	// save to the error log, and e-mail me if there is a critical user error
	// A 1 means:	Message is emailed to the address i the destination
	// A 3 means:	message is appended to the file destination. A newline is not
	//				automatically added to the end of the message string.
	//				
	//				Source: www.php.net. message is the first argument, destination
	//				is the third)
	//error_log($err, 1, "matt@realdecoy.com");

	if (SHOW_ERRORS == true) {
		$err = preg_replace("/Error Message: (.*)\n/", "Error Message: <span style=\"font-weight: bold; font-size: larger; background-color: #FFF; color: #D00;\">$1</span>\n", $err);
		$err = preg_replace("/Scriptlinenum: (\d*)\n/", "Scriptlinenum: <span style=\"font-weight: bold; font-size: larger; background-color: #FFF; color: #D00;\">$1</span>\n", $err);
//	$err = preg_replace("/(Error Message): (.*)/", "", $err);
		print "<pre style=\"text-align: left; font-size: normal;\">$err</pre>";
	}
}

$old_error_handler = set_error_handler("userErrorHandler");

}
