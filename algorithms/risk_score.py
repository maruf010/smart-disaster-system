def calculate_risk(life_threat, injured, children_elderly, people_affected, resource_shortage):
    score = 0
    if life_threat:
        score += 40
    if injured > 0:
        score += min(20, injured * 5)
    if children_elderly > 0:
        score += min(15, children_elderly * 3)
    if people_affected > 0:
        score += min(15, max(5, people_affected // 5))
    if resource_shortage:
        score += 10

    score = min(100, score)

    if score <= 30:
        level = "LOW"
    elif score <= 50:
        level = "MODERATE"
    elif score <= 70:
        level = "HIGH"
    else:
        level = "CRITICAL"
    return score, level
