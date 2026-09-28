"""
eRTMAC-NWIS Trajectory Engine: Minimum Curvature Method (MCM)
Compliant with API / SPE Bulletin D12 standards.
Transforms directional survey stations (MD, Inc, Azi) into 3D spatial trajectories
with PostGIS EPSG:3857 PointZ geometry support.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional


@dataclass
class SurveyStation:
    """Input directional survey measurement."""
    md_m: float       # Measured Depth (meters)
    inc_deg: float    # Inclination from vertical (degrees, 0 = vertical)
    azi_deg: float    # Azimuth from True North (degrees, 0-360)


@dataclass
class TrajectoryStation:
    """Computed 3D trajectory position station."""
    md_m: float
    inc_deg: float
    azi_deg: float
    tvd_m: float               # True Vertical Depth (meters from KB)
    tvdss_m: float             # Subsea TVD (TVD - KB_elevation)
    north_m: float             # Local Northing offset (meters)
    east_m: float              # Local Easting offset (meters)
    dogleg_deg_per_30m: float  # Dogleg Severity (deg / 30m)
    x_3857: float              # Web Mercator Easting (EPSG:3857)
    y_3857: float              # Web Mercator Northing (EPSG:3857)
    z_3857: float              # Elevation AMSL (meters, -tvdss_m)
    geom_wkt: str              # WKT: POINT Z (X Y Z)
    geom_ewkt: str             # PostGIS EWKT: SRID=3857;POINT Z (X Y Z)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "md_m": self.md_m,
            "inc_deg": self.inc_deg,
            "azi_deg": self.azi_deg,
            "tvd_m": self.tvd_m,
            "tvdss_m": self.tvdss_m,
            "north_m": self.north_m,
            "east_m": self.east_m,
            "dogleg_deg_per_30m": self.dogleg_deg_per_30m,
            "x_3857": self.x_3857,
            "y_3857": self.y_3857,
            "z_3857": self.z_3857,
            "geom_wkt": self.geom_wkt,
            "geom_ewkt": self.geom_ewkt,
        }


class MCMTrajectoryEngine:
    """
    High-precision, numerically stable Minimum Curvature Method (MCM) engine.
    """
    R_EARTH_3857: float = 6378137.0  # WGS84 Spherical Mercator Semi-Major Axis (meters)

    @classmethod
    def wgs84_to_epsg3857(cls, lat_deg: float, lon_deg: float) -> Tuple[float, float]:
        """
        Converts WGS84 geographic coordinates (lat, lon in degrees)
        to Web Mercator meters (EPSG:3857).
        """
        rad_lat = math.radians(lat_deg)
        rad_lon = math.radians(lon_deg)
        x = cls.R_EARTH_3857 * rad_lon
        # Guard against pole singularities
        clamped_rad_lat = max(-math.radians(85.05112878), min(math.radians(85.05112878), rad_lat))
        y = cls.R_EARTH_3857 * math.log(math.tan(math.pi / 4.0 + clamped_rad_lat / 2.0))
        return x, y

    @classmethod
    def compute_step(
        cls,
        md1: float, inc1_deg: float, azi1_deg: float,
        md2: float, inc2_deg: float, azi2_deg: float
    ) -> Tuple[float, float, float, float, float]:
        """
        Calculates incremental 3D displacements between two survey stations.

        Returns:
            Tuple[d_tvd, d_north, d_east, beta, dls_deg_30m]
        """
        d_md = md2 - md1
        if d_md < 0.0:
            raise ValueError(f"Invalid MD step: md2 ({md2}) must be greater than or equal to md1 ({md1})")
        if d_md == 0.0:
            return 0.0, 0.0, 0.0, 0.0, 0.0

        i1 = math.radians(inc1_deg)
        i2 = math.radians(inc2_deg)
        a1 = math.radians(azi1_deg)
        a2 = math.radians(azi2_deg)

        # 1. Total Subtended Dogleg Angle (beta)
        cos_beta = math.cos(i1) * math.cos(i2) + math.sin(i1) * math.sin(i2) * math.cos(a2 - a1)

        # Numerical Stability Guard 1: Strict floating-point clamping to [-1.0, 1.0]
        cos_beta_clamped = max(-1.0, min(1.0, cos_beta))
        beta = math.acos(cos_beta_clamped)

        # Numerical Stability Guard 2: Curvature Ratio Factor singularity resolution
        if abs(beta) < 1e-6:
            # Taylor series expansion: RF = 1 + beta^2 / 12 + beta^4 / 120
            rf = 1.0 + (beta ** 2) / 12.0
        else:
            rf = (2.0 / beta) * math.tan(beta / 2.0)

        # 2. Incremental Displacements
        half_dmd_rf = (d_md / 2.0) * rf
        d_tvd = half_dmd_rf * (math.cos(i1) + math.cos(i2))
        d_north = half_dmd_rf * (math.sin(i1) * math.cos(a1) + math.sin(i2) * math.cos(a2))
        d_east = half_dmd_rf * (math.sin(i1) * math.sin(a1) + math.sin(i2) * math.sin(a2))

        # 3. Dogleg Severity in deg/30m
        dls_deg_30m = (beta / d_md) * 30.0 * (180.0 / math.pi)

        return d_tvd, d_north, d_east, beta, dls_deg_30m

    @classmethod
    def calculate_trajectory(
        cls,
        surveys: List[Tuple[float, float, float]],  # List of (MD, Inc, Azi)
        surface_lat: float,
        surface_lon: float,
        kb_elevation_m: float,
        z_elevation_mode: str = "AMSL"  # "AMSL" (-TVDSS) or "DEPTH" (+TVDSS)
    ) -> List[TrajectoryStation]:
        """
        Computes the complete 3D trajectory sequence from surface to TD.
        """
        if not surveys:
            return []

        # Sort surveys by MD and eliminate duplicates
        sorted_surveys = sorted(surveys, key=lambda s: s[0])
        cleaned_surveys: List[Tuple[float, float, float]] = []
        for s in sorted_surveys:
            if not cleaned_surveys or s[0] > cleaned_surveys[-1][0] + 1e-4:
                cleaned_surveys.append(s)

        # Guarantee surface origin station at MD = 0
        if cleaned_surveys[0][0] > 0.0:
            cleaned_surveys.insert(0, (0.0, 0.0, cleaned_surveys[0][2]))

        x0, y0 = cls.wgs84_to_epsg3857(surface_lat, surface_lon)

        stations: List[TrajectoryStation] = []

        # Surface Station (k = 0)
        md0, inc0, azi0 = cleaned_surveys[0]
        tvd0 = 0.0
        tvdss0 = tvd0 - kb_elevation_m
        north0 = 0.0
        east0 = 0.0
        dls0 = 0.0

        x0_stat = x0 + east0
        y0_stat = y0 + north0
        z0_stat = -tvdss0 if z_elevation_mode == "AMSL" else tvdss0

        stations.append(TrajectoryStation(
            md_m=round(md0, 2),
            inc_deg=round(inc0, 3),
            azi_deg=round(azi0, 3),
            tvd_m=round(tvd0, 2),
            tvdss_m=round(tvdss0, 2),
            north_m=round(north0, 3),
            east_m=round(east0, 3),
            dogleg_deg_per_30m=round(dls0, 3),
            x_3857=round(x0_stat, 3),
            y_3857=round(y0_stat, 3),
            z_3857=round(z0_stat, 3),
            geom_wkt=f"POINT Z ({x0_stat:.3f} {y0_stat:.3f} {z0_stat:.3f})",
            geom_ewkt=f"SRID=3857;POINT Z ({x0_stat:.3f} {y0_stat:.3f} {z0_stat:.3f})"
        ))

        # Integrate subsequent stations (k >= 1)
        cum_tvd = tvd0
        cum_north = north0
        cum_east = east0

        for i in range(1, len(cleaned_surveys)):
            md1, inc1, azi1 = cleaned_surveys[i - 1]
            md2, inc2, azi2 = cleaned_surveys[i]

            d_tvd, d_north, d_east, _, dls = cls.compute_step(
                md1, inc1, azi1,
                md2, inc2, azi2
            )

            cum_tvd += d_tvd
            cum_north += d_north
            cum_east += d_east

            tvdss = cum_tvd - kb_elevation_m
            xs = x0 + cum_east
            ys = y0 + cum_north
            zs = -tvdss if z_elevation_mode == "AMSL" else tvdss

            stations.append(TrajectoryStation(
                md_m=round(md2, 2),
                inc_deg=round(inc2, 3),
                azi_deg=round(azi2, 3),
                tvd_m=round(cum_tvd, 2),
                tvdss_m=round(tvdss, 2),
                north_m=round(cum_north, 3),
                east_m=round(cum_east, 3),
                dogleg_deg_per_30m=round(dls, 3),
                x_3857=round(xs, 3),
                y_3857=round(ys, 3),
                z_3857=round(zs, 3),
                geom_wkt=f"POINT Z ({xs:.3f} {ys:.3f} {zs:.3f})",
                geom_ewkt=f"SRID=3857;POINT Z ({xs:.3f} {ys:.3f} {zs:.3f})"
            ))

        return stations


def compute_mcm_station(
    md1: float,
    inc1_deg: float,
    azi1_deg: float,
    md2: float,
    inc2_deg: float,
    azi2_deg: float,
    prev_tvd: float = 0.0,
    prev_north: float = 0.0,
    prev_east: float = 0.0,
    kb_elevation_m: float = 112.0
) -> Dict[str, float]:
    """
    Functional interface to compute single MCM station transition.
    """
    delta_md = md2 - md1
    if delta_md < 0:
        raise ValueError(f"delta_md cannot be negative: md1={md1}, md2={md2}")

    if delta_md == 0:
        tvd = prev_tvd
        north = prev_north
        east = prev_east
        return {
            "md_m": md2,
            "inc_deg": inc2_deg,
            "azi_deg": azi2_deg,
            "delta_md": 0.0,
            "beta_rad": 0.0,
            "rf": 1.0,
            "delta_tvd": 0.0,
            "delta_north": 0.0,
            "delta_east": 0.0,
            "tvd_m": tvd,
            "tvdss_m": tvd - kb_elevation_m,
            "north_m": north,
            "east_m": east,
            "dls_deg_per_30m": 0.0
        }

    inc1 = math.radians(inc1_deg)
    inc2 = math.radians(inc2_deg)
    azi1 = math.radians(azi1_deg)
    azi2 = math.radians(azi2_deg)

    cos_beta = math.cos(inc1) * math.cos(inc2) + math.sin(inc1) * math.sin(inc2) * math.cos(azi2 - azi1)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)

    if beta < 1e-6:
        rf = 1.0 + (beta ** 2) / 12.0
    else:
        rf = (2.0 / beta) * math.tan(beta / 2.0)

    delta_tvd = (delta_md / 2.0) * (math.cos(inc1) + math.cos(inc2)) * rf
    delta_north = (delta_md / 2.0) * (math.sin(inc1) * math.cos(azi1) + math.sin(inc2) * math.cos(azi2)) * rf
    delta_east = (delta_md / 2.0) * (math.sin(inc1) * math.sin(azi1) + math.sin(inc2) * math.sin(azi2)) * rf

    tvd = prev_tvd + delta_tvd
    north = prev_north + delta_north
    east = prev_east + delta_east
    tvdss = tvd - kb_elevation_m
    dls = (beta / delta_md) * 30.0 * (180.0 / math.pi)

    return {
        "md_m": md2,
        "inc_deg": inc2_deg,
        "azi_deg": azi2_deg,
        "delta_md": delta_md,
        "beta_rad": beta,
        "rf": rf,
        "delta_tvd": delta_tvd,
        "delta_north": delta_north,
        "delta_east": delta_east,
        "tvd_m": tvd,
        "tvdss_m": tvdss,
        "north_m": north,
        "east_m": east,
        "dls_deg_per_30m": dls
    }


def calculate_dogleg_angle_rad(inc1_deg: float, azi1_deg: float, inc2_deg: float, azi2_deg: float) -> float:
    """Calculates total subtended dogleg angle beta in radians between two directional stations."""
    i1 = math.radians(inc1_deg)
    i2 = math.radians(inc2_deg)
    a1 = math.radians(azi1_deg)
    a2 = math.radians(azi2_deg)
    cos_beta = math.cos(i1) * math.cos(i2) + math.sin(i1) * math.sin(i2) * math.cos(a2 - a1)
    return math.acos(max(-1.0, min(1.0, cos_beta)))


def calculate_ratio_factor(beta_rad: float) -> float:
    """Calculates curvature ratio factor RF with small angle Taylor expansion."""
    if abs(beta_rad) < 1e-6:
        return 1.0 + (beta_rad ** 2) / 12.0
    return (2.0 / beta_rad) * math.tan(beta_rad / 2.0)


# Backward-compatible alias
minimum_curvature_step = compute_mcm_station
