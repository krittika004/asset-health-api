import numpy as np

def adaptive_mean(vals: np.ndarray, k_outlier: float = 3.5, max_frac: float = 0.05) -> float:
    if vals.size == 0:
        return np.nan
    med = np.median(vals)
    mad = np.median(np.abs(vals - med))
    if mad == 0:
        return float(med)
    sigma = 1.4826 * mad
    mask_out = np.abs(vals - med) > k_outlier * sigma
    if mask_out.sum() / vals.size <= max_frac:
        vals = vals[~mask_out]
    return float(vals.mean())

def analyze_sensor_data_duo(data_list: list[dict],
                        thresholds_json: dict,
                        field_alias: dict,
                        k_outlier: float = 3.5,
                        max_frac: float = 0.05):
    details = {}
    for log_key, base in field_alias.items():
        vals = np.fromiter((row[log_key] for row in data_list), dtype=float)
        avg = adaptive_mean(vals, k_outlier, max_frac)
        low = thresholds_json.get(f"{base}_healthy", float('-inf'))
        high = thresholds_json.get(f"{base}_warning", float('inf'))
        if low <= avg <= high:
            status = "GOOD"
        else:
            status = "NEEDS MAINTENANCE"
        details[log_key] = {
            "average": avg,
            "status": status,
            "low": low,
            "high": high
        }
    if any(d["status"] == "NEEDS MAINTENANCE" for d in details.values()):
        overall = "MACHINE NEEDS MAINTENANCE"
    else:
        overall = "MACHINE IS IN GOOD CONDITION"
    if overall == "MACHINE IS IN GOOD CONDITION":
        cause = "All parameters are within the specified bands."
    else:
        def deviation(item):
            fld, info = item
            if info["average"] < info["low"]:
                return info["low"] - info["average"]
            else:
                return info["average"] - info["high"]
        fld, info = max(details.items(), key=deviation)
        direction = "below" if info["average"] < info["low"] else "above"
        bound = info["low"] if direction == "below" else info["high"]
        cause = (f"Issue in '{fld}': average {info['average']:.2f} is "
                 f"{direction} the acceptable band ({bound}).")
    return overall, cause, details

def adaptive_mean_quad(vals: np.ndarray, k_outlier: float = 3.5, max_frac: float = 0.05) -> float:
    if vals.size == 0:
        return np.nan
    med = np.median(vals)
    mad = np.median(np.abs(vals - med))
    if mad == 0:
        return float(med)
    sigma = 1.4826 * mad
    mask_out = np.abs(vals - med) > k_outlier * sigma
    if mask_out.sum() / vals.size <= max_frac:
        vals = vals[~mask_out]
    return float(vals.mean())

def analyze_sensor_data_quad(data_list: list[dict],
                        thresholds_json: dict,
                        field_alias: dict,
                        k_outlier: float = 3.5,
                        max_frac: float = 0.05):
    details = {}
    for log_key, base in field_alias.items():
        vals = np.fromiter((row.get(log_key, np.nan) for row in data_list), dtype=float)
        vals = vals[~np.isnan(vals)]
        avg  = adaptive_mean_quad(vals, k_outlier, max_frac)
        low  = thresholds_json.get(f"{base}_healthy", float('-inf'))
        high = thresholds_json.get(f"{base}_warning", float('inf'))
        status = "GOOD" if low <= avg <= high else "NEEDS MAINTENANCE"
        details[log_key] = {
            "average": avg,
            "status" : status,
            "low"    : low,
            "high"   : high
        }
    if any(d["status"] == "NEEDS MAINTENANCE" for d in details.values()):
        overall = "MACHINE NEEDS MAINTENANCE"
    else:
        overall = "MACHINE IS IN GOOD CONDITION"
    if overall == "MACHINE IS IN GOOD CONDITION":
        cause = "All parameters are within the specified bands."
    else:
        def deviation(item):
            fld, info = item
            if info["average"] < info["low"]:
                return info["low"] - info["average"]
            return info["average"] - info["high"]
        fld, info = max(details.items(), key=deviation)
        direction = "below" if info["average"] < info["low"] else "above"
        bound     = info["low"] if direction == "below" else info["high"]
        cause = (f"Issue in '{fld}': average {info['average']:.2f} is "
                 f"{direction} the acceptable band ({bound}).")
    return overall, cause, details

field_alias_duo = {
    "temperature_one": "temperature_skin",
    "temperature_two": "temperature_bearing",
    "vibration_x": "vibration_X",
    "vibration_y": "vibration_Y",
    "vibration_z": "vibration_Z"
}

field_alias = {
    "temperature_one"  : "temperature_skin",
    "temperature_two"  : "temperature_bearing",
    "vibration_x"      : "vibration_X",
    "vibration_y"      : "vibration_Y",
    "vibration_z"      : "vibration_Z",
    "magnetic_flux_x"  : "magnetic_flux_X",
    "magnetic_flux_y"  : "magnetic_flux_Y",
    "magnetic_flux_z"  : "magnetic_flux_Z",
    "ultrasound_one"   : "ultrasound_one",
    "ultrasound_two"   : "ultrasound_two"
} 