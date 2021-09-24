import random
import matplotlib.pyplot as plt


def main():
    amount_of_attacks = 10000
    enemy_ac_lower = 10
    enemy_ac_higher = 18
    attack_bonus = 2
    damage_dice = {"d6": 2}
    damage_bonus = 2
    re_rolls = [1, 2]

    stats = simulate(amount_of_attacks, enemy_ac_lower, enemy_ac_higher, attack_bonus, damage_dice, damage_bonus, re_rolls)

    x_axis = []
    y_axis = []
    for enemy_ac in stats:
        x_axis.append(int(enemy_ac))
        y_axis.append(stats[enemy_ac][0])

    plt.plot(x_axis, y_axis)
    plt.show()


def simulate(amount_of_attacks, enemy_ac_lower, enemy_ac_higher, attack_bonus, damage_dice, damage_bonus, re_rolls=None,
             disadvantage=False, advantage=False, crit_floor=20):
    stats = {}

    for enemy_ac in range(enemy_ac_lower, enemy_ac_higher + 1):
        amount_of_hits = 0
        amount_of_misses = 0
        amount_of_crits = 0
        damage_rolls = []

        for attack in range(amount_of_attacks):
            is_hit, is_crit, die, bonus = roll_to_hit(enemy_ac, attack_bonus, disadvantage, advantage, crit_floor)
            if is_hit:
                amount_of_hits += 1
                crit_multiplier = 1
                if is_crit:
                    amount_of_crits += 1
                    crit_multiplier = 2

                damage, dice, bonus = roll_damage(damage_dice, damage_bonus, crit_multiplier, re_rolls)
                damage_rolls.append(damage)

            else:
                amount_of_misses += 1

        accuracy = to_percentage(amount_of_hits, amount_of_attacks)
        precision = to_percentage(amount_of_crits, amount_of_hits)
        mean_damage = 0
        if not (sum(damage_rolls) == 0 or len(damage_rolls) == 0):
            mean_damage = sum(damage_rolls) // len(damage_rolls)

        data = [accuracy, precision, mean_damage]
        stats[str(enemy_ac)] = data

    return stats


def to_percentage(frequency, max_frequency):
    if frequency == 0 or max_frequency == 0:
        return 0
    percentage_string = ("%.0f%%" % (max_frequency * 1.0 / frequency))
    return int(percentage_string[:-1])


def roll_dice(sides, amount=1, re_rolls=None):
    resulting_dice = []
    for i in range(amount):
        resulting_dice.append(random.randint(0, sides))

    if re_rolls:
        for rolled_die_index in range(len(resulting_dice)):
            if resulting_dice[rolled_die_index] in re_rolls:
                resulting_dice[rolled_die_index] = random.randint(0, sides)

    return resulting_dice


def roll_to_hit(enemy_ac, attack_bonus, disadvantage=False, advantage=False, crit_floor=20):
    initial_attack_roll = roll_dice(20, 1)
    if disadvantage == advantage:
        if initial_attack_roll[0] >= crit_floor:
            return True, True, initial_attack_roll[0], attack_bonus
        elif initial_attack_roll[0] + attack_bonus > enemy_ac:
            return True, False, initial_attack_roll[0], attack_bonus
        else:
            return False, False, initial_attack_roll[0], attack_bonus
    else:
        second_attack_roll = roll_dice(20, 1)
        if disadvantage:
            lowest_roll = min(initial_attack_roll[0], second_attack_roll[0])
            if lowest_roll >= crit_floor:
                return True, True, lowest_roll, attack_bonus
            elif lowest_roll + attack_bonus > enemy_ac:
                return True, False, lowest_roll, attack_bonus
            else:
                return False, False, lowest_roll, attack_bonus
        else:
            highest_roll = max(initial_attack_roll[0], second_attack_roll[0])
            if highest_roll >= crit_floor:
                return True, True, highest_roll, attack_bonus
            elif highest_roll + attack_bonus > enemy_ac:
                return True, False, highest_roll, attack_bonus
            else:
                return False, False, highest_roll, attack_bonus


def roll_damage(dice, damage_bonus, dice_multiplier=1, re_rolls=None):
    resulting_dice = []
    for die, amount in dice.items():
        resulting_dice += roll_dice(int(die[-1]), amount * dice_multiplier, re_rolls)

    return sum(resulting_dice) + damage_bonus, resulting_dice, damage_bonus


if __name__ == "__main__":
    main()
