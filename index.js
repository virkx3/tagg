const puppeteer = require('puppeteer');
const axios = require('axios');
const fs = require('fs');
const { USERNAME, SMMWIZ_API_KEY, SERVICE_ID, QUANTITY } = require('./config');

const processedFile = 'processed.json';

let processed = [];
if (fs.existsSync(processedFile)) {
    processed = JSON.parse(fs.readFileSync(processedFile));
}

(async () => {
    try {
        const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
        const page = await browser.newPage();

        await page.goto(`https://www.instagram.com/${USERNAME}/tagged/`, { waitUntil: 'networkidle2', timeout: 60000 });

        await page.waitForSelector('article a');

        const postLinks = await page.$$eval('article a', anchors =>
            anchors.map(a => a.href).filter(link => link.includes('/p/'))
        );

        const newLinks = postLinks.filter(link => !processed.includes(link));

        console.log(`🆕 Found ${newLinks.length} new tagged post(s).`);

        for (const link of newLinks) {
            console.log(`💥 Sending likes to: ${link}`);
            try {
                const res = await axios.post('https://smmwiz.com/api/v2', {
                    key: SMMWIZ_API_KEY,
                    action: 'add',
                    service: SERVICE_ID,
                    link,
                    quantity: QUANTITY
                });
                console.log('✅ API response:', res.data);
                processed.push(link);
            } catch (err) {
                console.error('❌ Error sending likes:', err.response?.data || err.message);
            }
        }

        fs.writeFileSync(processedFile, JSON.stringify(processed, null, 2));

        await browser.close();
    } catch (err) {
        console.error('❌ Failed to run bot:', err.message);
    }
})();
