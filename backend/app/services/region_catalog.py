from typing import List, Dict, Any, Optional

HOTSPOTS: List[Dict[str, Any]] = [
    {
        "id": "amazon",
        "name": "Amazon Basin",
        "location": "Brazil · South America",
        "latitude": -3.4,
        "longitude": -62.2,
        "category": "forests",
        "badge": "CANOPY BIOPHONY",
        "sound_type": "rainforest",
        "sound_description": "Synthesized rainforest biophony with avian FM sweeps and moist canopy resonance.",
        "icon": "🌿"
    },
    {
        "id": "patagonia",
        "name": "Patagonian Ice Fields",
        "location": "Chile & Argentina · South America",
        "latitude": -49.5,
        "longitude": -73.5,
        "category": "cryosphere",
        "badge": "SOUTHERN ICE FIELD",
        "sound_type": "polar",
        "sound_description": "Glacial creaking, sub-zero katabatic wind gusts, and southern maritime resonance.",
        "icon": "❄️"
    },
    {
        "id": "pnw",
        "name": "Pacific Northwest Rainforest",
        "location": "USA & Canada · North America",
        "latitude": 47.5,
        "longitude": -122.3,
        "category": "forests",
        "badge": "TEMPERATE RAINFOREST",
        "sound_type": "temperate",
        "sound_description": "Temperate coastal canopy, rainfall flutter, and dense conifer forest resonance.",
        "icon": "🌲"
    },
    {
        "id": "mojave",
        "name": "Mojave Desert & Death Valley",
        "location": "California · North America",
        "latitude": 36.2,
        "longitude": -116.8,
        "category": "climate",
        "badge": "THERMAL BASIN",
        "sound_type": "desert",
        "sound_description": "Extreme heat acoustic shimmer, arid wind friction, and sun-baked earth drone.",
        "icon": "🏜️"
    },
    {
        "id": "gbr",
        "name": "Great Barrier Reef",
        "location": "Coral Sea · Australia",
        "latitude": -18.2,
        "longitude": 147.7,
        "category": "oceans",
        "badge": "REEF HYDROPHONY",
        "sound_type": "ocean",
        "sound_description": "Coral hydrophony, snapping shrimp pulses, and thermal bleaching frequency drift.",
        "icon": "🪸"
    },
    {
        "id": "outback",
        "name": "Australian Outback",
        "location": "Northern Territory · Australia",
        "latitude": -23.7,
        "longitude": 133.8,
        "category": "climate",
        "badge": "ARID INTERIOR",
        "sound_type": "desert",
        "sound_description": "Low red-sand resonance, high cicada drone, and dust devil acoustic textures.",
        "icon": "🦘"
    },
    {
        "id": "greenland",
        "name": "Greenland Ice Sheet (Ilulissat)",
        "location": "West Greenland · Arctic",
        "latitude": 69.2,
        "longitude": -51.1,
        "category": "cryosphere",
        "badge": "CALVING GLACIER",
        "sound_type": "polar",
        "sound_description": "Deep sub-surface glacier calving booms, crystalline ice fracture, and meltwater stream tone.",
        "icon": "🧊"
    },
    {
        "id": "svalbard",
        "name": "Svalbard Arctic Archipelago",
        "location": "Norway · Arctic Ocean",
        "latitude": 78.2,
        "longitude": 15.6,
        "category": "cryosphere",
        "badge": "HIGH ARCTIC",
        "sound_type": "polar",
        "sound_description": "Katabatic wind resonance, sub-zero drone, and Arctic ocean pack ice grind.",
        "icon": "🐻‍❄️"
    },
    {
        "id": "sahara",
        "name": "Sahara Desert",
        "location": "North Africa · Erg Chebbi",
        "latitude": 23.4,
        "longitude": 12.6,
        "category": "climate",
        "badge": "SOLAR MAXIMA",
        "sound_type": "desert",
        "sound_description": "Hyper-arid heat shimmer harmonics, wind-blown silica whistle, and vast silence.",
        "icon": "☀️"
    },
    {
        "id": "congo",
        "name": "Congo Rainforest Basin",
        "location": "Democratic Republic of Congo · Central Africa",
        "latitude": -0.8,
        "longitude": 21.7,
        "category": "forests",
        "badge": "EQUATORIAL PEATLAND",
        "sound_type": "rainforest",
        "sound_description": "Dense equatorial peatland reverberation, nocturnal biophony, and river humidity resonance.",
        "icon": "🌳"
    },
    {
        "id": "mariana",
        "name": "Mariana Trench Abyssal Plain",
        "location": "Western Pacific Ocean",
        "latitude": 11.3,
        "longitude": 142.2,
        "category": "oceans",
        "badge": "HADAL ZONE",
        "sound_type": "ocean",
        "sound_description": "Sub-oceanic tectonic low-frequency rumble, ultra-deep abyssal pressure drone, and whale song reverb.",
        "icon": "🌊"
    },
    {
        "id": "marianas",
        "name": "North Pacific Subtropical Gyre",
        "location": "Central North Pacific",
        "latitude": 32.0,
        "longitude": -145.0,
        "category": "oceans",
        "badge": "OCEAN GYRE",
        "sound_type": "ocean",
        "sound_description": "Open ocean swell harmonics, pelagic wind friction, and calm high-pressure expanse drone.",
        "icon": "🌀"
    },
    {
        "id": "himalayas",
        "name": "Himalayan Glaciers & Tibetan Plateau",
        "location": "Nepal & Tibet · High Asia",
        "latitude": 27.9,
        "longitude": 86.9,
        "category": "cryosphere",
        "badge": "THIRD POLE",
        "sound_type": "mountain",
        "sound_description": "Thin atmospheric wind flute tones, high-altitude prayer-flag flutter, and glacier crevasse hum.",
        "icon": "🏔️"
    },
    {
        "id": "siberia",
        "name": "Siberian Taiga Permafrost",
        "location": "Sakha Republic · Russia",
        "latitude": 62.0,
        "longitude": 129.7,
        "category": "methane",
        "badge": "METHANE SEEP",
        "sound_type": "polar",
        "sound_description": "Sub-surface permafrost thaw bubbling, thermokarst lake methane seeps, and boreal wind drone.",
        "icon": "🔥"
    },
    {
        "id": "borneo",
        "name": "Borneo Peat Swamp Forest",
        "location": "Indonesia & Malaysia · Southeast Asia",
        "latitude": 0.5,
        "longitude": 114.0,
        "category": "forests",
        "badge": "PEAT SWAMP CANOPY",
        "sound_type": "rainforest",
        "sound_description": "Rich tropical peat swamp canopy, gibbon call glissandi, and nocturnal amphibian chirps.",
        "icon": "🦧"
    },
    {
        "id": "antarctica",
        "name": "Antarctic Ross Ice Shelf",
        "location": "Antarctica · Polar Plateau",
        "latitude": -81.5,
        "longitude": -175.0,
        "category": "cryosphere",
        "badge": "POLAR VORTEX",
        "sound_type": "polar",
        "sound_description": "Sub-zero polar vortex acoustic hiss, ice-shelf seismic hum, and vast continental white noise.",
        "icon": "🐧"
    },
    {
        "id": "mlo",
        "name": "Mauna Loa Observatory",
        "location": "Hawaii · Central Pacific",
        "latitude": 19.5,
        "longitude": -155.6,
        "category": "atmosphere",
        "badge": "KEELING BASELINE",
        "sound_type": "mountain",
        "sound_description": "Pure Pacific maritime baseline airstream, volcanic ridge whistle, and continuous analyzer hum.",
        "icon": "📈"
    },
    {
        "id": "atacama",
        "name": "Atacama Desert Plateau",
        "location": "Chile · South America",
        "latitude": -23.8,
        "longitude": -69.2,
        "category": "climate",
        "badge": "HYPER-ARID MARS ANALOG",
        "sound_type": "desert",
        "sound_description": "Hyper-arid high-altitude silence, crystalline salt flat friction, and solar wind resonance.",
        "icon": "🔭"
    }
]

class RegionCatalog:
    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        return HOTSPOTS

    @staticmethod
    def get_by_id(region_id: str) -> Optional[Dict[str, Any]]:
        for r in HOTSPOTS:
            if r["id"] == region_id:
                return r
        return None
