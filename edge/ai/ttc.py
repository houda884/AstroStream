def compute_ttc(obj, speed=1.0):
    width = obj.get("w", 0)

    if width <= 0 or speed <= 0:
        return None

    estimated_distance = 1000 / width
    ttc = estimated_distance / speed
    return round(ttc, 2)