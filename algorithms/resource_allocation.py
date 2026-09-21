def proportional_allocation(total_resource, area_populations):
    total_population = sum(area_populations.values())
    if total_population <= 0:
        return {}

    result = {}
    remaining = float(total_resource)

    items = list(area_populations.items())
    for index, (area, population) in enumerate(items):
        if index == len(items) - 1:
            allocated = round(max(0, remaining), 2)
        else:
            allocated = round((population / total_population) * total_resource, 2)
            remaining -= allocated
        result[area] = allocated
    return result
