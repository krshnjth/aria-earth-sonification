if (typeof THREE === 'undefined') {
      document.write('<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"><\/script>');
    }
  </script>
  <script>
    if (typeof THREE === 'undefined') {
      document.write('<script src="https://unpkg.com/three@0.128.0/build/three.min.js"><\/script>');
    }
  </script>

  <!-- External Textures bundle if available -->
  <script src="textures.js"></script>

  <!-- Application Logic -->
  <script>
    // --- Helper Utilities ---
    const $ = s => document.querySelector(s);
    const $$ = s => document.querySelectorAll(s);
    const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
    const lerp = (a, b, t) => a + (b - a) * t;

    // --- Texture Fallback generator ---
    function ensureTextures() {
      if (typeof window.TX === 'undefined' || !window.TX.day) {
        window.TX = {};
        const c = document.createElement('canvas');
        c.width = 512; c.height = 256;
        const ctx = c.getContext('2d');
        
        const grad = ctx.createLinearGradient(0, 0, 0, 256);
        grad.addColorStop(0, '#103060'); grad.addColorStop(0.5, '#1e528e'); grad.addColorStop(1, '#0e2648');
        ctx.fillStyle = grad; ctx.fillRect(0, 0, 512, 256);
        ctx.fillStyle = '#2d6a4f';
        for (let i = 0; i < 40; i++) {
          ctx.beginPath();
          ctx.arc((i * 37) % 512, 60 + ((i * 53) % 140), 20 + ((i * 19) % 40), 0, Math.PI * 2);
          ctx.fill();
        }
        window.TX.day = c.toDataURL('image/jpeg', 0.8);

        ctx.fillStyle = '#02050c'; ctx.fillRect(0, 0, 512, 256);
        ctx.fillStyle = '#ffd166';
        for (let i = 0; i < 60; i++) {
          ctx.fillRect((i * 47) % 512, 60 + ((i * 41) % 140), 2, 2);
        }
        window.TX.night = c.toDataURL('image/jpeg', 0.8);

        ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, 512, 256);
        ctx.fillStyle = '#000000';
        for (let i = 0; i < 40; i++) {
          ctx.beginPath();
          ctx.arc((i * 37) % 512, 60 + ((i * 53) % 140), 20 + ((i * 19) % 40), 0, Math.PI * 2);
          ctx.fill();
        }
        window.TX.water = c.toDataURL('image/jpeg', 0.8);
      }
    }
    ensureTextures();

    // --- Planetary Categories with Unique Palettes & Historical Trajectories (1980–2025: 46 data points) ---
    const CATS = {
      climate: {
        id: 'climate',
        n: 'CLIMATE',
        t: 'GLOBAL SURFACE TEMPERATURE ANOMALY',
        sub: 'NASA GISTEMP & ERA5 Multi-Reanalysis compilation (1980–2025)',
        u: '°C',
        d: 2,
        baseline: '1850–1900 Pre-Industrial',
        sensor: 'NASA Goddard / Copernicus Climate Change Service',
        rate: '+0.24°C / DECADE',
        hex: '#FF5722',
        glow: 'rgba(255, 87, 34, 0.45)',
        subtle: 'rgba(255, 87, 34, 0.14)',
        tint: [1.25, 0.45, 0.18],
        aura1: [1.0, 0.35, 0.12],
        aura2: [1.0, 0.65, 0.2],
        icon: '<path d="M12 2a3 3 0 0 0-3 3v8.17a5 5 0 1 0 6 0V5a3 3 0 0 0-3-3zm0 16a2 2 0 1 1 0-4 2 2 0 0 1 0 4z"/>',
        raw: [
          0.26, 0.32, 0.14, 0.31, 0.16, 0.12, 0.18, 0.32, 0.39, 0.27,
          0.45, 0.41, 0.22, 0.24, 0.32, 0.45, 0.35, 0.48, 0.64, 0.42,
          0.40, 0.54, 0.63, 0.62, 0.54, 0.68, 0.64, 0.66, 0.54, 0.65,
          0.72, 0.61, 0.65, 0.68, 0.75, 0.90, 1.02, 0.92, 0.85, 0.98,
          1.02, 0.85, 0.89, 1.18, 1.45, 1.48
        ]
      },
      oceans: {
        id: 'oceans',
        n: 'OCEANS',
        t: 'SEA SURFACE TEMPERATURE ANOMALY',
        sub: 'NOAA OISST & Ocean Acidification pH Monitoring (1980–2025)',
        u: '°C',
        d: 2,
        baseline: '1981–2010 Climatology Baseline',
        sensor: 'NOAA Coral Reef Watch / Argo Autonomous Float Fleet',
        rate: '+0.18°C / DECADE',
        hex: '#00E5FF',
        glow: 'rgba(0, 229, 255, 0.45)',
        subtle: 'rgba(0, 229, 255, 0.14)',
        tint: [0.15, 0.75, 1.25],
        aura1: [0.0, 0.65, 1.0],
        aura2: [0.1, 0.9, 0.75],
        icon: '<path d="M2 6c3-3 5 3 8 0s5 3 8 0 4 2 4 2M2 12c3-3 5 3 8 0s5 3 8 0 4 2 4 2M2 18c3-3 5 3 8 0s5 3 8 0 4 2 4 2"/>',
        raw: [
          0.12, 0.14, 0.08, 0.18, 0.06, 0.04, 0.08, 0.17, 0.22, 0.15,
          0.22, 0.24, 0.11, 0.14, 0.17, 0.24, 0.19, 0.27, 0.42, 0.23,
          0.21, 0.29, 0.35, 0.36, 0.31, 0.38, 0.36, 0.35, 0.29, 0.37,
          0.41, 0.33, 0.37, 0.39, 0.44, 0.54, 0.62, 0.53, 0.49, 0.58,
          0.60, 0.53, 0.56, 0.78, 0.96, 0.98
        ]
      },
      forests: {
        id: 'forests',
        n: 'FORESTS',
        t: 'GLOBAL INTACT CANOPY INTEGRITY',
        sub: 'Global Canopy Integrity (Global Forest Watch reference index — live API ingestion pending)',
        u: '% BASE',
        d: 1,
        baseline: '100.0% at 1980 Baseline Epoch',
        sensor: 'MODIS/Landsat Reference (Satellite API integration in progress)',
        rate: '-3.1% LOSS / DECADE',
        hex: '#00E676',
        glow: 'rgba(0, 230, 118, 0.45)',
        subtle: 'rgba(0, 230, 118, 0.14)',
        tint: [0.2, 1.15, 0.4],
        aura1: [0.1, 0.95, 0.35],
        aura2: [0.2, 0.85, 0.65],
        icon: '<path d="M12 2L4 12h5l-3 7h12l-3-7h5zM12 19v3"/>',
        raw: [
          100.0, 99.7, 99.3, 99.0, 98.6, 98.2, 97.8, 97.3, 96.9, 96.4,
          96.0, 95.5, 95.1, 94.7, 94.2, 93.8, 93.3, 92.8, 92.1, 91.8,
          91.4, 91.0, 90.5, 90.0, 89.6, 89.1, 88.7, 88.4, 88.1, 87.8,
          87.5, 87.2, 86.9, 86.7, 86.4, 86.0, 85.5, 85.1, 84.7, 84.1,
          83.8, 83.5, 83.1, 82.6, 82.2, 82.0
        ]
      },
      atmosphere: {
        id: 'atmosphere',
        n: 'ATMOSPHERE',
        t: 'CARBON DIOXIDE CONCENTRATION (CO₂)',
        sub: 'Mauna Loa Baseline Observatory Keeling Curve (1980–2025)',
        u: 'PPM',
        d: 1,
        baseline: '280 PPM Pre-Industrial Baseline',
        sensor: 'NOAA Global Monitoring Lab / Scripps Institution',
        rate: '+2.45 PPM / YEAR',
        hex: '#D500F9',
        glow: 'rgba(213, 0, 249, 0.45)',
        subtle: 'rgba(213, 0, 249, 0.14)',
        tint: [0.95, 0.45, 1.2],
        aura1: [0.85, 0.25, 1.0],
        aura2: [0.45, 0.4, 1.0],
        icon: '<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 9 9M8 12a4 4 0 0 1 8 0"/>',
        raw: [
          338.8, 340.1, 341.2, 342.9, 344.4, 345.9, 347.2, 348.9, 351.5, 352.9,
          354.2, 355.6, 356.4, 357.1, 358.8, 360.8, 362.6, 363.7, 366.7, 368.4,
          369.5, 371.1, 373.2, 375.8, 377.5, 379.8, 381.9, 383.8, 385.6, 387.4,
          389.9, 391.7, 393.8, 396.5, 398.6, 400.8, 404.2, 406.6, 408.5, 411.4,
          414.2, 416.4, 418.6, 421.1, 424.2, 425.5
        ]
      },
      cryosphere: {
        id: 'cryosphere',
        n: 'CRYOSPHERE',
        t: 'ARCTIC SEPTEMBER SEA ICE EXTENT',
        sub: 'NSIDC Satellite Microwave Altimetry Index (1980–2025)',
        u: 'M km²',
        d: 2,
        baseline: '1981–2010 Median (6.5 M km²)',
        sensor: 'National Snow & Ice Data Center / CryoSat-2 SAR',
        rate: '-12.8% LOSS / DECADE',
        hex: '#80D8FF',
        glow: 'rgba(128, 216, 255, 0.45)',
        subtle: 'rgba(128, 216, 255, 0.14)',
        tint: [0.6, 0.95, 1.3],
        aura1: [0.5, 0.85, 1.0],
        aura2: [0.95, 0.98, 1.0],
        icon: '<path d="M12 2v20M2 12h20M5 5l14 14M19 5L5 19"/>',
        raw: [
          7.85, 7.25, 7.45, 7.52, 7.17, 6.93, 7.54, 7.48, 7.49, 7.04,
          6.24, 6.55, 7.55, 6.50, 7.18, 6.13, 7.58, 6.74, 6.56, 6.24,
          6.32, 6.75, 5.83, 6.15, 6.05, 5.57, 5.92, 4.30, 4.73, 5.39,
          4.93, 4.63, 3.41, 5.35, 5.28, 4.68, 4.72, 4.87, 4.79, 4.32,
          4.00, 4.92, 4.87, 4.37, 4.28, 4.22
        ]
      },
      methane: {
        id: 'methane',
        n: 'METHANE',
        t: 'ATMOSPHERIC METHANE (CH₄)',
        sub: 'WMO Global Atmosphere Watch & TROPOMI Satellite (1980–2025)',
        u: 'PPB',
        d: 0,
        baseline: '722 PPB Pre-Industrial Baseline',
        sensor: 'Copernicus Sentinel-5P TROPOMI / NOAA Carbon Cycle',
        rate: '+11.5 PPB / YEAR SURGE',
        hex: '#FFD600',
        glow: 'rgba(255, 214, 0, 0.45)',
        subtle: 'rgba(255, 214, 0, 0.14)',
        tint: [1.18, 0.95, 0.15],
        aura1: [1.0, 0.85, 0.12],
        aura2: [0.75, 0.95, 0.25],
        icon: '<path d="M12 2a5 5 0 0 1 5 5v3a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5zM5 14a7 7 0 0 0 14 0M12 18v4"/>',
        raw: [
          1570, 1585, 1600, 1618, 1632, 1648, 1662, 1675, 1690, 1704,
          1716, 1728, 1735, 1740, 1745, 1750, 1756, 1761, 1768, 1774,
          1773, 1772, 1773, 1775, 1777, 1776, 1778, 1785, 1792, 1800,
          1808, 1813, 1819, 1826, 1834, 1845, 1853, 1860, 1869, 1877,
          1889, 1908, 1920, 1928, 1934, 1938
        ]
      }
    };

    for (const k in CATS) {
      const c = CATS[k];
      c.min = Math.min(...c.raw);
      c.max = Math.max(...c.raw);
    }

    const getVal = (catKey, year) => {
      const c = CATS[catKey];
      const idxFloat = clamp(year - 1980, 0, 45);
      const i = Math.floor(idxFloat);
      const frac = idxFloat - i;
      if (i >= 45) return c.raw[45];
      return lerp(c.raw[i], c.raw[i + 1], frac);
    };

    const getNorm = (catKey, year) => {
      const c = CATS[catKey];
      return clamp((getVal(catKey, year) - c.min) / (c.max - c.min), 0, 1);
    };

    // --- Landmark Milestones across 1980–2025 ---
    const MILESTONES = [
      { year: 1988, title: '1988 · IPCC Formed', tag: 'POLITICAL', desc: 'UN establishes IPCC following James Hansen’s historic greenhouse testimony.' },
      { year: 1992, title: '1992 · Rio Earth Summit', tag: 'ACCORD', desc: '154 nations sign UNFCCC framework treaty on greenhouse stabilization.' },
      { year: 1997, title: '1997 · Kyoto Protocol', tag: 'POLICY', desc: 'First legally binding greenhouse gas reduction treaty established.' },
      { year: 1998, title: '1998 · Super El Niño', tag: 'CLIMATE EVENT', desc: 'Intense Pacific heat pulse drives unprecedented global marine bleaching.' },
      { year: 2007, title: '2007 · Arctic Ice Drop', tag: 'CRYOSPHERE', desc: 'Summer Arctic sea ice collapses to shocking record minimum.' },
      { year: 2015, title: '2015 · Paris Climate Agreement', tag: 'TREATY', desc: 'Historic 196-nation accord commits to pursue limiting warming to 1.5°C.' },
      { year: 2020, title: '2020 · COVID Lockdown Dip', tag: 'EMISSIONS', desc: 'Global industrial slowdown briefly reduces fossil fuel emissions by 5.4%.' },
      { year: 2023, title: '2023 · Hottest Year on Record', tag: 'RECORD', desc: 'Global surface temperature surges to +1.45°C above baseline.' },
      { year: 2024, title: '2024 · 1.5°C Threshold Sequence', tag: 'CRITICAL', desc: '12 consecutive months exceeding the 1.5°C threshold recorded by Copernicus.' }
    ];

    // --- Comprehensive Global Landmark Biomes (18 Regions) ---
    const HOTSPOTS = [
      {
        id: 'amazon',
        n: 'Amazon Basin',
        location: 'Brazil · South America',
        lat: -3.4,
        lon: -62.2,
        cat: 'forests',
        badge: 'CANOPY BIOPHONY',
        soundDesc: 'Synthesized rainforest biophony with avian FM sweeps and moist canopy resonance.',
        soundType: 'rainforest',
        icon: '🌿'
      },
      {
        id: 'patagonia',
        n: 'Patagonian Ice Fields',
        location: 'Chile & Argentina · South America',
        lat: -49.5,
        lon: -73.5,
        cat: 'cryosphere',
        badge: 'SOUTHERN ICE FIELD',
        soundDesc: 'Glacial creaking, sub-zero katabatic wind gusts, and southern maritime resonance.',
        soundType: 'polar',
        icon: '❄️'
      },
      {
        id: 'pnw',
        n: 'Pacific Northwest Rainforest',
        location: 'USA & Canada · North America',
        lat: 47.5,
        lon: -122.3,
        cat: 'forests',
        badge: 'TEMPERATE RAINFOREST',
        soundDesc: 'Temperate coastal canopy, rainfall flutter, and dense conifer forest resonance.',
        soundType: 'temperate',
        icon: '🌲'
      },
      {
        id: 'mojave',
        n: 'Mojave Desert & Death Valley',
        location: 'California · North America',
        lat: 36.2,
        lon: -116.8,
        cat: 'climate',
        badge: 'THERMAL BASIN',
        soundDesc: 'Extreme heat acoustic shimmer, arid wind friction, and sun-baked earth drone.',
        soundType: 'desert',
        icon: '🏜️'
      },
      {
        id: 'svalbard',
        n: 'Arctic Svalbard',
        location: 'Norway · High Arctic',
        lat: 78.5,
        lon: 16.0,
        cat: 'cryosphere',
        badge: 'GLACIAL HARMONICS',
        soundDesc: 'Sub-zero resonant wind filter sweeps, high crystalline ice chimes, and deep crevicular drone.',
        soundType: 'polar',
        icon: '❄️'
      },
      {
        id: 'scandinavia',
        n: 'Scandinavian Taiga',
        location: 'Sweden & Finland · Northern Europe',
        lat: 64.0,
        lon: 17.5,
        cat: 'forests',
        badge: 'BOREAL CONIFER',
        soundDesc: 'High latitude pine forest hum, gentle sub-arctic breeze, and mossy ground acoustic absorption.',
        soundType: 'taiga',
        icon: '🌲'
      },
      {
        id: 'mediterranean',
        n: 'Mediterranean Marine Basin',
        location: 'Southern Europe',
        lat: 38.5,
        lon: 15.0,
        cat: 'oceans',
        badge: 'COASTAL HEATWAVE',
        soundDesc: 'Warm coastal currents, tidal rhythmic modulation, and marine thermal swelling.',
        soundType: 'coral',
        icon: '🌊'
      },
      {
        id: 'sahara',
        n: 'Sahara Desert (Erg Chebbi)',
        location: 'Morocco · North Africa',
        lat: 25.0,
        lon: 10.0,
        cat: 'climate',
        badge: 'ARID THERMAL DUNE',
        soundDesc: 'Microtonal dry drone in Phrygian dominant with granular sand-friction wind sweeps and warm overtones.',
        soundType: 'desert',
        icon: '🏜️'
      },
      {
        id: 'congo',
        n: 'Congo Basin',
        location: 'Democratic Republic of Congo',
        lat: 0.5,
        lon: 24.0,
        cat: 'forests',
        badge: 'EQUATORIAL PULSE',
        soundDesc: 'Polyrhythmic triangle-wave ambient pulses, equatorial moisture resonance, and insect cadence sweeps.',
        soundType: 'rainforest',
        icon: '🌲'
      },
      {
        id: 'madagascar',
        n: 'Madagascar Coastal Biome',
        location: 'Madagascar · Indian Ocean',
        lat: -18.5,
        lon: 47.5,
        cat: 'oceans',
        badge: 'ISLAND BIOSPHERE',
        soundDesc: 'Tropical coastal swells, coral hydrophone bubbling, and endemic nocturnal biophony.',
        soundType: 'coral',
        icon: '🪸'
      },
      {
        id: 'himalayas',
        n: 'Himalayan Khumbu Glacier',
        location: 'Nepal & Tibet · High Asia',
        lat: 28.0,
        lon: 86.9,
        cat: 'cryosphere',
        badge: 'THIRD POLE CRYOSPHERE',
        soundDesc: 'High altitude thin-air whistling, singing-bowl overtone drone, and glacial stream resonance.',
        soundType: 'alpine',
        icon: '🏔️'
      },
      {
        id: 'siberia',
        n: 'Siberian Permafrost Taiga',
        location: 'Sakha Republic · Russia',
        lat: 63.5,
        lon: 120.0,
        cat: 'methane',
        badge: 'PERMAFROST THAW',
        soundDesc: 'Sub-arctic boreal forest wind, permafrost thaw micro-bubbling, and low-frequency bog resonance.',
        soundType: 'taiga',
        icon: '🌲'
      },
      {
        id: 'borneo',
        n: 'Sundaland Borneo Rainforest',
        location: 'Indonesia & Malaysia',
        lat: 1.0,
        lon: 114.0,
        cat: 'forests',
        badge: 'TROPICAL PEATLAND',
        soundDesc: 'Ancient dipterocarp forest biophony, peat swamp moisture resonance, and primate calls.',
        soundType: 'rainforest',
        icon: '🌿'
      },
      {
        id: 'barrier',
        n: 'Great Barrier Reef',
        location: 'Coral Sea · Australia',
        lat: -18.2,
        lon: 147.7,
        cat: 'oceans',
        badge: 'CORAL HYDROPHONE',
        soundDesc: 'Aquatic micro-bubble impulse clicks, gentle tidal chorus modulation, and marine shimmer pads.',
        soundType: 'coral',
        icon: '🪸'
      },
      {
        id: 'outback',
        n: 'Australian Red Centre',
        location: 'Northern Territory · Australia',
        lat: -23.7,
        lon: 133.8,
        cat: 'climate',
        badge: 'ARID OUTBACK',
        soundDesc: 'Dry ancient bedrock harmonics, thermal dust devils, and deep red desert drone.',
        soundType: 'desert',
        icon: '🏜️'
      },
      {
        id: 'mariana',
        n: 'Mariana Trench',
        location: 'Western Pacific Ocean',
        lat: 11.3,
        lon: 142.2,
        cat: 'oceans',
        badge: 'ABYSSAL SONAR',
        soundDesc: '48 Hz tectonic sub-bass drone with resonant acoustic sonar ping echoes and oceanic pressure delays.',
        soundType: 'ocean_abyss',
        icon: '🌊'
      },
      {
        id: 'maunaloa',
        n: 'Mauna Loa Observatory',
        location: 'Hawaii · Pacific Ocean',
        lat: 19.5,
        lon: -155.6,
        cat: 'atmosphere',
        badge: 'KEELING PURE SINE',
        soundDesc: 'High-altitude sinusoidal drone tuned directly to real-time CO₂ PPM with ethereal harmonic overtone.',
        soundType: 'atmosphere',
        icon: '🌋'
      },
      {
        id: 'ross',
        n: 'Antarctic Ross Ice Shelf',
        location: 'Antarctica · South Pole',
        lat: -81.5,
        lon: 175.0,
        cat: 'cryosphere',
        badge: 'CRYOGENIC CALVING',
        soundDesc: '36 Hz sub-pulse, cryogenic ice fractures, and sub-zero katabatic wind gusts.',
        soundType: 'polar',
        icon: '🧊'
      }
    ];

    // --- State Machine ---
    const st = {
      cat: 'climate',
      year: 1990,
      play: false,
      region: null,
      customMarker: null,
      scale: 'pent',
      rotSpeed: 'med',
      mute: false,
      auraIntensity: 1.0,
      cruise: 'off',
      scanMode: false,
      dockPos: 'bottom'
    };

    // --- Global Biome Classification Engine for ANY Clicked Point on Earth ---
    function classifyGeoPoint(lat, lon) {
      const absLat = Math.abs(lat);
      
      if (absLat >= 68) {
        const isNorth = lat > 0;
        return {
          name: isNorth ? 'Arctic High Glacial Cap' : 'Antarctic Polar Ice Sheet',
          type: 'cryosphere',
          badge: 'POLAR CRYOSPHERE',
          icon: '❄️',
          soundType: 'polar',
          desc: 'Sub-zero resonant katabatic wind sweeps, brittle ice crackle transients, and calving sub-harmonics.'
        };
      }
      
      if (absLat >= 54) {
        if (lat < 0) {
          return {
            name: 'Southern Circumpolar Ocean Abyss',
            type: 'oceans',
            badge: 'CIRCUMPOLAR DEEP',
            icon: '🌊',
            soundType: 'ocean_abyss',
            desc: 'Deep circumpolar current swells, 44 Hz sub-bass rumble, and violent high-latitude maritime winds.'
          };
        } else {
          return {
            name: (lon > 30 && lon < 140) ? 'Siberian Boreal Permafrost Taiga' : 'Sub-Arctic Boreal Forest',
            type: 'forests',
            badge: 'BOREAL TAIGA & PERMAFROST',
            icon: '🌲',
            soundType: 'taiga',
            desc: 'Permafrost thaw micro-bubbling, sub-arctic pine needle wind friction, and low frequency peatland hum.'
          };
        }
      }
      
      const isSaharaArabia = (lat >= 12 && lat <= 35 && lon >= -17 && lon <= 60);
      const isAustraliaOutback = (lat <= -18 && lat >= -32 && lon >= 115 && lon <= 145);
      const isGobi = (lat >= 36 && lat <= 46 && lon >= 85 && lon <= 115);
      const isMojave = (lat >= 30 && lat <= 38 && lon >= -118 && lon <= -110);
      const isAtacama = (lat <= -18 && lat >= -28 && lon >= -72 && lon <= -67);
      
      if (isSaharaArabia || isAustraliaOutback || isGobi || isMojave || isAtacama) {
        const dName = isSaharaArabia ? 'Sahara & Arabian Thermal Dune Belt' :
                      isAustraliaOutback ? 'Australian Arid Outback Basin' :
                      isGobi ? 'Gobi Cold Desert Plateau' :
                      isMojave ? 'Mojave & Great Basin Desert' : 'Atacama Hyper-Arid Desert';
        return {
          name: dName,
          type: 'climate',
          badge: 'ARID THERMAL ZONE',
          icon: '🏜️',
          soundType: 'desert',
          desc: 'High-temperature thermal air shimmer, dry granular sand friction, and microtonal Phrygian harmonics.'
        };
      }
      
      const isAmazon = (lat >= -15 && lat <= 8 && lon >= -80 && lon <= -45);
      const isCongo = (lat >= -8 && lat <= 8 && lon >= 10 && lon <= 35);
      const isSEAsia = (lat >= -10 && lat <= 15 && lon >= 95 && lon <= 145);
      
      if (isAmazon || isCongo || isSEAsia) {
        const fName = isAmazon ? 'Amazonian Wet Canopy Basin' :
                      isCongo ? 'Congo Equatorial Peatland' : 'Sundaland Tropical Rainforest';
        return {
          name: fName,
          type: 'forests',
          badge: 'EQUATORIAL BIOPHONY',
          icon: '🌿',
          soundType: 'rainforest',
          desc: 'Dense multi-layered canopy biophony with bird chirp FM sweeps, cicada resonance, and rainfall flutter.'
        };
      }
      
      const isHimalayas = (lat >= 26 && lat <= 36 && lon >= 75 && lon <= 100);
      const isAndes = (lat >= -50 && lat <= 10 && lon >= -76 && lon <= -65);
      if (isHimalayas || isAndes) {
        return {
          name: isHimalayas ? 'Himalayan High Peak Cryosphere' : 'Andean Cordillera & Glaciers',
          type: 'cryosphere',
          badge: 'ALPINE PEAK ELEVATION',
          icon: '🏔️',
          soundType: 'alpine',
          desc: 'Thin atmospheric altitude whistling, glacial stream resonance, and harmonic singing bowl tones.'
        };
      }
      
      const isPacific = (lon < -70 && lon > -180) || (lon > 120 && lon <= 180);
      const isAtlantic = (lon >= -70 && lon <= 20 && absLat < 60);
      const isIndian = (lon >= 40 && lon <= 115 && lat < 25 && lat > -50);
      
      const isLandApprox = (
        (lat >= 25 && lat <= 60 && lon >= -125 && lon <= -65) ||
        (lat >= 36 && lat <= 60 && lon >= -10 && lon <= 40) ||
        (lat >= 15 && lat <= 55 && lon >= 40 && lon <= 135) ||
        (lat >= -35 && lat <= 35 && lon >= -17 && lon <= 50) ||
        (lat >= -55 && lat <= 12 && lon >= -80 && lon <= -35) ||
        (lat >= -40 && lat <= -11 && lon >= 113 && lon <= 154)
      );
      
      if (!isLandApprox) {
        const oceanName = isPacific ? 'Pacific Abyssal Pelagic Basin' :
                          isAtlantic ? 'Atlantic Deep Ocean Drift' :
                          isIndian ? 'Indian Ocean Tropical Waters' : 'Global Ocean Pelagic Waters';
        return {
          name: oceanName,
          type: 'oceans',
          badge: 'PELAGIC DEEP OCEAN',
          icon: '🌊',
          soundType: 'ocean_abyss',
          desc: 'Hydrothermal sub-bass swells (45 Hz), distant acoustic sonar echo pings, and oceanic pressure drones.'
        };
      }
      
      return {
        name: 'Temperate Continental Biosphere',
        type: 'climate',
        badge: 'TEMPERATE REGION',
        icon: '🍃',
        soundType: 'temperate',
        desc: 'Breezy canopy resonance, gentle acoustic harmonics, and seasonal temperature variance drone.'
      };
    }

    // --- Three.js Setup & Robust Fallback Management ---
    let R, scene, cam, planet, earth, ring, auraMesh, starPoints, U, auraU;
    let ok = false;
    let zT = 3.6, zoom = 1.0;
    let drag = false, lx = 0, ly = 0, tgt = null;
    let pointerStartedOnGlobe = false;
    let movedDistance = 0;

    let raycaster = null;
    let mouse = null;

    let ctx2d = null;
    let map2DImage = null;
    let map2DLoaded = false;

    function activate2DFallback() {
      ok = false;
      let canvas = $('#gl');
      if (canvas) {
        try {
          ctx2d = canvas.getContext('2d');
        } catch (e) {}
        if (!ctx2d) {
          const freshCanvas = document.createElement('canvas');
          freshCanvas.id = 'gl';
          freshCanvas.setAttribute('aria-label', 'Interactive 2D Earth Observatory Map');
          freshCanvas.className = canvas.className;
          canvas.parentNode.replaceChild(freshCanvas, canvas);
          ctx2d = freshCanvas.getContext('2d');
          bindCanvasInteraction(freshCanvas);
        }
      }
      if (!map2DImage && typeof window.TX !== 'undefined' && window.TX.day) {
        map2DImage = new Image();
        map2DImage.onload = () => { map2DLoaded = true; };
        map2DImage.src = window.TX.day;
      }
      const fb = $('#fb');
      if (fb) fb.style.display = 'block';
    }

    function render2DFallbackMap(now, dt, normVal, c) {
      const canvas = $('#gl');
      if (!canvas) return;
      if (!ctx2d) {
        ctx2d = canvas.getContext('2d');
        if (!ctx2d) return;
      }

      const W = window.innerWidth;
      const H = window.innerHeight;
      if (canvas.width !== W || canvas.height !== H) {
        canvas.width = W;
        canvas.height = H;
      }

      // 1. Deep space background
      ctx2d.fillStyle = '#02040A';
      ctx2d.fillRect(0, 0, W, H);

      // Radial observatory glow behind map
      const radGrad = ctx2d.createRadialGradient(W / 2, H / 2, 40, W / 2, H / 2, Math.max(W, H) * 0.65);
      radGrad.addColorStop(0, '#061022');
      radGrad.addColorStop(0.6, '#030712');
      radGrad.addColorStop(1, '#010206');
      ctx2d.fillStyle = radGrad;
      ctx2d.fillRect(0, 0, W, H);

      // Deep space subtle stars
      ctx2d.fillStyle = 'rgba(200, 220, 255, 0.4)';
      for (let i = 0; i < 40; i++) {
        const sx = ((i * 137.5) % W);
        const sy = ((i * 269.3 + now * 0.005) % H);
        ctx2d.fillRect(sx, sy, 1.2, 1.2);
      }

      // 2. Centered equirectangular map box
      const mapW = Math.min(W * 0.90, H * 1.80);
      const mapH = mapW * 0.5;
      const mapX = (W - mapW) / 2;
      const mapY = (H - mapH) / 2;

      // Draw map frame & shadow
      ctx2d.save();
      ctx2d.shadowColor = 'rgba(0, 0, 0, 0.85)';
      ctx2d.shadowBlur = 30;
      ctx2d.fillStyle = '#050D1A';
      ctx2d.fillRect(mapX, mapY, mapW, mapH);
      ctx2d.restore();

      // Draw day texture image
      if (map2DLoaded && map2DImage) {
        ctx2d.drawImage(map2DImage, mapX, mapY, mapW, mapH);
      } else {
        // Fallback continent grid if image still decoding
        ctx2d.fillStyle = '#08172E';
        ctx2d.fillRect(mapX, mapY, mapW, mapH);
      }

      // Dynamic planetary anomaly color tint overlay
      ctx2d.save();
      ctx2d.fillStyle = c.hex;
      ctx2d.globalAlpha = 0.22 * normVal;
      ctx2d.fillRect(mapX, mapY, mapW, mapH);
      ctx2d.restore();

      // 3. Solar Day/Night Terminator wave
      ctx2d.save();
      ctx2d.beginPath();
      ctx2d.moveTo(mapX, mapY + mapH);
      const sunPhase = (now * 0.00008) % (Math.PI * 2);
      for (let x = 0; x <= mapW; x += 8) {
        const rad = (x / mapW) * Math.PI * 2 + sunPhase;
        const waveY = mapY + (mapH / 2) + Math.sin(rad) * (mapH * 0.38);
        ctx2d.lineTo(mapX + x, waveY);
      }
      ctx2d.lineTo(mapX + mapW, mapY + mapH);
      ctx2d.closePath();
      ctx2d.fillStyle = 'rgba(2, 4, 10, 0.52)';
      ctx2d.fill();
      ctx2d.restore();

      // 4. Equirectangular coordinate grid
      ctx2d.save();
      ctx2d.strokeStyle = 'rgba(255, 255, 255, 0.10)';
      ctx2d.lineWidth = 1;
      ctx2d.setLineDash([4, 6]);

      // Tropics (+23.5°, -23.5°)
      const tropicN = mapY + ((90 - 23.5) / 180) * mapH;
      const tropicS = mapY + ((90 - (-23.5)) / 180) * mapH;
      ctx2d.beginPath();
      ctx2d.moveTo(mapX, tropicN); ctx2d.lineTo(mapX + mapW, tropicN);
      ctx2d.moveTo(mapX, tropicS); ctx2d.lineTo(mapX + mapW, tropicS);
      ctx2d.stroke();

      // Equator (Solid vibrant accent)
      ctx2d.setLineDash([]);
      ctx2d.strokeStyle = 'rgba(128, 216, 255, 0.35)';
      ctx2d.lineWidth = 1.2;
      const equatorY = mapY + mapH / 2;
      ctx2d.beginPath();
      ctx2d.moveTo(mapX, equatorY); ctx2d.lineTo(mapX + mapW, equatorY);
      ctx2d.stroke();

      // Prime Meridian & Longitude marks
      ctx2d.setLineDash([3, 6]);
      ctx2d.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      for (let lon = -120; lon <= 120; lon += 60) {
        const lx = mapX + ((lon + 180) / 360) * mapW;
        ctx2d.beginPath();
        ctx2d.moveTo(lx, mapY); ctx2d.lineTo(lx, mapY + mapH);
        ctx2d.stroke();
      }

      // Outer map border
      ctx2d.setLineDash([]);
      ctx2d.strokeStyle = 'rgba(255, 255, 255, 0.22)';
      ctx2d.lineWidth = 1;
      ctx2d.strokeRect(mapX, mapY, mapW, mapH);
      ctx2d.restore();

      // 5. Hotspot beacons & live DOM positioning
      const allMarkers = [...HOTSPOTS];
      if (st.region && st.region.isCustom && st.region.el) {
        allMarkers.push(st.region);
      }

      allMarkers.forEach((h, idx) => {
        const sx = mapX + ((h.lon + 180) / 360) * mapW;
        const sy = mapY + ((90 - h.lat) / 180) * mapH;

        if (h.el) {
          h.el.style.transform = `translate(${sx}px, ${sy}px)`;
          h.el.style.display = 'block';
        }

        // Draw animated concentric pulse on canvas
        const isSelected = st.region && (st.region.id === h.id || st.region.n === h.n);
        const pulse = (Math.sin(now * 0.004 + idx) + 1) * 0.5;
        const radius = isSelected ? (8 + pulse * 8) : (4 + pulse * 4);

        ctx2d.save();
        ctx2d.beginPath();
        ctx2d.arc(sx, sy, radius, 0, Math.PI * 2);
        ctx2d.strokeStyle = isSelected ? '#00E676' : (h.cat && CATS[h.cat] ? CATS[h.cat].hex : c.hex);
        ctx2d.lineWidth = isSelected ? 2 : 1.2;
        ctx2d.shadowColor = ctx2d.strokeStyle;
        ctx2d.shadowBlur = 8;
        ctx2d.stroke();

        ctx2d.beginPath();
        ctx2d.arc(sx, sy, isSelected ? 3.5 : 2, 0, Math.PI * 2);
        ctx2d.fillStyle = '#FFFFFF';
        ctx2d.fill();
        ctx2d.restore();
      });

      // 6. Observatory status watermark
      ctx2d.save();
      ctx2d.font = '10px "JetBrains Mono", monospace';
      ctx2d.fillStyle = 'rgba(140, 160, 186, 0.7)';
      ctx2d.fillText('● 2D PLANETARY OBSERVATORY · EQUIRECTANGULAR PROJECTION', mapX + 8, mapY - 8);
      ctx2d.restore();
    }

    function initWebGL() {
      if (typeof THREE === 'undefined') {
        console.warn('Three.js library is not available. Activating 2D fallback mode.');
        activate2DFallback();
        return;
      }

      try {
        const canvas = $('#gl');
        R = new THREE.WebGLRenderer({
          canvas,
          alpha: true,
          antialias: true,
          powerPreference: 'high-performance',
          failIfMajorPerformanceCaveat: false
        });
        R.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        canvas.addEventListener('webglcontextlost', e => {
          e.preventDefault();
          console.warn('WebGL context lost. Activating 2D fallback map.');
          activate2DFallback();
        }, false);

        canvas.addEventListener('webglcontextrestored', () => {
          console.info('WebGL context restored. Re-initializing 3D observatory.');
          initWebGL();
        }, false);

        scene = new THREE.Scene();
        cam = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
        cam.position.z = 3.6;

        raycaster = new THREE.Raycaster();
        mouse = new THREE.Vector2();

        planet = new THREE.Group();
        scene.add(planet);

        const vs = `
          varying vec3 vP, vN;
          varying vec2 vUv;
          void main() {
            vP = position;
            vUv = uv;
            vN = normalize(normalMatrix * normal);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `;

        const fs = `
          #ifdef GL_FRAGMENT_PRECISION_HIGH
          precision highp float;
          #else
          precision mediump float;
          #endif
          varying vec3 vP, vN;
          varying vec2 vUv;
          uniform vec3 uSun, uTint;
          uniform float uTime, uV;
          uniform sampler2D uDay, uNight, uWater;
          
          float h(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
          float n3(vec3 p) {
            vec3 i = floor(p), f = fract(p);
            f = f * f * (3.0 - 2.0 * f);
            return mix(
              mix(mix(h(i), h(i + vec3(1, 0, 0)), f.x), mix(h(i + vec3(0, 1, 0)), h(i + vec3(1, 1, 0)), f.x), f.y),
              mix(mix(h(i + vec3(0, 0, 1)), h(i + vec3(1, 0, 1)), f.x), mix(h(i + vec3(0, 1, 1)), h(i + vec3(1, 1, 1)), f.x), f.y),
              f.z
            );
          }
          float fbm(vec3 p) {
            float a = 0.5, s = 0.0;
            for (int i = 0; i < 5; i++) {
              s += a * n3(p);
              p *= 2.03;
              a *= 0.5;
            }
            return s;
          }
          void main() {
            vec3 p = normalize(vP), N = normalize(vN);
            float d = dot(N, uSun);
            vec3 dy = texture2D(uDay, vUv).rgb;
            vec3 ni = texture2D(uNight, vUv).rgb;
            float w = texture2D(uWater, vUv).r;
            
            dy = pow(dy, vec3(1.1)) * 1.12;
            dy = mix(dy, dy * uTint * 1.6, 0.28 * uV * (1.0 - w * 0.5));
            vec3 o = dy * (0.04 + 1.15 * max(d, 0.0));
            
            vec3 Hh = normalize(uSun + vec3(0.0, 0.0, 1.0));
            o += vec3(0.9, 0.95, 1.0) * pow(max(dot(N, Hh), 0.0), 70.0) * w * 0.75 * step(0.0, d);
            
            float cl = smoothstep(0.50, 0.82, fbm(p * 3.2 + vec3(uTime * 0.012, 0.0, 0.0) + 20.0));
            o = mix(o, vec3(0.04 + max(d, 0.0) * 0.96), cl * 0.6);
            
            o += pow(ni, vec3(1.3)) * vec3(1.0, 0.82, 0.55) * 2.2 * smoothstep(0.1, -0.2, d) * (1.0 - cl * 0.6);
            o += vec3(1.0, 0.45, 0.2) * smoothstep(0.0, 0.12, d) * smoothstep(0.3, 0.08, d) * 0.07;
            
            float fr = pow(1.0 - max(N.z, 0.0), 3.0);
            o += uTint * fr * 0.9 * (0.3 + max(d + 0.3, 0.0));
            gl_FragColor = vec4(o, 1.0);
          }
        `;

        U = {
          uSun: { value: new THREE.Vector3(-0.7, 0.25, 0.65).normalize() },
          uTime: { value: 0 },
          uTint: { value: new THREE.Vector3(1.2, 0.45, 0.18) },
          uV: { value: 0 },
          uDay: { value: null },
          uNight: { value: null },
          uWater: { value: null }
        };

        earth = new THREE.Mesh(
          new THREE.SphereGeometry(1, 96, 96),
          new THREE.ShaderMaterial({ vertexShader: vs, fragmentShader: fs, uniforms: U })
        );
        earth.rotation.x = 0.3;
        earth.rotation.y = -1.9;
        planet.add(earth);

        const tl = new THREE.TextureLoader();
        [['uDay', 'day'], ['uNight', 'night'], ['uWater', 'water']].forEach(([u, k]) => {
          if (window.TX && window.TX[k]) {
            tl.load(window.TX[k], t => {
              if (R && R.capabilities) {
                t.anisotropy = R.capabilities.getMaxAnisotropy();
              }
              U[u].value = t;
            });
          }
        });

        const auraFs = `
          varying vec3 vP, vN;
          uniform vec3 uAura1, uAura2;
          uniform float uIntensity;
          void main() {
            float i = clamp(pow(max(0.60 - dot(normalize(vN), vec3(0.0, 0.0, 1.0)), 0.0), 3.2) * 2.2 * uIntensity, 0.0, 1.0);
            float a = smoothstep(0.35, 0.95, vP.y / 1.14);
            vec3 c = mix(uAura1, uAura2, a * 0.8);
            gl_FragColor = vec4(c * i, i);
          }
        `;
        auraU = {
          uAura1: { value: new THREE.Vector3(1.0, 0.35, 0.12) },
          uAura2: { value: new THREE.Vector3(1.0, 0.65, 0.2) },
          uIntensity: { value: 1.0 }
        };

        auraMesh = new THREE.Mesh(
          new THREE.SphereGeometry(1.14, 64, 64),
          new THREE.ShaderMaterial({
            vertexShader: vs,
            fragmentShader: auraFs,
            uniforms: auraU,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending,
            transparent: true,
            depthWrite: false
          })
        );
        planet.add(auraMesh);

        const starGeom = new THREE.BufferGeometry();
        const starPos = [];
        for (let i = 0; i < 900; i++) {
          const t = Math.random() * Math.PI * 2;
          const u = Math.random() * 2 - 1;
          const r = Math.sqrt(1 - u * u);
          const m = 22 + Math.random() * 20;
          starPos.push(m * r * Math.cos(t), m * u, m * r * Math.sin(t));
        }
        starGeom.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
        starPoints = new THREE.Points(
          starGeom,
          new THREE.PointsMaterial({ color: 0x8CA0BA, size: 0.11, transparent: true, opacity: 0.65 })
        );
        scene.add(starPoints);

        ring = new THREE.Mesh(
          new THREE.RingGeometry(1.52, 1.528, 128),
          new THREE.MeshBasicMaterial({ color: 0xFF5722, transparent: true, opacity: 0.35, side: THREE.DoubleSide })
        );
        ring.rotation.x = 1.25;
        planet.add(ring);

        ok = true;
        const fb = $('#fb');
        if (fb) fb.style.display = 'none';

      } catch (err) {
        console.warn('WebGL initialization failed, activating 2D fallback:', err);
        activate2DFallback();
      }
    }

    const latLonToVec3 = (lat, lon) => {
      const phi = lat * (Math.PI / 180);
      const theta = lon * (Math.PI / 180);
      const x = Math.cos(phi) * Math.cos(theta);
      const y = Math.sin(phi);
      const z = -Math.cos(phi) * Math.sin(theta);
      
      if (typeof THREE !== 'undefined') {
        return new THREE.Vector3(x, y, z);
      }
      return {
        x, y, z,
        clone() { return latLonToVec3(lat, lon); },
        applyEuler() { return this; },
        multiplyScalar(s) { this.x *= s; this.y *= s; this.z *= s; return this; },
        add() { return this; },
        dot() { return 1; },
        project() {}
      };
    };

    function initHotspotBeacons() {
      const container = $('#hsb');
      container.innerHTML = '';
      HOTSPOTS.forEach(h => {
        h.v = latLonToVec3(h.lat, h.lon);
        const el = document.createElement('div');
        el.className = 'hs-marker';
        el.setAttribute('aria-label', h.n);
        el.innerHTML = `
          <div class="hs-tooltip">
            <b>${h.icon} ${h.n}</b>
            <small>${h.badge}</small>
          </div>
        `;
        el.addEventListener('pointerdown', e => e.stopPropagation());
        el.addEventListener('pointerup', e => e.stopPropagation());
        el.onclick = (e) => {
          e.stopPropagation();
          selectRegion(h);
        };
        container.appendChild(el);
        h.el = el;
      });
    }

    function getEarthIntersect(clientX, clientY) {
      if (!ok) {
        const canvas = $('#gl');
        if (!canvas) return null;
        const rect = canvas.getBoundingClientRect();
        const mapW = Math.min(rect.width * 0.90, rect.height * 1.80);
        const mapH = mapW * 0.5;
        const mapX = (rect.width - mapW) / 2;
        const mapY = (rect.height - mapH) / 2;
        const px = clientX - rect.left;
        const py = clientY - rect.top;

        if (px >= mapX && px <= mapX + mapW && py >= mapY && py <= mapY + mapH) {
          const u = (px - mapX) / mapW;
          const v = (py - mapY) / mapH;
          const lon = clamp((u * 360) - 180, -180, 180);
          const lat = clamp(90 - (v * 180), -90, 90);
          return { hit: null, lat, lon };
        }
        return null;
      }

      if (!earth || !cam || !R || !raycaster || !mouse) return null;
      const rect = R.domElement.getBoundingClientRect();
      mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, cam);
      const intersects = raycaster.intersectObject(earth);
      if (intersects.length > 0) {
        const hit = intersects[0];
        const local = hit.point.clone();
        earth.worldToLocal(local);
        local.normalize();
        const lat = Math.asin(clamp(local.y, -1, 1)) * (180 / Math.PI);
        const lon = Math.atan2(-local.z, local.x) * (180 / Math.PI);
        return { hit, lat, lon };
      }
      return null;
    }

    function handleEarthClick(clientX, clientY) {
      const result = getEarthIntersect(clientX, clientY);
      if (!result) return;
      const { lat, lon } = result;
      const geo = classifyGeoPoint(lat, lon);

      const latStr = Math.abs(lat).toFixed(1) + '°' + (lat >= 0 ? 'N' : 'S');
      const lonStr = Math.abs(lon).toFixed(1) + '°' + (lon >= 0 ? 'E' : 'W');

      const customSpot = {
        id: 'custom_' + Date.now(),
        n: geo.name,
        location: `${latStr}, ${lonStr}`,
        lat,
        lon,
        cat: geo.type,
        badge: geo.badge,
        soundDesc: geo.desc,
        soundType: geo.soundType,
        icon: geo.icon,
        isCustom: true
      };

      selectRegion(customSpot);
    }

    function updateScannerHover(clientX, clientY) {
      const reticle = $('#scanner-reticle');
      const pill = $('#scanner-pill');
      if (!st.scanMode) {
        reticle.style.display = 'none';
        pill.style.display = 'none';
        return;
      }

      const result = getEarthIntersect(clientX, clientY);
      if (result) {
        reticle.style.display = 'grid';
        reticle.style.left = clientX + 'px';
        reticle.style.top = clientY + 'px';

        pill.style.display = 'block';
        pill.style.left = Math.min(clientX + 28, window.innerWidth - 220) + 'px';
        pill.style.top = Math.max(clientY - 12, 60) + 'px';

        const { lat, lon } = result;
        const geo = classifyGeoPoint(lat, lon);
        const latStr = Math.abs(lat).toFixed(1) + '°' + (lat >= 0 ? 'N' : 'S');
        const lonStr = Math.abs(lon).toFixed(1) + '°' + (lon >= 0 ? 'E' : 'W');
        pill.textContent = `${geo.icon} ${latStr}, ${lonStr} · ${geo.badge}`;

        if (audio && st.play) {
          const now = audio.ctx.currentTime;
          if (audio.panner && audio.panner.pan) {
            audio.panner.pan.setTargetAtTime(clamp(lon / 180, -1, 1), now, 0.08);
          }
          const basePitch = clamp(Math.abs(lat) / 90, 0, 1);
          const filterFreq = 600 + (1 - basePitch) * 2400;
          audio.primaryFilter.frequency.setTargetAtTime(filterFreq, now, 0.1);
        }
      } else {
        reticle.style.display = 'none';
        pill.style.display = 'none';
      }
    }

    function onResize() {
      const W = window.innerWidth;
      const H = window.innerHeight;
      
      if (ok && R && cam) {
        R.setSize(W, H, false);
        cam.aspect = W / H;
        cam.updateProjectionMatrix();
        const isNarrow = W / H < 0.85;
        zT = (isNarrow ? 5.2 : 3.6) * zoom;
        planet.position.y = isNarrow ? 0.35 : 0;
      }

      if (st.dockPos === 'free') {
        const leftVal = parseInt(deck.style.left) || (W / 2 - deck.offsetWidth / 2);
        const topVal = parseInt(deck.style.top) || (H - deck.offsetHeight - 20);
        deck.style.left = clamp(leftVal, 10, Math.max(10, W - deck.offsetWidth - 10)) + 'px';
        deck.style.top = clamp(topVal, 10, Math.max(10, H - deck.offsetHeight - 10)) + 'px';
      } else {
        setDeckDock(st.dockPos);
      }
    }
    window.addEventListener('resize', onResize);

    function bindCanvasInteraction(canvas) {
      if (!canvas) return;
      canvas.addEventListener('pointerdown', e => {
        if (e.target !== canvas) return;
        pointerStartedOnGlobe = true;
        drag = true;
        tgt = null;
        lx = e.clientX;
        ly = e.clientY;
        movedDistance = 0;
        if (canvas.setPointerCapture) {
          try { canvas.setPointerCapture(e.pointerId); } catch(err) {}
        }
        canvas.classList.add('grabbing');
      });

      canvas.addEventListener('pointerleave', () => {
        if (st.scanMode) {
          $('#scanner-reticle').style.display = 'none';
          $('#scanner-pill').style.display = 'none';
        }
      });

      canvas.addEventListener('wheel', e => {
        zoom = clamp(zoom * (1 + e.deltaY * 0.001), 0.65, 1.8);
        onResize();
      }, { passive: true });
    }

    function initGlobeInteraction() {
      const canvas = $('#gl');
      bindCanvasInteraction(canvas);

      window.addEventListener('pointermove', e => {
        if (st.scanMode) {
          updateScannerHover(e.clientX, e.clientY);
        }

        if (!drag || !ok || !earth) return;
        const dx = e.clientX - lx;
        const dy = e.clientY - ly;
        movedDistance += Math.abs(dx) + Math.abs(dy);
        earth.rotation.y += dx * 0.005;
        earth.rotation.x = clamp(earth.rotation.x + dy * 0.005, -1.3, 1.3);
        lx = e.clientX;
        ly = e.clientY;
      });

      window.addEventListener('pointerup', e => {
        const wasGlobe = pointerStartedOnGlobe;
        pointerStartedOnGlobe = false;
        drag = false;
        const c = $('#gl');
        if (c) c.classList.remove('grabbing');
        if (c && c.releasePointerCapture && c.hasPointerCapture && c.hasPointerCapture(e.pointerId)) {
          try { c.releasePointerCapture(e.pointerId); } catch(err) {}
        }

        const hitUI = e.target.closest && (
          e.target.closest('#ui') ||
          e.target.closest('.hs-marker') ||
          e.target.closest('.modal-box') ||
          e.target.closest('#zen-restore-btn') ||
          e.target.closest('#milestone-alert') ||
          e.target.closest('#region-banner')
        );

        if (wasGlobe && movedDistance < 7 && !hitUI) {
          handleEarthClick(e.clientX, e.clientY);
        }
      });

      window.addEventListener('pointercancel', e => {
        pointerStartedOnGlobe = false;
        drag = false;
        const c = $('#gl');
        if (c) c.classList.remove('grabbing');
      });

      $('#zi').onclick = () => { zoom = clamp(zoom * 0.85, 0.65, 1.8); onResize(); };
      $('#zo').onclick = () => { zoom = clamp(zoom * 1.18, 0.65, 1.8); onResize(); };
    }

    // --- Web Audio API Synthesizer Architecture ---
    const SCALES = {
      pent: [0, 2, 4, 7, 9],
      min: [0, 2, 3, 5, 7, 8, 10],
      dorian: [0, 2, 3, 5, 7, 9, 10],
      phrygian: [0, 1, 3, 5, 7, 8, 10]
    };

    let audio = null;
    let audioAvailable = true;
    let tickTimer = null;
    let biomeTimer = null;

    function degreeToFreq(degree, rootFreq = 110) {
      const s = SCALES[st.scale] || SCALES.pent;
      const octave = Math.floor(degree / s.length);
      const semitone = s[((degree % s.length) + s.length) % s.length];
      return rootFreq * Math.pow(2, (octave * 12 + semitone) / 12);
    }

    function initAudioEngine() {
      if (audio) return;
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) {
          audioAvailable = false;
          $('#live-tag').innerHTML = '<span style="color:#FF5252">NO AUDIO API</span>';
          return;
        }

        const ctx = new AudioCtx();
        
        const masterGain = ctx.createGain();
        masterGain.gain.value = st.mute ? 0 : +$('#vol').value;

        const compressor = ctx.createDynamicsCompressor();
        compressor.threshold.value = -12;
        compressor.knee.value = 8;
        compressor.ratio.value = 4;

        const analyser = ctx.createAnalyser();
        analyser.fftSize = 512;
        analyser.smoothingTimeConstant = 0.82;

        masterGain.connect(compressor);
        compressor.connect(analyser);
        analyser.connect(ctx.destination);

        const panner = ctx.createStereoPanner ? ctx.createStereoPanner() : ctx.createGain();
        panner.connect(masterGain);

        const primaryFilter = ctx.createBiquadFilter();
        primaryFilter.type = 'lowpass';
        primaryFilter.frequency.value = 1400;
        primaryFilter.Q.value = 2.0;

        const filterGain = ctx.createGain();
        filterGain.gain.value = 0;
        primaryFilter.connect(filterGain);
        filterGain.connect(panner);

        const oscNodes = [0, 1, 2, 3].map(i => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = i === 1 ? 'triangle' : (i === 3 ? 'sawtooth' : 'sine');
          gain.gain.value = 0.12;
          osc.connect(gain);
          gain.connect(primaryFilter);
          osc.start();
          return { osc, gain };
        });

        const subOsc = ctx.createOscillator();
        const subGain = ctx.createGain();
        subOsc.type = 'sine';
        subOsc.frequency.value = 55;
        subGain.gain.value = 0.18;
        subOsc.connect(subGain);
        subGain.connect(primaryFilter);
        subOsc.start();

        const noiseBuffer = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
        const noiseData = noiseBuffer.getChannelData(0);
        for (let i = 0; i < noiseData.length; i++) noiseData[i] = Math.random() * 2 - 1;

        const noiseSource = ctx.createBufferSource();
        noiseSource.buffer = noiseBuffer;
        noiseSource.loop = true;

        const noiseFilter = ctx.createBiquadFilter();
        noiseFilter.type = 'bandpass';
        noiseFilter.frequency.value = 1600;
        noiseFilter.Q.value = 3.5;

        const noiseGain = ctx.createGain();
        noiseGain.gain.value = 0;

        noiseSource.connect(noiseFilter);
        noiseFilter.connect(noiseGain);
        noiseGain.connect(panner);
        noiseSource.start();

        const delayBus = ctx.createGain();
        const delay = ctx.createDelay(1.0);
        const delayFeedback = ctx.createGain();
        const delayDamp = ctx.createBiquadFilter();

        delay.delayTime.value = 0.36;
        delayFeedback.gain.value = 0.38;
        delayDamp.type = 'lowpass';
        delayDamp.frequency.value = 2200;

        delayBus.connect(panner);
        delayBus.connect(delay);
        delay.connect(delayDamp);
        delayDamp.connect(delayFeedback);
        delayFeedback.connect(delay);
        delay.connect(panner);

        audio = {
          ctx,
          masterGain,
          panner,
          primaryFilter,
          filterGain,
          oscNodes,
          subOsc,
          subGain,
          noiseFilter,
          noiseGain,
          delayBus,
          analyser
        };
        audioAvailable = true;

      } catch (err) {
        console.warn('Audio initialization encountered an error:', err);
        audioAvailable = false;
      }
    }

    function updateAudioParams() {
      if (!audio) return;
      const c = st.cat;
      const normVal = getNorm(c, st.year);
      const now = audio.ctx.currentTime;
      const baseNote = Math.floor(normVal * 8);

      let cutoff = 1200;
      let detune = 0;
      let noiseLevel = 0.02;
      let subVol = 0.16;

      if (c === 'climate') {
        cutoff = 800 + normVal * 2800;
        detune = normVal * 20;
      } else if (c === 'oceans') {
        cutoff = 500 + normVal * 2200;
        subVol = 0.22 + normVal * 0.1;
      } else if (c === 'forests') {
        noiseLevel = (1 - normVal) * 0.15;
        cutoff = 1000 + normVal * 1500;
      } else if (c === 'atmosphere') {
        detune = normVal * 45;
        cutoff = 1200 + normVal * 2400;
      } else if (c === 'cryosphere') {
        cutoff = 1800 + (1 - normVal) * 1600;
        noiseLevel = (1 - normVal) * 0.12;
      } else if (c === 'methane') {
        subVol = 0.2 + normVal * 0.15;
        detune = normVal * 35;
      }

      [0, 2, 4, 7].forEach((step, i) => {
        const freq = degreeToFreq(baseNote + step);
        audio.oscNodes[i].osc.frequency.setTargetAtTime(freq, now, 0.15);
        audio.oscNodes[i].osc.detune.setTargetAtTime(i % 2 ? detune : 0, now, 0.2);
      });

      audio.subOsc.frequency.setTargetAtTime(c === 'cryosphere' ? 44 : 55, now, 0.2);
      audio.subGain.gain.setTargetAtTime(st.play ? subVol : 0, now, 0.2);

      audio.primaryFilter.frequency.setTargetAtTime(cutoff, now, 0.2);
      audio.noiseGain.gain.setTargetAtTime(st.play ? noiseLevel : 0, now, 0.3);

      if (audio.panner && audio.panner.pan) {
        const targetPan = st.region ? clamp(st.region.lon / 180, -1, 1) : 0;
        audio.panner.pan.setTargetAtTime(targetPan, now, 0.25);
      }

      $('#stat-res').textContent = Math.round(cutoff) + ' HZ';
      $('#osc-hz').textContent = Math.round(degreeToFreq(baseNote)) + ' HZ';
      if (st.region) {
        const panDir = st.region.lon < 0 ? `L ${Math.abs(Math.round(st.region.lon / 1.8))}%` : `R ${Math.round(st.region.lon / 1.8)}%`;
        $('#stat-pan').textContent = panDir;
      } else {
        $('#stat-pan').textContent = 'CENTER';
      }
    }

    function calculateTempo() {
      const v = getNorm(st.cat, st.year);
      const c = st.cat;
      if (c === 'climate') return Math.round(65 + v * 60);
      if (c === 'oceans') return 56;
      if (c === 'forests') return Math.round(58 + (1 - v) * 24);
      if (c === 'atmosphere') return Math.round(68 + v * 52);
      if (c === 'cryosphere') return Math.round(52 + (1 - v) * 38);
      return Math.round(60 + v * 45);
    }

    function audioTick() {
      if (!st.play || !audio) return;
      const ctx = audio.ctx;
      const v = getNorm(st.cat, st.year);
      const baseNote = Math.floor(v * 8) + [0, 2, 4, 5, 7, 9][Math.floor(Math.random() * 6)] + 7;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const now = ctx.currentTime;

      osc.type = 'triangle';
      osc.frequency.value = degreeToFreq(baseNote);

      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.14, now + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2);

      osc.connect(gain);
      gain.connect(audio.delayBus);

      osc.onended = () => {
        try {
          osc.disconnect();
          gain.disconnect();
        } catch(e) {}
      };

      osc.start(now);
      osc.stop(now + 1.3);

      const bpm = calculateTempo();
      $('#stat-bpm').textContent = bpm + ' BPM';
      const delayMs = (60000 / bpm) / (st.cat === 'oceans' || st.cat === 'forests' ? 1 : 2);

      if (tickTimer) clearTimeout(tickTimer);
      if (st.play) {
        tickTimer = setTimeout(audioTick, delayMs);
      }
    }

    function triggerBiomeSound() {
      if (!st.play || !audio || !st.region) return;
      const ctx = audio.ctx;
      const now = ctx.currentTime;
      const sType = st.region.soundType || 'rainforest';

      if (sType === 'rainforest') {
        const osc = ctx.createOscillator();
        const mod = ctx.createOscillator();
        const modGain = ctx.createGain();
        const gain = ctx.createGain();

        osc.type = 'sine';
        mod.type = 'sine';
        mod.frequency.value = 18 + Math.random() * 12;
        modGain.gain.value = 240;

        const baseChirp = 2800 + Math.random() * 1400;
        osc.frequency.setValueAtTime(baseChirp, now);
        osc.frequency.exponentialRampToValueAtTime(baseChirp * 1.3, now + 0.12);

        mod.connect(modGain);
        modGain.connect(osc.frequency);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.06, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.25);

        osc.connect(gain);
        gain.connect(audio.panner);

        osc.onended = () => {
          try {
            osc.disconnect();
            mod.disconnect();
            modGain.disconnect();
            gain.disconnect();
          } catch(e) {}
        };

        mod.start(now); osc.start(now);
        mod.stop(now + 0.3); osc.stop(now + 0.3);

      } else if (sType === 'ocean_abyss') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1150, now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.12, now + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.8);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 0.9);

      } else if (sType === 'polar') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        const chimeFreq = 2200 + [0, 4, 7, 11, 14][Math.floor(Math.random() * 5)] * 110;
        osc.frequency.setValueAtTime(chimeFreq, now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.08, now + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.4);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 1.5);

      } else if (sType === 'coral') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(600 + Math.random() * 800, now);
        osc.frequency.exponentialRampToValueAtTime(1600 + Math.random() * 400, now + 0.05);

        gain.gain.setValueAtTime(0.05, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);

        osc.connect(gain);
        gain.connect(audio.panner);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 0.07);

      } else if (sType === 'desert') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        const notes = [164.8, 174.6, 220.0, 246.9];
        osc.frequency.setValueAtTime(notes[Math.floor(Math.random() * notes.length)], now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.07, now + 0.2);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.8);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 1.9);

      } else if (sType === 'alpine') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(432 * 1.5, now);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.08, now + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 2.2);

        osc.connect(gain);
        gain.connect(audio.delayBus);

        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };

        osc.start(now);
        osc.stop(now + 2.3);
      }

      const nextInterval = 900 + Math.random() * 1800;
      if (biomeTimer) clearTimeout(biomeTimer);
      if (st.play && st.region) {
        biomeTimer = setTimeout(triggerBiomeSound, nextInterval);
      }
    }

    function setPlayState(playing) {
      if (playing) {
        initAudioEngine();
        if (audio && audio.ctx.state === 'suspended') {
          audio.ctx.resume().catch(e => console.warn(e));
        }
      }
      st.play = playing;
      const playBtn = $('#play');
      const miniPlayBtn = $('#mini-play');
      const playText = $('#play-text');

      if (playing) {
        playBtn.classList.add('active');
        miniPlayBtn.classList.add('active');
        playBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
        miniPlayBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
        playText.textContent = 'PAUSE';
        if (audio) {
          audio.filterGain.gain.setTargetAtTime(1.0, audio.ctx.currentTime, 0.35);
          updateAudioParams();
          if (tickTimer) clearTimeout(tickTimer);
          audioTick();
          if (st.region) {
            if (biomeTimer) clearTimeout(biomeTimer);
            triggerBiomeSound();
          }
        }
      } else {
        playBtn.classList.remove('active');
        miniPlayBtn.classList.remove('active');
        playBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
        miniPlayBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
        playText.textContent = 'SONIFY';
        if (audio) {
          audio.filterGain.gain.setTargetAtTime(0.0, audio.ctx.currentTime, 0.35);
          updateAudioParams();
        }
        if (tickTimer) { clearTimeout(tickTimer); tickTimer = null; }
        if (biomeTimer) { clearTimeout(biomeTimer); biomeTimer = null; }
      }
    }
    $('#play').onclick = () => setPlayState(!st.play);
    $('#mini-play').onclick = () => setPlayState(!st.play);

    // --- Dynamic UI Theming & Category Selection ---
    function setCategory(catKey) {
      st.cat = catKey;
      const cat = CATS[catKey];

      $$('.cat-item').forEach(b => {
        b.classList.toggle('on', b.dataset.c === catKey);
      });

      document.documentElement.style.setProperty('--ac', cat.hex);
      document.documentElement.style.setProperty('--ac-glow', cat.glow);
      document.documentElement.style.setProperty('--ac-subtle', cat.subtle);

      $('#hud-name').textContent = cat.t;
      $('#hud-desc').textContent = cat.sub;
      $('#hud-baseline').textContent = cat.baseline;
      $('#hud-rate').textContent = cat.rate;
      $('#sensor-name').textContent = 'REFERENCE · ' + cat.sensor;

      if (U && U.uTint) U.uTint.value.set(...cat.tint);
      if (auraU) {
        auraU.uAura1.value.set(...cat.aura1);
        auraU.uAura2.value.set(...cat.aura2);
      }
      if (ring && ring.material) ring.material.color.set(cat.hex);
      if (starPoints && starPoints.material) starPoints.material.color.set(cat.hex);

      renderChartPath(catKey);
      updateAudioParams();
      updateMilestoneAlert(st.year);
    }

    function renderChartPath(catKey) {
      const cat = CATS[catKey];
      const pts = [];
      const areaPts = ['0,70'];

      for (let i = 0; i <= 45; i++) {
        const x = (i / 45 * 240).toFixed(1);
        const norm = (cat.raw[i] - cat.min) / (cat.max - cat.min);
        const y = (64 - norm * 56).toFixed(1);
        pts.push(`${x},${y}`);
        areaPts.push(`${x},${y}`);
      }
      areaPts.push('240,70');

      $('#ln').setAttribute('points', pts.join(' '));
      $('#ch-area').setAttribute('points', areaPts.join(' '));
    }

    function initCategoryNav() {
      const leftNav = $('#left');
      for (const k in CATS) {
        const c = CATS[k];
        const btn = document.createElement('button');
        btn.className = 'cat-item';
        btn.dataset.c = k;
        btn.style.setProperty('--cat-color', c.hex);
        btn.style.setProperty('--cat-subtle', c.subtle);
        btn.innerHTML = `
          <div class="cat-icon-wrap"><svg viewBox="0 0 24 24">${c.icon}</svg></div>
          <div class="cat-meta">
            <span class="cat-name">${c.n}</span>
            <span class="cat-sub">${c.u} &middot; ${c.rate}</span>
          </div>
        `;
        btn.onclick = () => setCategory(k);
        leftNav.appendChild(btn);
      }
    }

    // --- Interactive Adjustable Timeline Logic ---
    function setYear(yr, notify = true) {
      st.year = clamp(yr, 1980, 2025);
      const roundedYear = Math.round(st.year);
      $('#yr').value = roundedYear;
      $('#yt').textContent = roundedYear + (roundedYear >= 2024 ? ' · NOW' : '');
      $('#mini-year').textContent = roundedYear;
      $('#year-tag').textContent = 'EPOCH ' + roundedYear;

      $$('.ms-chip').forEach(chip => {
        chip.classList.toggle('active', +chip.dataset.yr === roundedYear);
      });

      if (notify) updateMilestoneAlert(roundedYear);
      updateAudioParams();
    }

    function updateMilestoneAlert(year) {
      const ms = MILESTONES.find(m => Math.abs(m.year - Math.round(year)) <= 0.5);
      const alertBox = $('#milestone-alert');
      if (ms) {
        $('#ms-tag').textContent = ms.tag;
        $('#ms-title').textContent = `${ms.year} · ${ms.title}`;
        $('#ms-desc').textContent = ms.desc;
        alertBox.classList.add('on');
      } else {
        alertBox.classList.remove('on');
      }
    }
    $('#btn-close-ms').onclick = () => $('#milestone-alert').classList.remove('on');

    function initMilestonesBar() {
      const bar = $('#ms-bar');
      bar.innerHTML = '';
      MILESTONES.forEach(m => {
        const chip = document.createElement('button');
        chip.className = 'ms-chip mono';
        chip.dataset.yr = m.year;
        chip.textContent = m.year;
        chip.title = m.title;
        chip.onclick = () => setYear(m.year);
        bar.appendChild(chip);
      });
    }

    $('#yr').oninput = e => setYear(+e.target.value);
    $('#btn-step-prev').onclick = () => setYear(st.year - 1);
    $('#btn-step-next').onclick = () => setYear(st.year + 1);
    $('#btn-mini-prev').onclick = () => setYear(st.year - 1);
    $('#btn-mini-next').onclick = () => setYear(st.year + 1);
    $('#btn-step-prev5').onclick = () => setYear(st.year - 5);
    $('#btn-step-next5').onclick = () => setYear(st.year + 5);
    $('#rs').onclick = () => setYear(1980);

    const chartSvg = $('#ch');
    const chartTooltip = $('#ch-tooltip');
    chartSvg.addEventListener('pointermove', e => {
      const rect = chartSvg.getBoundingClientRect();
      const xPct = clamp((e.clientX - rect.left) / rect.width, 0, 1);
      const hoveredYear = Math.round(1980 + xPct * 45);
      const val = getVal(st.cat, hoveredYear);
      chartTooltip.textContent = `${hoveredYear}: ${val.toFixed(CATS[st.cat].d)} ${CATS[st.cat].u}`;
      chartTooltip.style.left = `${xPct * 100}%`;
      chartTooltip.style.opacity = '1';
    });
    chartSvg.addEventListener('pointerleave', () => chartTooltip.style.opacity = '0');
    chartSvg.addEventListener('click', e => {
      const rect = chartSvg.getBoundingClientRect();
      const xPct = clamp((e.clientX - rect.left) / rect.width, 0, 1);
      setYear(Math.round(1980 + xPct * 45));
    });

    // --- Hotspot & Regional Sonification Selection ---
    function selectRegion(h) {
      st.region = h;
      HOTSPOTS.forEach(x => {
        if (x.el) x.el.classList.toggle('on', x === h);
      });

      let customEl = $('#custom-pin');
      if (h.isCustom) {
        if (!customEl) {
          customEl = document.createElement('div');
          customEl.id = 'custom-pin';
          customEl.className = 'hs-marker custom-beacon on';
          $('#hsb').appendChild(customEl);
        }
        h.el = customEl;
        customEl.innerHTML = `
          <div class="hs-tooltip" style="opacity:1">
            <b>${h.icon} ${h.n}</b>
            <small>${h.location}</small>
          </div>
        `;
      } else if (customEl) {
        customEl.remove();
      }

      h.v = latLonToVec3(h.lat, h.lon);

      if (h.cat && CATS[h.cat]) {
        setCategory(h.cat);
      }

      tgt = {
        y: -(h.lon + 90) * (Math.PI / 180),
        x: clamp(h.lat * (Math.PI / 180), -1.2, 1.2)
      };

      $('#reg-icon').textContent = h.icon;
      $('#reg-name').textContent = h.n.toUpperCase();
      $('#reg-badge').textContent = h.badge;
      $('#reg-coords').textContent = h.location;
      $('#reg-sound-desc').textContent = h.soundDesc;
      if (typeof AriaApi !== 'undefined' && AriaApi.isLive && h.lat != null && h.lon != null) {
        AriaApi.fetchRegionalWeather(h.lat, h.lon, 2022, 2023).then(data => {
          if (data && data.data && data.data.length > 0) {
            const latest = data.data[data.data.length - 1];
            $('#reg-sound-desc').textContent = `${h.soundDesc} [NASA POWER In-Situ 2m Temp: ${latest.value.toFixed(1)}°C]`;
          }
        }).catch(() => {});
      }
      $('#region-banner').classList.add('on');
      $('#tag-label').textContent = h.n.toUpperCase();
      $('#mini-region-tag').textContent = h.n.slice(0, 10).toUpperCase();

      updateAudioParams();
      if (st.play) {
        if (biomeTimer) clearTimeout(biomeTimer);
        triggerBiomeSound();
      }

      $('#region-drawer').classList.remove('open');
    }

    function resetToGlobal() {
      st.region = null;
      HOTSPOTS.forEach(x => { if (x.el) x.el.classList.remove('on'); });
      const customEl = $('#custom-pin');
      if (customEl) customEl.remove();
      $('#region-banner').classList.remove('on');
      $('#tag-label').textContent = 'GLOBAL SYNTH';
      $('#mini-region-tag').textContent = 'GLOBAL';
      if (biomeTimer) { clearTimeout(biomeTimer); biomeTimer = null; }
      updateAudioParams();
    }
    $('#btn-reset-region').onclick = resetToGlobal;

    function initRegionDrawer(filter = 'all') {
      const grid = $('#regions-grid');
      grid.innerHTML = '';
      HOTSPOTS.forEach(h => {
        if (filter !== 'all') {
          if (filter === 'atmosphere') {
            if (h.cat !== 'atmosphere' && h.cat !== 'methane') return;
          } else if (h.cat !== filter) {
            return;
          }
        }

        const cat = CATS[h.cat] || CATS.climate;
        const card = document.createElement('div');
        card.className = 'reg-card';
        card.style.setProperty('--card-color', cat.hex);
        card.style.setProperty('--card-subtle', cat.subtle);
        card.innerHTML = `
          <div class="rc-top">
            <span class="rc-icon">${h.icon}</span>
            <span class="rc-badge">${h.badge}</span>
          </div>
          <div class="rc-name">${h.n}</div>
          <div class="rc-loc">${h.location}</div>
          <div class="rc-sound">${h.soundDesc}</div>
          <button class="rc-btn">LISTEN TO REGION</button>
        `;
        card.onclick = () => selectRegion(h);
        grid.appendChild(card);
      });
    }

    $$('.biome-filter-btn').forEach(btn => {
      btn.onclick = () => {
        $$('.biome-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        initRegionDrawer(btn.dataset.filter);
      };
    });

    $('#btn-regions').onclick = () => {
      initRegionDrawer('all');
      $('#region-drawer').classList.add('open');
    };
    $('#btn-close-regions').onclick = () => $('#region-drawer').classList.remove('open');

    $('#btn-scanner').onclick = () => {
      st.scanMode = !st.scanMode;
      $('#btn-scanner').classList.toggle('active', st.scanMode);
      $('#scanner-btn-label').textContent = st.scanMode ? 'SCANNING ON' : 'SCAN EARTH';
      if (st.scanMode) {
        setPlayState(true);
      } else {
        $('#scanner-reticle').style.display = 'none';
        $('#scanner-pill').style.display = 'none';
      }
    };

    // --- Control Deck Dragging & Docking System ---
    const deck = $('#jb');
    const dragHandle = $('#deck-drag');
    let isDraggingDeck = false;
    let deckStartX, deckStartY, deckInitialLeft, deckInitialTop;

    dragHandle.addEventListener('pointerdown', e => {
      if (e.target.closest('button')) return;
      isDraggingDeck = true;
      if (dragHandle.setPointerCapture) {
        try { dragHandle.setPointerCapture(e.pointerId); } catch(err) {}
      }
      const rect = deck.getBoundingClientRect();
      deckStartX = e.clientX;
      deckStartY = e.clientY;
      deckInitialLeft = rect.left;
      deckInitialTop = rect.top;

      deck.style.transform = 'none';
      deck.style.left = deckInitialLeft + 'px';
      deck.style.top = deckInitialTop + 'px';
      deck.style.bottom = 'auto';
      st.dockPos = 'free';
      $('#sel-dock-pos').value = 'free';
    });

    window.addEventListener('pointermove', e => {
      if (!isDraggingDeck) return;
      const dx = e.clientX - deckStartX;
      const dy = e.clientY - deckStartY;
      const newLeft = clamp(deckInitialLeft + dx, 10, window.innerWidth - deck.offsetWidth - 10);
      const newTop = clamp(deckInitialTop + dy, 10, window.innerHeight - deck.offsetHeight - 10);
      deck.style.left = newLeft + 'px';
      deck.style.top = newTop + 'px';
    });

    window.addEventListener('pointerup', e => {
      if (isDraggingDeck) {
        isDraggingDeck = false;
        if (dragHandle.releasePointerCapture && dragHandle.hasPointerCapture && dragHandle.hasPointerCapture(e.pointerId)) {
          try { dragHandle.releasePointerCapture(e.pointerId); } catch(err) {}
        }
      }
    });

    function setDeckDock(pos) {
      st.dockPos = pos;
      if (pos === 'bottom') {
        deck.style.left = '50%';
        deck.style.top = 'auto';
        deck.style.bottom = 'calc(14px + env(safe-area-inset-bottom, 0px))';
        deck.style.right = 'auto';
        deck.style.transform = 'translateX(-50%)';
      } else if (pos === 'top') {
        deck.style.left = '50%';
        deck.style.top = 'calc(70px + env(safe-area-inset-top, 0px))';
        deck.style.bottom = 'auto';
        deck.style.right = 'auto';
        deck.style.transform = 'translateX(-50%)';
      } else if (pos === 'left') {
        deck.style.left = '22px';
        deck.style.bottom = 'calc(14px + env(safe-area-inset-bottom, 0px))';
        deck.style.top = 'auto';
        deck.style.right = 'auto';
        deck.style.transform = 'none';
      } else if (pos === 'right') {
        deck.style.left = 'auto';
        deck.style.right = '22px';
        deck.style.bottom = 'calc(14px + env(safe-area-inset-bottom, 0px))';
        deck.style.top = 'auto';
        deck.style.transform = 'none';
      }
    }

    const DOCK_CYCLE = ['bottom', 'top', 'left', 'right'];
    $('#btn-dock-cycle').onclick = () => {
      let nextIdx = (DOCK_CYCLE.indexOf(st.dockPos) + 1) % DOCK_CYCLE.length;
      setDeckDock(DOCK_CYCLE[nextIdx]);
      $('#sel-dock-pos').value = DOCK_CYCLE[nextIdx];
    };
    $('#sel-dock-pos').onchange = e => setDeckDock(e.target.value);

    function toggleDeckMinimize() {
      deck.classList.toggle('minimized');
      const isMin = deck.classList.contains('minimized');
      $('#btn-minimize-deck').innerHTML = isMin ? 
        '<svg viewBox="0 0 24 24"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>' :
        '<svg viewBox="0 0 24 24"><path d="M5 12h14"/></svg>';
      $('#btn-minimize-deck').title = isMin ? 'Expand Control Deck' : 'Minimize Control Deck';
    }
    $('#btn-minimize-deck').onclick = toggleDeckMinimize;
    $('#btn-expand-deck').onclick = toggleDeckMinimize;

    function toggleZenMode() {
      document.body.classList.toggle('zen-mode');
      const isZen = document.body.classList.contains('zen-mode');
      $('#btn-zen').classList.toggle('active', isZen);
    }
    $('#btn-zen').onclick = toggleZenMode;
    $('#zen-restore-btn').onclick = toggleZenMode;
    window.addEventListener('keydown', e => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA')) {
        return;
      }
      if (e.key === 'z' || e.key === 'Z') {
        toggleZenMode();
      } else if (e.code === 'Space') {
        e.preventDefault();
        setPlayState(!st.play);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        setYear(Math.min(2025, st.year + 1));
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        setYear(Math.max(1980, st.year - 1));
      } else if (e.key === 'Escape') {
        $('#settings-modal').classList.remove('open');
        $('#region-drawer').classList.remove('open');
        if (document.body.classList.contains('zen-mode')) toggleZenMode();
      }
    });

    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      st.rotSpeed = 'off';
      const selRot = $('#sel-rot');
      if (selRot) selRot.value = 'off';
    }

    const btnCloseFb = $('#btn-close-fb');
    if (btnCloseFb) {
      btnCloseFb.onclick = () => {
        const fb = $('#fb');
        if (fb) fb.style.display = 'none';
      };
    }

    $('#btn-settings').onclick = () => $('#settings-modal').classList.add('open');
    $('#btn-close-settings').onclick = () => $('#settings-modal').classList.remove('open');
    const bBadge = $('#backend-badge');
    if (bBadge) bBadge.onclick = () => $('#settings-modal').classList.add('open');
    const syncBtn = $('#btn-sync-backend');
    if (syncBtn) {
      syncBtn.onclick = () => {
        const inp = $('#inp-backend-url');
        if (inp && inp.value) AriaApi.setBaseUrl(inp.value);
        AriaApi.syncWithBackend();
      };
    }

    $('#sel-scale').onchange = e => {
      st.scale = e.target.value;
      const names = { pent: 'PENTATONIC', min: 'NATURAL MINOR', dorian: 'DORIAN MODE', phrygian: 'PHRYGIAN' };
      $('#scale-badge').textContent = names[st.scale] || 'PENTATONIC';
      updateAudioParams();
    };
    $('#sel-rot').onchange = e => st.rotSpeed = e.target.value;
    $('#sel-aura').onchange = e => {
      st.auraIntensity = +e.target.value;
      if (auraU) auraU.uIntensity.value = st.auraIntensity;
    };

    $('#btn-fs').onclick = () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    };

    $('#vol').oninput = e => {
      if (audio && !st.mute) audio.masterGain.gain.value = +e.target.value;
    };
    $('#snd').onclick = e => {
      st.mute = !st.mute;
      e.currentTarget.classList.toggle('on', st.mute);
      if (audio) audio.masterGain.gain.value = st.mute ? 0 : +$('#vol').value;
    };

    $('#go').onclick = () => {
      $('#intro').classList.add('off');
      $('#ui').classList.add('on');
      setPlayState(true);
    };

    // --- Main Animation & Render Loop ---
    const waveCtx = $('#wv').getContext('2d');
    const specCtx = $('#sp').getContext('2d');
    const timeData = new Uint8Array(256);
    const freqData = new Uint8Array(128);
    let lastTime = performance.now();

    function renderLoop(now) {
      requestAnimationFrame(renderLoop);
      const dt = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;

      const c = CATS[st.cat];
      const curVal = getVal(st.cat, st.year);
      const normVal = getNorm(st.cat, st.year);
      const base1980Val = c.raw[0];
      const delta1980 = curVal - base1980Val;

      const signPrefix = (st.cat === 'climate' || st.cat === 'oceans') && curVal >= 0 ? '+' : '';
      $('#val').innerHTML = `${signPrefix}${curVal.toFixed(c.d)}<small>${c.u}</small>`;

      const trendEl = $('#trend');
      const deltaSign = delta1980 >= 0 ? '▲ +' : '▼ ';
      trendEl.textContent = `${deltaSign}${Math.abs(delta1980).toFixed(c.d)} ${c.u} SINCE 1980`;
      trendEl.className = `delta-badge mono ${delta1980 >= 0 ? 'up' : 'down'}`;

      const xPos = ((st.year - 1980) / 45 * 240).toFixed(1);
      const yPos = (64 - normVal * 56).toFixed(1);
      $('#dt').setAttribute('cx', xPos);
      $('#dt').setAttribute('cy', yPos);
      $('#cursor-ln').setAttribute('x1', xPos);
      $('#cursor-ln').setAttribute('x2', xPos);

      // Render Audio Visualizers
      waveCtx.clearRect(0, 0, 260, 26);
      specCtx.clearRect(0, 0, 260, 26);

      if (audio && st.play && audio.analyser) {
        audio.analyser.getByteTimeDomainData(timeData);
        audio.analyser.getByteFrequencyData(freqData);

        waveCtx.strokeStyle = c.hex;
        waveCtx.lineWidth = 1.5;
        waveCtx.shadowColor = c.hex;
        waveCtx.shadowBlur = 4;
        waveCtx.beginPath();
        for (let i = 0; i < 256; i++) {
          const x = (i / 255) * 260;
          const y = (timeData[i] / 255) * 26;
          if (i === 0) waveCtx.moveTo(x, y);
          else waveCtx.lineTo(x, y);
        }
        waveCtx.stroke();
        waveCtx.shadowBlur = 0;

        const barCount = 30;
        const barWidth = 260 / barCount - 2;
        for (let i = 0; i < barCount; i++) {
          const h = (freqData[i * 2] / 255) * 24;
          const x = i * (barWidth + 2);
          const y = 26 - h;
          const grad = specCtx.createLinearGradient(0, y, 0, 26);
          grad.addColorStop(0, '#FFFFFF');
          grad.addColorStop(0.3, c.hex);
          grad.addColorStop(1, 'rgba(255,255,255,0.05)');
          specCtx.fillStyle = grad;
          specCtx.fillRect(x, y, barWidth, h);
        }
      } else {
        waveCtx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        waveCtx.beginPath();
        waveCtx.moveTo(0, 13);
        waveCtx.lineTo(260, 13);
        waveCtx.stroke();
      }

      // 3D WebGL or 2D Interactive Fallback Rendering
      if (!ok) {
        render2DFallbackMap(now, dt, normVal, c);
        return;
      }

      if (!earth || !cam || !R || !scene) return;

      if (U && U.uTime) {
        U.uTime.value = now / 1000;
        U.uV.value += (normVal - U.uV.value) * Math.min(1, dt * 3.5);
      }

      if (tgt) {
        let dy = tgt.y - earth.rotation.y;
        dy = Math.atan2(Math.sin(dy), Math.cos(dy));
        earth.rotation.y += dy * Math.min(1, dt * 4);
        earth.rotation.x += (tgt.x - earth.rotation.x) * Math.min(1, dt * 4);
      } else if (!drag) {
        const rotMultiplier = st.rotSpeed === 'fast' ? 0.12 : (st.rotSpeed === 'slow' ? 0.02 : 0.05);
        if (st.rotSpeed !== 'off') {
          earth.rotation.y += dt * rotMultiplier;
        }
      }

      cam.position.z += (zT - cam.position.z) * Math.min(1, dt * 5);

      const allMarkers = [...HOTSPOTS];
      if (st.region && st.region.isCustom && st.region.el) {
        allMarkers.push(st.region);
      }

      allMarkers.forEach(h => {
        if (!h.el || !h.v) return;
        const normalVec = h.v.clone().applyEuler(earth.rotation);
        const worldPos = normalVec.clone().multiplyScalar(1.02).add(planet.position);
        const isVisible = normalVec.dot(cam.position.clone().sub(worldPos)) > 0;

        worldPos.project(cam);
        const sx = (worldPos.x * 0.5 + 0.5) * window.innerWidth;
        const sy = (-worldPos.y * 0.5 + 0.5) * window.innerHeight;

        h.el.style.transform = `translate(${sx}px, ${sy}px)`;
        h.el.style.opacity = isVisible && $('#ui').classList.contains('on') && !document.body.classList.contains('zen-mode') ? '1' : '0';
        h.el.style.pointerEvents = isVisible ? 'auto' : 'none';
      });

      R.render(scene, cam);
    }

    // --- Central ARIA Frontend API Client ---
    const isLocalDev = Boolean(
      typeof window !== 'undefined' && (
        window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.protocol === 'file:' ||
        window.location.hostname === ''
      )
    );

    const AriaApi = {
      baseUrl: (typeof localStorage !== 'undefined' && localStorage.getItem('aria_backend_url')) || (isLocalDev ? 'http://127.0.0.1:8000' : ''),
      isLive: false,
      lastSync: null,

      async init() {
        const inp = $('#inp-backend-url');
        if (inp) inp.value = this.baseUrl;

        if (!this.baseUrl) {
          this.setStandaloneMode();
          return true;
        }
        return await this.syncWithBackend();
      },

      setStandaloneMode() {
        this.isLive = false;
        const badge = $('#backend-badge');
        const statusText = $('#backend-status-text');
        const warnEl = $('#backend-mixed-warn');
        if (warnEl) warnEl.style.display = 'none';
        if (badge) {
          badge.textContent = '● NASA/NOAA REFERENCE ENGINE';
          badge.style.color = '#80D8FF';
          badge.style.borderColor = 'rgba(128, 216, 255, 0.4)';
        }
        if (statusText) {
          statusText.textContent = 'STATUS: STANDALONE EMPIRICAL RECORD (1980–2025 NASA & NOAA REFERENCE ENGINE)';
          statusText.style.color = '#80D8FF';
        }
      },

      setBaseUrl(url) {
        if (!url || !url.trim()) {
          this.baseUrl = '';
          try {
            if (typeof localStorage !== 'undefined') localStorage.removeItem('aria_backend_url');
          } catch(e) {}
          this.setStandaloneMode();
          return;
        }

        const trimmed = url.trim().replace(/\/+$/, '');
        this.baseUrl = trimmed;
        try {
          if (typeof localStorage !== 'undefined') localStorage.setItem('aria_backend_url', this.baseUrl);
        } catch(e) {}
      },

      async checkHealth() {
        if (!this.baseUrl) return false;
        try {
          const controller = new AbortController();
          const timer = setTimeout(() => controller.abort(), 2000);
          const res = await fetch(`${this.baseUrl}/api/v1/health`, { method: 'GET', signal: controller.signal });
          clearTimeout(timer);
          if (!res.ok) return false;
          const data = await res.json();
          return data.status === 'healthy';
        } catch (e) {
          return false;
        }
      },

      async syncWithBackend() {
        const badge = $('#backend-badge');
        const statusText = $('#backend-status-text');
        const warnEl = $('#backend-mixed-warn');

        if (!this.baseUrl) {
          this.setStandaloneMode();
          return true;
        }

        // Mixed Content Check
        if (typeof window !== 'undefined' && window.location.protocol === 'https:' && this.baseUrl.startsWith('http://')) {
          if (warnEl) warnEl.style.display = 'block';
          if (statusText) {
            statusText.textContent = 'BLOCKED: Cannot request insecure HTTP from HTTPS page (Mixed Content).';
            statusText.style.color = '#FF5252';
          }
          if (badge) {
            badge.textContent = '● MIXED CONTENT BLOCKED';
            badge.style.color = '#FF5252';
            badge.style.borderColor = '#FF5252';
          }
          return false;
        }
        if (warnEl) warnEl.style.display = 'none';

        if (statusText) statusText.textContent = 'STATUS: CONNECTING TO ' + this.baseUrl + '...';
        if (badge) {
          badge.textContent = '● BACKEND: CONNECTING';
          badge.style.color = '#FFB74D';
          badge.style.borderColor = 'rgba(255, 183, 77, 0.4)';
        }

        const healthy = await this.checkHealth();
        if (!healthy) {
          this.isLive = false;
          if (badge) {
            badge.textContent = '● NASA/NOAA REFERENCE ENGINE';
            badge.style.color = '#80D8FF';
            badge.style.borderColor = 'rgba(128, 216, 255, 0.4)';
          }
          if (statusText) {
            statusText.textContent = `STATUS: UNREACHABLE (${this.baseUrl}) — USING CURATED NASA/NOAA REFERENCE ENGINE`;
            statusText.style.color = '#80D8FF';
          }
          return false;
        }

        this.isLive = true;
        this.lastSync = new Date();
        if (badge) {
          badge.textContent = '● NASA/NOAA LIVE';
          badge.style.color = '#00E676';
          badge.style.borderColor = '#00E676';
        }
        if (statusText) {
          statusText.textContent = 'STATUS: CONNECTED TO FASTAPI (REAL NASA/NOAA TELEMETRY)';
          statusText.style.color = '#00E676';
        }

        try {
          // 1. Fetch real NASA GISTEMP LOTI annual series (1980–2025)
          const gistempRes = await fetch(`${this.baseUrl}/api/v1/climate/temperature/global?start_year=1980&end_year=2025`);
          if (gistempRes.ok) {
            const json = await gistempRes.json();
            const yearAverages = {};
            json.data.forEach(p => {
              if (!yearAverages[p.year]) yearAverages[p.year] = [];
              yearAverages[p.year].push(p.value);
            });
            const newRaw = [];
            for (let y = 1980; y <= 2025; y++) {
              if (yearAverages[y] && yearAverages[y].length > 0) {
                const avg = yearAverages[y].reduce((a, b) => a + b, 0) / yearAverages[y].length;
                newRaw.push(parseFloat(avg.toFixed(2)));
              } else if (newRaw.length > 0) {
                newRaw.push(newRaw[newRaw.length - 1]);
              } else {
                newRaw.push(CATS.climate.raw[y - 1980]);
              }
            }
            if (newRaw.length === 46) {
              CATS.climate.raw = newRaw;
              CATS.climate.min = Math.min(...newRaw);
              CATS.climate.max = Math.max(...newRaw);
              CATS.climate.sub = 'NASA GISS GISTEMP v4 LOTI (Empirical Download)';
              CATS.climate.sensor = 'NASA Goddard Institute for Space Studies';
            }
          }

          // 2. Fetch real NOAA GML Mauna Loa monthly CO2 (1980–2025)
          const co2Res = await fetch(`${this.baseUrl}/api/v1/atmosphere/co2/mauna-loa?start_year=1980&end_year=2025`);
          if (co2Res.ok) {
            const json = await co2Res.json();
            const yearAverages = {};
            json.data.forEach(p => {
              if (!yearAverages[p.year]) yearAverages[p.year] = [];
              yearAverages[p.year].push(p.value);
            });
            const newRaw = [];
            for (let y = 1980; y <= 2025; y++) {
              if (yearAverages[y] && yearAverages[y].length > 0) {
                const avg = yearAverages[y].reduce((a, b) => a + b, 0) / yearAverages[y].length;
                newRaw.push(parseFloat(avg.toFixed(1)));
              } else if (newRaw.length > 0) {
                newRaw.push(newRaw[newRaw.length - 1]);
              } else {
                newRaw.push(CATS.atmosphere.raw[y - 1980]);
              }
            }
            if (newRaw.length === 46) {
              CATS.atmosphere.raw = newRaw;
              CATS.atmosphere.min = Math.min(...newRaw);
              CATS.atmosphere.max = Math.max(...newRaw);
              CATS.atmosphere.sub = 'NOAA GML Mauna Loa In-Situ Baseline Record';
              CATS.atmosphere.sensor = 'NOAA Global Monitoring Laboratory & Scripps';
            }
          }

          renderChartPath(st.cat);
          updateAudioParams();
        } catch (err) {
          console.warn('Real dataset synchronization warning:', err);
        }

        return true;
      },

      async fetchRegionalWeather(lat, lon, startYear = 2022, endYear = 2023) {
        if (!this.isLive) return null;
        try {
          const res = await fetch(`${this.baseUrl}/api/v1/climate/temperature/regional?latitude=${lat.toFixed(2)}&longitude=${lon.toFixed(2)}&start_year=${startYear}&end_year=${endYear}`);
          if (res.ok) return await res.json();
        } catch (e) {
          console.warn('Regional weather fetch error:', e);
        }
        return null;
      }
    };

    // Expose programmatic interface for testing, automation & external monitoring
    window.ARIA = {
      st,
      get ok() { return ok; },
      get zoom() { return zoom; },
      get audio() { return audio; },
      get audioAvailable() { return audioAvailable; },
      get earth() { return earth; },
      get planet() { return planet; },
      api: AriaApi,
      setCategory,
      setYear,
      selectRegion,
      resetToGlobal,
      setPlayState,
      toggleDeckMinimize,
      setDeckDock,
      toggleZenMode,
      handleEarthClick,
      updateScannerHover,
      onResize,
      HOTSPOTS,
      CATS,
      MILESTONES
    };

    // Also bind directly to window for global convenience and test suite backwards compatibility
    window.st = st;
    window.AriaApi = AriaApi;
    window.setCategory = setCategory;
    window.setYear = setYear;
    window.selectRegion = selectRegion;
    window.resetToGlobal = resetToGlobal;
    window.handleEarthClick = handleEarthClick;
    window.updateScannerHover = updateScannerHover;
    window.setDeckDock = setDeckDock;
    window.toggleDeckMinimize = toggleDeckMinimize;
    window.toggleZenMode = toggleZenMode;
    window.onResize = onResize;
    Object.defineProperty(window, 'ok', { get: () => ok });
    Object.defineProperty(window, 'zoom', { get: () => zoom });
    Object.defineProperty(window, 'audio', { get: () => audio });
    Object.defineProperty(window, 'audioAvailable', { get: () => audioAvailable });
    Object.defineProperty(window, 'earth', { get: () => earth });
    Object.defineProperty(window, 'planet', { get: () => planet });

    // --- Initialization Sequence ---
    window.addEventListener('DOMContentLoaded', () => {
      initWebGL();
      onResize();
      initGlobeInteraction();
      initCategoryNav();
      initMilestonesBar();
      initHotspotBeacons();
      initRegionDrawer('all');
      setCategory('climate');
      setYear(1990);
      AriaApi.init();
      
      if (window.innerWidth < 600) {
        toggleDeckMinimize();
      }

      requestAnimationFrame(renderLoop);
    });
