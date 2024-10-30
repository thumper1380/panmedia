<?php
$domain = 'REPLACE_WITH_YOUR_DOMAIN'; // change to your domain name (e.g. https://api.yourdomain.com)
$token = 'REPLACE_WITH_YOUR_TOKEN';






$domain = 'http://api.panmedia.io'; // change to your domain name (e.g. https://api.yourdomain.com)
$token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiYyI6MTY4NzE3NTE4My45NzM0OTl9.XRmgcb5kmcNaE5AoMExcBkjhmx3-BquCu9aAtGtjfAA';


$json = file_get_contents('php://input');
$data = json_decode($json, true);


// push lead url
$endpoint = '/leads';
$url = $domain . $endpoint;


// get client language
function getClientLanguage() { 
    $lang = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2);
    return strtoupper($lang);
}

// get client ip
function getClientIP() { 
    if (array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER)) {
        return $_SERVER["HTTP_X_FORWARDED_FOR"];
    } else if (array_key_exists('REMOTE_ADDR', $_SERVER)) {
        return $_SERVER["REMOTE_ADDR"];
    } else if (array_key_exists('HTTP_CLIENT_IP', $_SERVER)) {
        return $_SERVER["HTTP_CLIENT_IP"];
    }
    return '';
}

// Check if form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Collect data from the form
    $data_ = [
        "ip" => getClientIP(),
        "first_name" => $data['first_name'],
        "last_name" => $data['last_name'],
        "email" => $data['email'],
        "phone_number" => $data['phone_number'],
        "country" => $data['country'],
        "source" => $data['source'],
        "language" => getClientLanguage(),
        "funnel" => 1,
    ];
    
    // add all client aff_sub_1 - aff_sub_20 from post request to data array
    for ($i = 1; $i <= 20; $i++) {
        if (isset($data['aff_sub_' . $i])) {
            $data_['aff_sub_' . $i] = $data['aff_sub_' . $i];
        }
    }

    $ch = curl_init($url);

    // add Authorization header
    // Bearer + token

    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data_));                                                                  
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
        'Content-Type: application/json',
        'Content-Length: ' . strlen(json_encode($data_)),
        'Authorization: Bearer ' . $token
        ),
    );                                                                                                                   

    $result = curl_exec($ch);

    if (!$result) {
        die('Error: "' . curl_error($ch) . '" - Code: ' . curl_errno($ch));
    } else {
        // Decode the JSON response
        $responseData = json_decode($result, true);

        // Handle the response
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        switch ($httpCode) {
            case 201:  // OK
                // if auto_login_url is set, redirect to auto_login_url otherwise redirect to thank_you_url
                $redirectUrl = isset($responseData['auto_login_url']) ? $responseData['auto_login_url'] : $responseData['thank_you_url'];
                $pixels = isset($responseData['pixels']) ? $responseData['pixels'] : '';
                if ($pixels) {
                    foreach ($pixels as $pixel) {
                        if ($pixel['type'] == 'body_html_insert') {
                            echo $pixel['content'];
                        }
                        else if ($pixel['type'] == 'script_evaluate') {
                            echo '<script>' . $pixel['content'] . '</script>';
                        }
                        else if ($pixel['type'] == 'inline_iframe_url') {
                            echo '<iframe src="' . $pixel['content'] . '" frameborder="0" scrolling="no" width="1" height="1" style="display:none"></iframe>';
                        }
                        else if ($pixel['type'] == 'inline_script_url') {
                            echo '<script src="' . $pixel['content'] . '"></script>';
                        }
                        else if ($pixel['type'] == 'inline_script_img') {
                            echo '<img src="' . $pixel['content'] . '" width="1" height="1" />';
                        }
                    }
                }
                header('Location: ' . $redirectUrl);
                break;
            case 400:
                foreach ($responseData['validation_errors'] as $key => $value) {
                    echo $key . ': ' . $value[0] . "\n";
                }
                break;
            case 409:  // Unauthorized
                echo $responseData['message'];
                break;
            case 401:  // Unauthorized
                echo 'Unauthorized: ' . $responseData['message'];
                break;
            default:
                echo 'Unexpected HTTP code: ', $httpCode, "\n" . $responseData;
        }
    }

    curl_close($ch);
}

?>
