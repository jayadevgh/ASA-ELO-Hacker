from __future__ import annotations

from asa_elo_project.types import Competition

D = 400.0
K_NEW = 20.0
K_EST = 16.0

COMPS = [
    Competition(
        "steel_city_sapna",
        0,
        [
            "Dhamakapella",
            "Penn State Fanaa",
            "TAMU Swaram",
            "Cornell Tarana",
            "RP Iraaga",
            "STL Acapella",
            "Drexel Dhvani",
            "Mystery S",
        ],
        [1.00, 0.82, 0.60, 0.53, 0.43, 0.30, 0.14, -0.06],
        {"Dhamakapella": 1, "Penn State Fanaa": 2, "TAMU Swaram": 3},
    ),
    Competition(
        "buckeye_laya",
        1,
        [
            "CMU Saans",
            "USC Slibaat",
            "Penn State Fanaa",
            "Sargam",
            "Raaga at UCR",
            "UTD Dhunki",
            "Hum A Cappella",
            "UGA Kalakaar",
        ],
        [0.10, 0.00, 0.20, 0.50, -0.05, 1.00, 0.82, 0.65],
        {"UTD Dhunki": 1, "Hum A Cappella": 2, "UGA Kalakaar": 3, "Sargam": 4},
    ),
    Competition(
        "gathe_raho",
        2,
        [
            "VT Swara",
            "UCD Jhankaar",
            "MN Fitoor",
            "Illini Awaaz",
            "Duke Deewana",
            "UC Junoon",
            "Astha Acappella",
            "Purdue Taal",
        ],
        [-0.10, 1.00, 0.58, 0.57, -0.31, -0.45, -0.53, 0.21],
        {"UCD Jhankaar": 1, "MN Fitoor": 2, "Illini Awaaz": 3, "Purdue Taal": 4},
    ),
    Competition(
        "spartan_sitara",
        2,
        [
            "Wisconsin Waale",
            "Astha Acappella",
            "UC Junoon",
            "OSU Dhadkan",
            "Dhamakapella",
            "Duke Deewana",
            "Gator Awaaz",
            "Humraah at IU",
        ],
        [0.74, 0.63, 0.50, 0.35, 1.00, 0.17, -0.03, 0.84],
        {"Dhamakapella": 1, "Humraah at IU": 2, "Wisconsin Waale": 3},
    ),
    Competition(
        "davis_dhwani",
        2,
        [
            "UW Awaaz",
            "TAMU Swaram",
            "Hum A Cappella",
            "UMD Anokha",
            "Stanford Raagapella",
            "UC Berkeley Dilse",
            "UCSC Taza Taal",
            "UCLA Naya Zamaana",
        ],
        [0.754, 1.00, 0.469, 0.961, 0.781, 0.167, -0.116, -0.341],
        {
            "TAMU Swaram": 1,
            "UMD Anokha": 2,
            "Stanford Raagapella": 3,
            "UW Awaaz": 4,
            "Hum A Cappella": 5,
        },
    ),
    Competition(
        "jeena",
        3,
        [
            "TAMU Swaram",
            "UW Awaaz",
            "UTD Dhunki",
            "Illini Awaaz",
            "UGA Kalakaar",
            "Wisconsin Waale",
            "Drexel Dhvani",
        ],
        [1.235, 0.735, 0.615, 0.385, 0.3, 0.615, -0.385],
        {"TAMU Swaram": 1, "UW Awaaz": 2, "UTD Dhunki": 3},
    ),
    Competition(
        "awaazein",
        3,
        [
            "GT Taal Tadka",
            "Stanford Raagapella",
            "UCSB Ravaani",
            "MN Fitoor",
            "BU Suno",
            "Rice Basmati Beats",
            "UCLA Naya Zamaana",
            "Emory Suri",
            "UMD Anokha",
        ],
        [0.51, 0.78, 0.63, 1.005, 0.55, 0.74, 0.11, -0.39, 1.06],
        {"UMD Anokha": 1, "MN Fitoor": 2, "Stanford Raagapella": 3},
    ),
    Competition(
        "boston_bandish",
        3,
        [
            "Humraah at IU",
            "JHU Kranti",
            "OSU Dhadkan",
            "Purdue Taal",
            "Rutgers RAAG",
            "UCSC Taza Taal",
            "UCSD Sitaare",
            "UMiami Tufaan",
        ],
        [0.445, 0.835, 0.63, 1.175, 0.75, -0.045, 0.4, -0.02],
        {"Purdue Taal": 1, "JHU Kranti": 2, "Rutgers RAAG": 3},
    ),
]

KNOWN_0207 = {
    "Dhamakapella": 1531.39,
    "UCD Jhankaar": 1523.56,
    "UTD Dhunki": 1520.40,
    "TAMU Swaram": 1515.84,
    "MN Fitoor": 1512.22,
    "Illini Awaaz": 1512.03,
    "UMD Anokha": 1511.03,
    "Humraah at IU": 1509.90,
    "UGA Kalakaar": 1507.28,
    "Stanford Raagapella": 1507.10,
}

KNOWN_0220 = {
    "Dhamakapella": 1531.30,
    "TAMU Swaram": 1527.31,
    "UTD Dhunki": 1524.61,
    "UCD Jhankaar": 1523.66,
    "Purdue Taal": 1522.07,
    "MN Fitoor": 1520.45,
    "UMD Anokha": 1520.01,
    "Stanford Raagapella": 1511.09,
    "UW Awaaz": 1510.93,
    "Illini Awaaz": 1509.93,
}

TOP10_0207 = [
    "Dhamakapella",
    "UCD Jhankaar",
    "UTD Dhunki",
    "TAMU Swaram",
    "MN Fitoor",
    "Illini Awaaz",
    "UMD Anokha",
    "Humraah at IU",
    "UGA Kalakaar",
    "Stanford Raagapella",
]

TOP10_0220 = [
    "Dhamakapella",
    "TAMU Swaram",
    "UTD Dhunki",
    "UCD Jhankaar",
    "Purdue Taal",
    "MN Fitoor",
    "UMD Anokha",
    "Stanford Raagapella",
    "UW Awaaz",
    "Illini Awaaz",
]

# Joint-constrained fitted z-scores (valid fit, not unique truth)
JOINT_FIT_SCORES = {
    "steel_city_sapna": [1, 0.82, 0.6, 0.53, 0.43, 0.3, 0.14, -0.06],
    "buckeye_laya": [0.105046, -0.105265, 0.161161, 0.41304, -0.262462, 1, 0.570758, 0.537466],
    "gathe_raho": [-0.1, 1, 0.58, 0.57, -0.31, -0.45, -0.53, 0.21],
    "spartan_sitara": [0.74, 0.63, 0.5, 0.35, 1, 0.17, -0.03, 0.84],
    "davis_dhwani": [0.551273, 1, -0.137193, 0.930039, 0.62303, -0.298526, -0.888837, -1.334519],
    "jeena": [1, 0.416472, 0.330436, -0.008563, -0.244837, 0.317704, -0.929837],
    "awaazein": [0.45, 0.72, 0.57, 0.945, 0.49, 0.68, 0.05, -0.45, 1],
    "boston_bandish": [0.27, 0.66, 0.455, 1, 0.575, -0.22, 0.225, -0.195],
}
