const puppeteer = require('puppeteer-extra')
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())

var express = require("express");
var app = express();
app.use('/public', express.static(__dirname + '/public'));
app.listen(3000, () => {
 console.log("Server running on port 3000");
});

const viewPort = { width: 1280, height: 800 };


app.get("/members", async function(req, res, next) {
    var browser = await puppeteer.launch({ headless: true });    
    var page = await browser.newPage();
    await page.setViewport(viewPort)
    const options = {
        path: 'public/screenshot.png',  // set's the name of the output image'
        fullPage: false,
        // dimension to capture
        clip: {      
            x: 0,   // x coordinate
            y: 650,   // y coordinate
            width: 1280,      // width
            height: 2120   // height
        }
    }        
    page.on('response', async (response) => { 
        if (response.url().startsWith('https://proclubs.ea.com/api/nhl/members/career/stats')) {
            console.log(response.url())
            const data = await response.json();
            res.json(data);
        }           
    }); 
    await page.goto('https://www.ea.com/fi-fi/games/nhl/nhl-22/pro-clubs/overview?platform=ps4&clubId=19963', {
        waitUntil: 'networkidle2'
    });
    /*await page.waitForSelector('#truste-consent-button');
    const element = await page.$('#truste-consent-button');
    await element.click()
    await page.waitForSelector('#truste-consent-button', {hidden: true});
    await page.screenshot(options)*/
    await browser.close();
});

app.get("/matches", async function(req, res, next) {
    var browser = await puppeteer.launch({ headless: true });    
    var page = await browser.newPage();
    await page.setViewport(viewPort)
    page.on('response', async (response) => { 
        if (response.url().startsWith('https://proclubs.ea.com/api/nhl/clubs/matches')) {
            console.log(response.url())
            data = await response.json();
            res.json(data);
        }   
    }); 
    await page.goto('https://www.ea.com/fi-fi/games/nhl/nhl-22/pro-clubs/match-history?clubId=19963&platform=ps4', {
        waitUntil: 'networkidle2'
    });
    await browser.close();
});