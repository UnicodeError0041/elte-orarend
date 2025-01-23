<?php
header("Content-Type: application/json; charset=utf-8");
header("Access-Control-Allow-Origin: *");


ini_set('memory_limit', '1000000000');
echo file_get_contents("result.json");
