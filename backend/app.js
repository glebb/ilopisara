require('dotenv').config({ path: '../.env' })
const puppeteer = require('puppeteer-extra')
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin());
const puppeteer_original = require('puppeteer');
const {  QueryHandler } = require("query-selector-shadow-dom/plugins/puppeteer");
puppeteer.use(StealthPlugin())

var express = require("express");
var app = express();
app.listen(3000, () => {
 console.log("Server running on port 3000");
});

const viewPort = { width: 1280, height: 800 };
(async function() {
    await puppeteer_original.registerCustomQueryHandler('shadow', QueryHandler);
})();
app.get("/members/:clubId", async function(req, res, next) {
    var browser = await puppeteer.launch({ headless: true });    
    var page = await browser.newPage();
    await page.setViewport(viewPort)
    page.on('response', async (response) => { 
        if (response.url().startsWith('https://proclubs.ea.com/api/nhl/members/career/stats')) {
            console.log(response.url())
            const data = await response.json();
            res.json(data);
        }           
    }); 
    await page.goto('https://www.ea.com/fi-fi/games/nhl/nhl-22/pro-clubs/overview?platform=' + process.env.PLATFORM + '&clubId=' + req.params.clubId, {
        waitUntil: 'networkidle2'
    });
    await browser.close();
});

app.get("/matches/:clubId", async function(req, res, next) {
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
    await page.goto('https://www.ea.com/fi-fi/games/nhl/nhl-22/pro-clubs/match-history?clubId=' + req.params.clubId + '&platform=' + process.env.PLATFORM, {
        waitUntil: 'networkidle2'
    });
    await browser.close();
});

app.get("/team/:name", async function(req, res, next) {
    var browser = await puppeteer_original.launch({ headless: true });    
    var page = await browser.newPage();
    await page.setViewport(viewPort) 
    await page.setUserAgent(
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
       );   
    page.on('response', async (response) => { 
        if (response.url().startsWith('https://proclubs.ea.com/api/nhl/clubs/search')) {
            console.log(response.url());
            const data = await response.json();
            await browser.close();
            res.json(data);    
        }   
    }); 
    await page.goto('https://www.ea.com/fi-fi/games/nhl/nhl-22/pro-clubs/rankings#platform=' + process.env.PLATFORM, {
        waitUntil: 'networkidle2'
    });
    await page.waitForSelector('shadow/#search');
    element = await page.$('shadow/#search');
    await page.focus('shadow/#search');
    await page.keyboard.type(req.params.name);
    await page.click('shadow/div.eapl-proclub-ranking__tabs-search > div > iron-icon.eapl-proclub-ranking__search-icon');
});