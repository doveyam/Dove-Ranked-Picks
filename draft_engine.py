from meta import META_TIERS


META_POINTS = {
    "S": 60,
    "A": 45,
    "B": 30,
    "C": 15,
    "D": 5,
    "F": 0
}

MAP_POINTS = {
    1: 50,
    2: 45,
    3: 40,
    4: 35,
    5: 30,
    6: 25,
    7: 20,
    8: 15,
    9: 10,
    10: 5
}


def get_meta_score(brawler):

    tier = META_TIERS.get(brawler)

    if tier is None:
        return 0

    return META_POINTS.get(tier, 0)


def get_map_score(brawler, map_data):

    picks = map_data.get("first_picks", [])

    if brawler not in picks:
        return 0

    position = picks.index(brawler) + 1

    return MAP_POINTS.get(position, 0)


def calculate_score(
    candidate,
    enemy_brawler,
    counters,
    map_data
):

    score = 0

    enemy_counters = counters.get(enemy_brawler, [])

    if candidate in enemy_counters:
        score += 100

    score += get_map_score(candidate, map_data)

    score += get_meta_score(candidate)

    return score


def get_recommendations(
    enemy_brawlers,
    map_data,
    counters
):

    results = {}

    for enemy in enemy_brawlers:

        enemy_counters = counters.get(enemy, [])

        for candidate in enemy_counters:

            score = calculate_score(
                candidate,
                enemy,
                counters,
                map_data
            )

            results[candidate] = (
                results.get(candidate, 0)
                + score
            )

    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_results[:5]