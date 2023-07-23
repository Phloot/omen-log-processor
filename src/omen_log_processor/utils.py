import json

# Function to process player data and extract the desired fields
def process_keys_from_log(player_data):
    players_info = []
    for player in player_data.get("players", []):
        player_info = {}
        player_info["account"] = player.get("account", None)
        player_info["profession"] = player.get("profession", None)
        player_info["guildID"] = player.get("guildID", None)

        # DPS data
        dps_all = player.get("dpsAll", [])
        if dps_all:
            dps_data = dps_all[0]
            player_info["dps"] = dps_data.get("dps", None)
            player_info["damage"] = dps_data.get("damage", None)
            player_info["powerDps"] = dps_data.get("powerDps", None)
            player_info["powerDamage"] = dps_data.get("powerDamage", None)

        # Stats data
        stats_all = player.get("statsAll", [])
        if stats_all:
            stats_data = stats_all[0]
            player_info["stackDist"] = stats_data.get("stackDist", None)
            player_info["distToCom"] = stats_data.get("distToCom", None)
            player_info["swapCount"] = stats_data.get("swapCount", None)
            player_info["killed"] = stats_data.get("killed", None)
            player_info["downed"] = stats_data.get("downed", None)
            player_info["downContribution"] = stats_data.get("downContribution", None)

        # Defenses data
        defenses = player.get("defenses", [])
        if defenses:
            defenses_data = defenses[0]
            player_info["damageTaken"] = defenses_data.get("damageTaken", None)
            player_info["blockedCount"] = defenses_data.get("blockedCount", None)
            player_info["evadedCount"] = defenses_data.get("evadedCount", None)
            player_info["missedCount"] = defenses_data.get("missedCount", None)
            player_info["dodgeCount"] = defenses_data.get("dodgeCount", None)
            player_info["downCount"] = defenses_data.get("downCount", None)
            player_info["deadCount"] = defenses_data.get("deadCount", None)

        # Support data
        support = player.get("support", [])
        if support:
            support_data = support[0]
            player_info["boonStrips"] = support_data.get("boonStrips", None)
            player_info["resurrects"] = support_data.get("resurrects", None)
            player_info["condiCleanse"] = support_data.get("condiCleanse", None)
            player_info["condiCleanseSelf"] = support_data.get("condiCleanseSelf", None)

        # Boons data
        boons = player.get("groupBuffs", [])
        boon_info = []
        for boon in boons:
            for buff_data in boon.get("buffData", []):
                generation = buff_data.get("generation", None)
                wasted = buff_data.get("wasted", None)
                total = generation - wasted if generation is not None and wasted is not None else None
                boon_id = boon.get("id", None)

                # Extract the boon name from buffMap using the modified ID
                boon_name = player_data.get("buffMap", {}).get(f'b{boon_id}', {}).get("name", None)

                boon_info.append({
                    "boonName": boon_name,
                    "generation": generation,
                    "wasted": wasted,
                    "total": total
                })
        player_info["boonInfo"] = boon_info
        players_info.append(player_info)
    return players_info
