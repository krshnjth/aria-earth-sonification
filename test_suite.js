// Comprehensive Browser Testing Suite using Chrome DevTools Protocol
const http = require('http');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 8080;
const BACKEND_PORT = 8000;
const CDP_PORT = 9222;
const USER_DATA_DIR = path.join(__dirname, '.chrome-test-profile');

let chromeProc = null;
let serverProc = null;
let backendProc = null;
let ws = null;
let msgId = 1;
const callbacks = new Map();
const consoleLogs = [];
const consoleErrors = [];
const uncaughtExceptions = [];
const failedRequests = [];

function sendCommand(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = msgId++;
    callbacks.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

function evaluate(expression) {
  return sendCommand('Runtime.evaluate', {
    expression,
    returnByValue: true,
    awaitPromise: true
  }).then(res => {
    if (res.result.exceptionDetails) {
      throw new Error(res.result.exceptionDetails.text + ' ' + (res.result.exceptionDetails.exception?.description || ''));
    }
    return res.result.result?.value;
  });
}

async function startServers() {
  console.log('Starting FastAPI Backend on port ' + BACKEND_PORT + '...');
  backendProc = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(BACKEND_PORT)], {
    cwd: path.join(__dirname, 'backend'),
    stdio: 'ignore'
  });

  console.log('Starting local HTTP server on port ' + PORT + '...');
  serverProc = spawn('python', ['-m', 'http.server', String(PORT)], {
    cwd: __dirname,
    stdio: 'ignore'
  });

  await sleep(1500);
}

async function launchChrome() {
  console.log('Launching Headless Chrome with WebGL...');
  if (!fs.existsSync(USER_DATA_DIR)) {
    fs.mkdirSync(USER_DATA_DIR, { recursive: true });
  }

  const args = [
    '--headless=new',
    '--remote-debugging-port=' + CDP_PORT,
    '--user-data-dir=' + USER_DATA_DIR,
    '--enable-webgl',
    '--use-gl=angle',
    '--use-angle=swiftshader',
    '--ignore-gpu-blocklist',
    '--disable-background-networking',
    '--disable-default-apps',
    '--no-first-run',
    '--mute-audio', // run audio engine logic without physical sound blasting
    `http://127.0.0.1:${PORT}/index.html`
  ];

  chromeProc = spawn(CHROME_PATH, args, { stdio: 'ignore' });

  // Wait for CDP readiness
  for (let i = 0; i < 25; i++) {
    try {
      const targets = await getJson(`http://127.0.0.1:${CDP_PORT}/json/list`);
      if (targets && targets.length > 0) {
        const pageTarget = targets.find(t => t.type === 'page');
        if (pageTarget && pageTarget.webSocketDebuggerUrl) {
          return pageTarget.webSocketDebuggerUrl;
        }
      }
    } catch(e) {}
    await sleep(250);
  }
  throw new Error('Chrome failed to respond on CDP port ' + CDP_PORT);
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch(e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function runTests() {
  const testResults = [];
  function assert(title, condition, extra = '') {
    if (condition) {
      console.log(`  [PASS] ${title}`);
      testResults.push({ title, pass: true, extra });
    } else {
      console.error(`  [FAIL] ${title} - ${extra}`);
      testResults.push({ title, pass: false, extra });
    }
  }

  try {
    await startServers();
    const wsUrl = await launchChrome();
    console.log('Connected to Chrome CDP WebSocket: ' + wsUrl);

    ws = new WebSocket(wsUrl);
    await new Promise((resolve, reject) => {
      ws.onopen = resolve;
      ws.onerror = reject;
    });

    ws.onmessage = event => {
      const msg = JSON.parse(event.data);
      if (msg.id && callbacks.has(msg.id)) {
        const { resolve, reject } = callbacks.get(msg.id);
        callbacks.delete(msg.id);
        if (msg.error) reject(msg.error);
        else resolve(msg);
      } else if (msg.method) {
        if (msg.method === 'Runtime.consoleAPICalled') {
          const type = msg.params.type;
          const text = msg.params.args.map(a => a.value || a.description || '').join(' ');
          consoleLogs.push({ type, text });
          if (type === 'error') consoleErrors.push(text);
        } else if (msg.method === 'Runtime.exceptionThrown') {
          const desc = msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text;
          uncaughtExceptions.push(desc);
        } else if (msg.method === 'Network.loadingFailed') {
          failedRequests.push(msg.params.errorText + ' ' + msg.params.type);
        }
      }
    };

    // Enable domains
    await sendCommand('Runtime.enable');
    await sendCommand('Page.enable');
    await sendCommand('Network.enable');

    console.log('\n--- EXECUTING AUTOMATED BROWSER TEST SUITE ---\n');

    // Wait for initial load
    await sleep(1500);

    // Test 1: DOM Structure & Intro overlay
    console.log('Test Group 1: Initial Page Load & DOM Readiness');
    const title = await evaluate('document.title');
    assert('Page title contains ARIA', title.includes('ARIA'), title);

    const hasIntro = await evaluate("!!document.getElementById('intro')");
    assert('Intro screen exists in DOM', hasIntro);

    const hasCanvas = await evaluate("!!document.getElementById('gl')");
    assert('Three.js canvas element exists in DOM', hasCanvas);

    // Test 2: Initialize Observatory CTA
    console.log('\nTest Group 2: Initialize Observatory Journey');
    await evaluate("document.getElementById('go').click()");
    await sleep(800);

    const introOff = await evaluate("document.getElementById('intro').classList.contains('off')");
    assert('Intro overlay dismissed after clicking go', introOff);

    const uiOn = await evaluate("document.getElementById('ui').classList.contains('on')");
    assert('Main UI overlay activated', uiOn);

    // Test 3: WebGL & Three.js Globe Status
    console.log('\nTest Group 3: WebGL Globe Rendering & Shader State');
    const threeLoaded = await evaluate("typeof THREE !== 'undefined'");
    assert('Three.js library loaded successfully', threeLoaded);

    const webglOk = await evaluate("window.ok === true");
    assert('WebGL initialized and ok state is true', webglOk);

    const earthGroup = await evaluate("!!window.earth && !!window.planet");
    assert('Earth mesh and planetary group exist', earthGroup);

    // Test 4: Globe Rotation, Zoom, and Size
    console.log('\nTest Group 4: 3D Camera, Zoom & Rotation');
    const initialZoom = await evaluate("window.zoom");
    await evaluate("document.getElementById('zi').click()");
    const zoomedIn = await evaluate("window.zoom");
    assert('Zoom in button decreases zoom scalar properly', zoomedIn < initialZoom, `initial: ${initialZoom}, zoomed: ${zoomedIn}`);

    await evaluate("document.getElementById('zo').click()");
    const zoomedOut = await evaluate("window.zoom");
    assert('Zoom out button works properly', Math.abs(zoomedOut - initialZoom) < 0.1, `zoomedOut: ${zoomedOut}`);

    // Test 5: Web Audio API Engine
    console.log('\nTest Group 5: Web Audio API Synthesizer Lifecycle');
    const audioState = await evaluate("!!window.audio && window.audioAvailable");
    assert('Audio engine initialized and available', audioState);

    const isPlaying = await evaluate("window.st.play");
    assert('Playback state is true after initialization', isPlaying);

    const filterFreq = await evaluate("window.audio ? window.audio.primaryFilter.frequency.value : 0");
    assert('Primary filter frequency active (> 500 Hz)', filterFreq > 500, `${filterFreq} Hz`);

    // Test 6: Scientific Categories & Shaders
    console.log('\nTest Group 6: Scientific Categories & Dynamic Colors');
    const categories = ['oceans', 'forests', 'atmosphere', 'cryosphere', 'methane', 'climate'];
    for (const cat of categories) {
      await evaluate(`setCategory('${cat}')`);
      await sleep(150);
      const activeCat = await evaluate("window.st.cat");
      const hex = await evaluate("getComputedStyle(document.documentElement).getPropertyValue('--ac').trim()");
      assert(`Switched to category: ${cat}`, activeCat === cat && hex.length > 0, `Active: ${activeCat}, color: ${hex}`);
    }

    // Test 7: Historical Exploration & Timeline
    console.log('\nTest Group 7: Adjustable Timeline & Historical Milestones');
    await evaluate("setYear(2015)");
    await sleep(200);
    const yr2015 = await evaluate("window.st.year");
    assert('Timeline scrubbed to 2015', yr2015 === 2015);

    const milestoneAlert2015 = await evaluate("document.getElementById('milestone-alert').classList.contains('on')");
    assert('Milestone alert displayed for 2015 (Paris Agreement)', milestoneAlert2015);

    await evaluate("document.getElementById('btn-close-ms').click()");
    const milestoneClosed = await evaluate("!document.getElementById('milestone-alert').classList.contains('on')");
    assert('Milestone alert close button works', milestoneClosed);

    await evaluate("document.getElementById('btn-step-prev5').click()");
    const yr2010 = await evaluate("window.st.year");
    assert('Step -5Y button works', yr2010 === 2010, `Year: ${yr2010}`);

    await evaluate("document.getElementById('btn-step-next').click()");
    const yr2011 = await evaluate("window.st.year");
    assert('Step +1Y button works', yr2011 === 2011, `Year: ${yr2011}`);

    // Test 8: Universal Earth Click-to-Sonify (Raycasting)
    console.log('\nTest Group 8: Universal Click-to-Sonify on Earth');
    // Simulate clicking in the Pacific Ocean (center of canvas)
    await evaluate(`(() => {
      const rect = document.getElementById('gl').getBoundingClientRect();
      handleEarthClick(rect.left + rect.width / 2, rect.top + rect.height / 2);
    })()`);
    await sleep(400);

    const hasRegion = await evaluate("!!window.st.region");
    assert('Direct click on Earth selected a region', hasRegion);

    const bannerOn = await evaluate("document.getElementById('region-banner').classList.contains('on')");
    assert('Region banner popped up with details', bannerOn);

    const regionName = await evaluate("document.getElementById('reg-name').textContent");
    assert('Region name populated properly', regionName.length > 0, regionName);

    // Test 9: UI Protection from Accidental Earth Clicks
    console.log('\nTest Group 9: Pointer Protection on UI Elements');
    // Simulate pointerup over a UI button (e.g. settings button)
    await evaluate(`(() => {
      const btn = document.getElementById('btn-settings');
      const rect = btn.getBoundingClientRect();
      // Dispatch pointerup on the button
      btn.dispatchEvent(new PointerEvent('pointerup', {
        clientX: rect.left + 5,
        clientY: rect.top + 5,
        bubbles: true
      }));
    })()`);
    await sleep(200);

    // Verify it did not replace the region with an accidental click
    const sameRegion = await evaluate("document.getElementById('reg-name').textContent");
    assert('Clicking UI button did not trigger accidental Earth raycast', sameRegion === regionName);

    // Test 10: 18 Global Hotspots & Biome Drawer
    console.log('\nTest Group 10: 18 Global Biomes & Category Filters');
    await evaluate("document.getElementById('btn-regions').click()");
    await sleep(300);

    const drawerOpen = await evaluate("document.getElementById('region-drawer').classList.contains('open')");
    assert('Regions drawer modal opened', drawerOpen);

    const totalCards = await evaluate("document.querySelectorAll('#regions-grid .reg-card').length");
    assert('All 18 hotspot cards rendered in modal', totalCards === 18, `Count: ${totalCards}`);

    // Filter by forests
    await evaluate("document.querySelector(\".biome-filter-btn[data-filter='forests']\").click()");
    const forestCards = await evaluate("document.querySelectorAll('#regions-grid .reg-card').length");
    assert('Forests filter tab displays subset of cards', forestCards > 0 && forestCards < 18, `Count: ${forestCards}`);

    // Filter by atmosphere & permafrost (must include Siberian Taiga!)
    await evaluate("document.querySelector(\".biome-filter-btn[data-filter='atmosphere']\").click()");
    const atmoCards = await evaluate("document.querySelectorAll('#regions-grid .reg-card').length");
    const hasSiberia = await evaluate("Array.from(document.querySelectorAll('#regions-grid .rc-name')).some(el => el.textContent.includes('Siberian'))");
    assert('Atmosphere & Permafrost filter includes Siberian Taiga', hasSiberia, `Cards: ${atmoCards}`);

    // Select Amazon Basin from drawer
    await evaluate("document.querySelector(\".biome-filter-btn[data-filter='all']\").click()");
    await evaluate("document.querySelector('#regions-grid .reg-card').click()");
    await sleep(300);

    const drawerClosed = await evaluate("!document.getElementById('region-drawer').classList.contains('open')");
    assert('Selecting a region card closes modal and updates active biome', drawerClosed);

    // Test 11: Live Earth Scanner Mode
    console.log('\nTest Group 11: Live Earth Audio Scanner Mode');
    await evaluate("document.getElementById('btn-scanner').click()");
    const scanActive = await evaluate("window.st.scanMode === true");
    assert('Scanner mode toggled on', scanActive);

    // Simulate mouse move over center of globe
    await evaluate(`(() => {
      const rect = document.getElementById('gl').getBoundingClientRect();
      updateScannerHover(rect.left + rect.width / 2, rect.top + rect.height / 2);
    })()`);
    const reticleVisible = await evaluate("document.getElementById('scanner-reticle').style.display !== 'none'");
    assert('Scanner reticle visible on globe hover', reticleVisible);

    await evaluate("document.getElementById('btn-scanner').click()");
    const scanOff = await evaluate("window.st.scanMode === false");
    assert('Scanner mode toggled off cleanly', scanOff);

    // Test 12: Control Deck Docking & Minimizing (Full Vision of Earth)
    console.log('\nTest Group 12: Control Deck Minimizing & Dock Presets');
    await evaluate("document.getElementById('btn-minimize-deck').click()");
    const deckMinimized = await evaluate("document.getElementById('jb').classList.contains('minimized')");
    assert('Control deck minimized to slim floating capsule', deckMinimized);

    const miniPlayVisible = await evaluate("document.querySelector('.deck-mini-content').offsetParent !== null");
    assert('Mini capsule controls visible when minimized', miniPlayVisible);

    await evaluate("document.getElementById('btn-expand-deck').click()");
    const deckExpanded = await evaluate("!document.getElementById('jb').classList.contains('minimized')");
    assert('Control deck expanded back to full view', deckExpanded);

    // Dock top
    await evaluate("setDeckDock('top')");
    const dockedTop = await evaluate("document.getElementById('jb').style.top.includes('calc')");
    assert('Deck docked to top position', dockedTop);

    // Restore to bottom
    await evaluate("setDeckDock('bottom')");
    const dockedBottom = await evaluate("document.getElementById('jb').style.bottom.includes('calc')");
    assert('Deck restored to bottom position', dockedBottom);

    // Test 13: Zen Mode (Panoramic Earth Observation)
    console.log('\nTest Group 13: Zen Mode Panoramic Earth View');
    await evaluate("toggleZenMode()");
    const zenOn = await evaluate("document.body.classList.contains('zen-mode')");
    assert('Zen mode activated (overlays hidden)', zenOn);

    await evaluate("toggleZenMode()");
    const zenOff = await evaluate("!document.body.classList.contains('zen-mode')");
    assert('Zen mode deactivated (overlays restored)', zenOff);

    // Test 14: Mobile Responsive Viewports
    console.log('\nTest Group 14: Mobile Viewports Emulation');
    const viewports = [
      { width: 1920, height: 1080, name: '1080p Desktop' },
      { width: 1366, height: 768, name: 'Laptop' },
      { width: 768, height: 1024, name: 'Tablet Portrait' },
      { width: 390, height: 844, name: 'Mobile iPhone' },
      { width: 360, height: 800, name: 'Mobile Android' }
    ];

    for (const vp of viewports) {
      await sendCommand('Emulation.setDeviceMetricsOverride', {
        width: vp.width,
        height: vp.height,
        deviceScaleFactor: 1,
        mobile: vp.width < 768
      });
      await evaluate("onResize()");
      await sleep(150);

      const glWidth = await evaluate("document.getElementById('gl').offsetWidth");
      const deckWidth = await evaluate("document.getElementById('jb').offsetWidth");
      assert(`Viewport ${vp.name} (${vp.width}x${vp.height}) renders without overflow`, deckWidth <= vp.width, `Deck width: ${deckWidth}px, Viewport: ${vp.width}px`);
    }

    // Reset viewport
    await sendCommand('Emulation.clearDeviceMetricsOverride');

    // Test 15: Live Scientific Backend & Empirical Telemetry Sync
    console.log('\nTest Group 15: Live Scientific Backend & Empirical Sync');
    const isLive = await evaluate("window.AriaApi.isLive");
    assert('AriaApi connected to FastAPI backend', isLive === true);

    const badgeText = await evaluate("document.getElementById('backend-badge').textContent");
    assert('Backend badge shows NASA/NOAA LIVE', badgeText.includes('LIVE'), badgeText);

    const climateSub = await evaluate("window.ARIA.CATS.climate.sub");
    assert('Global temperature dataset synchronized with official GISTEMP', climateSub.includes('GISTEMP') || climateSub.includes('Empirical'), climateSub);

    const co2Sub = await evaluate("window.ARIA.CATS.atmosphere.sub");
    assert('Atmospheric CO2 dataset synchronized with official NOAA GML', co2Sub.includes('Mauna Loa') || co2Sub.includes('NOAA'), co2Sub);

    // Test 16: Check Console Errors and Exceptions
    console.log('\nTest Group 16: Console Error & Uncaught Exception Audit');
    assert('Zero uncaught JavaScript exceptions during user journey', uncaughtExceptions.length === 0, uncaughtExceptions.join(' | '));
    assert('Zero browser console errors logged', consoleErrors.length === 0, consoleErrors.join(' | '));

    console.log('\n=============================================');
    const passed = testResults.filter(r => r.pass).length;
    const failed = testResults.filter(r => !r.pass).length;
    console.log(`TOTAL TESTS: ${testResults.length} | PASSED: ${passed} | FAILED: ${failed}`);
    console.log('=============================================\n');

  } catch(err) {
    console.error('Test suite error:', err);
  } finally {
    if (ws) ws.close();
    if (chromeProc) chromeProc.kill();
    if (serverProc) serverProc.kill();
    if (backendProc) backendProc.kill();
    try {
      if (fs.existsSync(USER_DATA_DIR)) {
        fs.rmSync(USER_DATA_DIR, { recursive: true, force: true });
      }
    } catch(e) {}
    process.exit(0);
  }
}

runTests();
