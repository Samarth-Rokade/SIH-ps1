"""Approximate lat/long centroids for Indian states/UTs plus the non-state
labels that appear in projects.csv (Multi-States, PAN India, Offshore).

projects.csv has no per-project coordinates, so the map endpoint places each
project near its state's centroid with a small random jitter (see
backend/app/ml/seed.py). These are approximate display centroids, not
precise geographic boundaries.
"""
from __future__ import annotations

STATE_CENTROIDS: dict[str, tuple[float, float]] = {
    "Andaman & Nicobar": (11.7401, 92.6586),
    "Andhra Pradesh": (15.9129, 79.7400),
    "Arunachal Pradesh": (28.2180, 94.7278),
    "Assam": (26.2006, 92.9376),
    "Bihar": (25.0961, 85.3131),
    "Chhattisgarh": (21.2787, 81.8661),
    "Dadra & Nagar Haveli and Daman & Diu": (20.1809, 73.0169),
    "Delhi": (28.7041, 77.1025),
    "Goa": (15.2993, 74.1240),
    "Gujarat": (22.2587, 71.1924),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jammu and Kashmir": (33.7782, 76.5762),
    "Jharkhand": (23.6102, 85.2799),
    "Karnataka": (15.3173, 75.7139),
    "Kerala": (10.8505, 76.2711),
    "Ladakh": (34.1526, 77.5771),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Maharashtra": (19.7515, 75.7139),
    "Manipur": (24.6637, 93.9063),
    "Meghalaya": (25.4670, 91.3662),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (26.1584, 94.5624),
    "Odisha": (20.9517, 85.0985),
    "Puducherry": (11.9416, 79.8083),
    "Punjab": (31.1471, 75.3412),
    "Rajasthan": (27.0238, 74.2179),
    "Sikkim": (27.5330, 88.5122),
    "Tamil Nadu": (11.1271, 78.6569),
    "Telangana": (18.1124, 79.0193),
    "Tripura": (23.9408, 91.9882),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.9868, 87.8550),
    # Non-state labels used for projects that don't map to one state.
    "Multi-States": (22.3511, 78.6677),  # geographic centre of India
    "PAN India": (22.3511, 78.6677),
    "Offshore": (15.0, 73.0),  # Arabian Sea, off the Konkan coast
}

DEFAULT_CENTROID = (22.3511, 78.6677)


def get_centroid(state: str) -> tuple[float, float]:
    return STATE_CENTROIDS.get(state, DEFAULT_CENTROID)
