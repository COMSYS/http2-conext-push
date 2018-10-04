#!/usr/bin/env nodejs
const penthouse = require('penthouse'),
    puppeteer = require('puppeteer')
    path = require('path'),
    fs = require('fs'),
    __basedir = './';


if(process.argv.length != 6)
{
    console.error("Usage create-critical-css.js URL MERGED_CSS OUTPUT_PATH SCREENSHOT_PATH")
    process.exit()
}


const url = process.argv[2];
const merged_css_path = process.argv[3];
const output_path_css = process.argv[4];
const output_path_screenshots = process.argv[5];
//TODO: Ideally puppeteer would use the same browser as we used for
//capturing but atm i have no idea how to tell puppeteer the chrome binary over penthouse
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3281.0 Safari/537.36"
console.log(url, merged_css_path, output_path_css)

penthouse({
    url: url,       // can be local html file path
    css: path.join(__basedir + merged_css_path),
    // OPTIONAL params
    //1200x960
    width: 1200,                    // viewport width
    height: 960,                    // viewport height
    forceInclude: [],
    timeout: 30000,                 // ms; abort critical CSS generation after this timeout
    strict: false,                  // set to true to throw on CSS errors (will run faster if no errors)
    maxEmbeddedBase64Length: 1000,  // characters; strip out inline base64 encoded resources larger than this
    userAgent: UA, // specify which user agent string when loading the page
    renderWaitTime: 2000,            // ms; render wait timeout before CSS processing starts (default: 100)
    blockJSRequests: false,          // set to false to load (external) JS (default: true)
    puppeteer: {
        getBrowser: function(){
            return puppeteer.launch({
                //executablePath: process.env.CHROME_BINARY_PUSH, does not work...
                headless:false, //crashes for youtube and twitter otherwise.
                ignoreHTTPSErrors:true,
                waitUntil: 'networkidle2',
                args: ['--disable-setuid-sandbox', '--no-sandbox','--disable-quic']
            }
            );
        }
    },
    /*screenshots: {
        // turned off by default
        basePath: output_path_screenshots, // absolute or relative; excluding file extension
        type: 'jpeg', // jpeg or png, png default
        quality: 20 // only applies for jpeg type
        // -> these settings will produce homepage-before.jpg and homepage-after.jpg
      },
    */
    //customPageHeaders: {
    //  'Accept-Encoding': 'identity' // add if getting compression errors like 'Data corrupted'
    //}
})
.then(criticalCss => {
    // use the critical css
    fs.writeFileSync(output_path_css, criticalCss);
})
.catch(err => {
    console.error(err);
    // handle the error
})
