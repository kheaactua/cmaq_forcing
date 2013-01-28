<?php

if (!class_exists('Request')) {

class Request {
	var $_rqs;
	var $_done_init;

	function request() {
		if (isset($GLOBALS['_RD_REQUEST'])) {
			$this->_rqs = &$GLOBALS['_RD_REQUEST']->_rqs;
			$this->_done_init = true;
		} else {
	  
			$this->_done_init = false;
			$this->_rqs = array();
			reset( $_REQUEST );
	
			// Grab our data and cleanup
			$this->_rqs = $_REQUEST;
	
			$tmp = "_rqs_cleanup";
			array_walk( $this->_rqs, $tmp );
	
			$_REQUEST = array();
			$_GET = array();
			$_POST = array();
	
			$this->_done_init = true;
		}
	}

	// Retrieve a paramater by name. Returns NULL if it doesn't exist
	function getParam($name) {
		return array_key_exists($name, $this->_rqs) ? $this->_rqs[ $name ] : NULL;
	}

	// Set the value of the specified param. Will create if it doens't exist
	function setParam($name, $val) {
		_rqs_cleanup($val);
		$this->_rqs[ $name ] = $val;
	}

  // Set the value of the specified param. Will skip assignment if the param 
  // is already defined.
	function setParamDefault($param, $val) {
		if ( !$this->inRequest($param) )
			$this->setParam($param, $val);
	}

	// Return request elements in an associative array
	function getParamArray() {
		return $this->_rqs;
	}

	// Checks wether the given name was actually included in the actual request
	function inRequest($param) {
		return array_key_exists($param, $this->_rqs); 
	}

	function getRequestUrlString($exclude = array()) {
		$str = "";

//		if (!count($exclude))
			$exclude[] = "PHPSESSID";

		$exclude_arr = array();
		foreach ($exclude as $key) {
			$exclude_arr[$key] = true;
		}

		foreach ($this->_rqs as $key=>$val) {
			
			if (array_key_exists($key, $exclude_arr))
				continue;
				
			if (is_array($val)) {
				foreach($val as $k=>$v) {
					$str .= "&". urlencode($key) . "[$k]=" . urlencode($v);
				}
			} else {
				$str .= "&". urlencode($key) . "=" . urlencode($val);
			}
		}
		return $str;
	}

	function isEmpty() {
		return count($this->_rqs) ? false : true;
	}

}

// This is here because PHP 5.0 can't do call backs well enough. Infact they loose $this completely..
function _rqs_cleanup(&$item, $key = NULL, $r = NULL) {
	// If item is an array, recurse into it
	if ( is_array( $item ) ) {
		//$tmp[0] = &$this; $tmp[1] = '_rqs_cleanup';
		$tmp = '_rqs_cleanup';
		array_walk( $item, $tmp, $r );
		return;
	}
	// If we are in the constructor, cleanup various PHP foolishness
	if (is_object($r)) {
		if ( $r->_done_init == false ) {
			// Fix magic quotes
			if( get_magic_quotes_gpc() )
				$item = stripslashes($item);
		}
	}
	// Cleanup runtime foolishness
	if( $item == NULL && $item !== NULL )
		$item = NULL;
}

$GLOBALS['_RD_REQUEST'] = new Request();

}
?>
