import math

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def distance_robot_to_rect(robot, obstacle):
    rx, ry = robot.x, robot.y

    closest_x = clamp(rx, obstacle.x, obstacle.x + obstacle.width)
    closest_y = clamp(ry, obstacle.y, obstacle.y + obstacle.height)

    dx = closest_x - rx
    dy = closest_y - ry

    distance = math.sqrt(dx * dx + dy * dy)
    return distance, dx, dy

def robot_collides_with_obstacle(robot, obstacle):
    return robot.get_rect().colliderect(obstacle)

def compute_real_ttc(robot, obstacle):
    # collision réelle
    if robot_collides_with_obstacle(robot, obstacle):
        return 0.0

    distance, dx, dy = distance_robot_to_rect(robot, obstacle)

    speed = robot.speed
    if abs(speed) < 0.01:
        return None

    angle_rad = math.radians(robot.angle)
    dir_x = math.cos(angle_rad)
    dir_y = math.sin(angle_rad)

    if distance == 0:
        return 0.0

    to_obs_x = dx / distance
    to_obs_y = dy / distance

    closing_speed = speed * (dir_x * to_obs_x + dir_y * to_obs_y)

    if closing_speed <= 0:
        return None

    ttc = distance / closing_speed

    if ttc > 999:
        return None

    return round(ttc, 2)

def detect_from_simulation(env, robot):
    detections = []

    for obs in env.obstacles:
        ttc = compute_real_ttc(robot, obs)

        detections.append({
            "label": "obstacle",
            "confidence": 1.0,
            "x": obs.x,
            "y": obs.y,
            "w": obs.width,
            "h": obs.height,
            "ttc": ttc
        })

    return detections