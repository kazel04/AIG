def is_opponent_in_range(character, opponent):
    opponent_distance = (character.position - opponent.position).length()
    if opponent_distance <= character.min_target_distance:
        return opponent