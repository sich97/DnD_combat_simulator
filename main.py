import random
import matplotlib.pyplot as plt

PRECISION = False


def main():
    name = "Shortsword +2"
    settings = {"amount_of_attacks": 1000000,
                "enemy_ac_lower": 11,
                "enemy_ac_higher": 21,
                "attack_bonus": 9,
                "damage_dice": {"d6": 1},
                "damage_bonus": 6,
                "re_rolls": [],
                "disadvantage": False,
                "advantage": False,
                "crit_floor": 20}

    stats, min_damage, max_damage, damage_total = simulate(settings["amount_of_attacks"],
                                                           settings["enemy_ac_lower"], settings["enemy_ac_higher"],
                                                           settings["attack_bonus"], settings["damage_dice"],
                                                           settings["damage_bonus"], settings["re_rolls"],
                                                           settings["disadvantage"], settings["advantage"],
                                                           settings["crit_floor"])

    plt.axhline(y=min_damage, color="darkgreen", linestyle='dashed')
    plt.text(settings["enemy_ac_lower"] - 0.75, -9.5, "Min damage: " + str(min_damage),
             verticalalignment="center")
    plt.axhline(y=max_damage, color="darkgreen", linestyle='dashed')
    plt.text(settings["enemy_ac_lower"] - 0.75, max_damage + 1.5, "Max damage: " + str(max_damage),
             verticalalignment="center")

    highest_precision = 0
    highest_accuracy = 0
    lowest_accuracy = 0
    for data_key in stats[str(settings["enemy_ac_lower"])]:
        x_axis = []
        y_axis = []

        for enemy_ac in stats:
            x_axis.append(int(enemy_ac))
            y_axis.append(stats[enemy_ac][data_key])

            if data_key == "precision":
                highest_precision = max(highest_precision, stats[enemy_ac][data_key])
            elif data_key == "accuracy":
                highest_accuracy = max(highest_accuracy, stats[enemy_ac][data_key])
                if lowest_accuracy == 0:
                    lowest_accuracy = stats[enemy_ac][data_key]
                else:
                    lowest_accuracy = min(lowest_accuracy, stats[enemy_ac][data_key])

        if data_key == "mean_damage":
            plt.bar(x_axis, y_axis, color="green", label="Mean damage")
        elif data_key == "accuracy":
            plt.plot(x_axis, y_axis, color="blue", label="Accuracy", linestyle='solid')
        elif data_key == "precision" and PRECISION:
            plt.plot(x_axis, y_axis, color="red", label="Precision on hit", linestyle='solid')

    damage_total_string_temp = str(damage_total)[::-1]
    damage_total_string_list = []
    for number_index in range(len(damage_total_string_temp)):
        damage_total_string_list.insert(0, damage_total_string_temp[number_index])
        if (number_index + 1) % 3 == 0:
            damage_total_string_list.insert(0, " ")
    damage_total_string = ""
    for char in damage_total_string_list:
        damage_total_string += char

    plt.title("DnD simulation results - " + name + ": " + str(damage_total_string))
    plt.legend()
    plt.xlabel("Enemy AC")
    plt.ylabel("Accuracy/precision as %, damage as absolute")
    plt.axhline(y=highest_accuracy, color="blue", linestyle="dashed")
    plt.axhline(y=lowest_accuracy, color="blue", linestyle="dashed")
    settings_formatted = str(settings).replace("{", "")
    settings_formatted = settings_formatted.replace("}", "")
    settings_formatted = settings_formatted.replace("'", "")
    settings_formatted = settings_formatted.split(", ")
    settings_formatted.pop(1)
    settings_formatted.pop(1)
    settings_formatted_line1 = str(settings_formatted[:4])
    settings_formatted_line2 = str(settings_formatted[4:])
    settings_formatted = settings_formatted_line1 + "\n" + settings_formatted_line2
    settings_formatted = settings_formatted.replace("[", "")
    settings_formatted = settings_formatted.replace("]", "")
    settings_formatted = settings_formatted.replace("'", "")
    plt.ylim(0, 100)
    plt.xticks([x for x in range(settings["enemy_ac_lower"], settings["enemy_ac_higher"] + 1)])
    plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    plt.text(settings["enemy_ac_lower"] - 2.25, 111.25, settings_formatted,
             verticalalignment="center")
    plt.show()


def simulate(amount_of_attacks, enemy_ac_lower, enemy_ac_higher, attack_bonus, damage_dice, damage_bonus, re_rolls=None,
             disadvantage=False, advantage=False, crit_floor=20):
    stats = {}
    min_damage = 0
    max_damage = 0
    damage_total = 0

    for enemy_ac in range(enemy_ac_lower, enemy_ac_higher + 1):
        amount_of_hits = 0
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
                damage_rolls.append(0)

        damage_total += sum(damage_rolls)

        accuracy = to_percentage(amount_of_hits, amount_of_attacks)
        precision = to_percentage(amount_of_crits, amount_of_hits)
        mean_damage = 0
        if not (sum(damage_rolls) == 0 or len(damage_rolls) == 0):
            mean_damage = sum(damage_rolls) // len(damage_rolls)
        if min_damage == 0:
            min_damage = min([roll for roll in damage_rolls if roll != 0])
        else:
            min_damage = min(min([roll for roll in damage_rolls if roll != 0]), min_damage)
        max_damage = max(max(damage_rolls), max_damage)

        data = {"accuracy": accuracy, "precision": precision, "mean_damage": mean_damage}
        stats[str(enemy_ac)] = data

    return stats, min_damage, max_damage, damage_total


def to_percentage(frequency, max_frequency):
    decimal = frequency / max_frequency
    decimal *= 100
    percentage = int(round(decimal))
    return percentage


def roll_dice(sides, amount=1, re_rolls=None):
    resulting_dice = []
    for i in range(amount):
        resulting_dice.append(random.randint(1, sides))

    if re_rolls:
        for rolled_die_index in range(len(resulting_dice)):
            if resulting_dice[rolled_die_index] in re_rolls:
                resulting_dice[rolled_die_index] = random.randint(1, sides)
                pass

    return resulting_dice


def roll_to_hit(enemy_ac, attack_bonus, disadvantage=False, advantage=False, crit_floor=20):
    initial_attack_roll = roll_dice(20, 1)
    if disadvantage == advantage:
        if initial_attack_roll[0] >= crit_floor:
            return True, True, initial_attack_roll[0], attack_bonus
        elif initial_attack_roll[0] == 1:
            return False, False, initial_attack_roll[0], attack_bonus
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
            elif lowest_roll == 1:
                return False, False, lowest_roll, attack_bonus
            elif lowest_roll + attack_bonus > enemy_ac:
                return True, False, lowest_roll, attack_bonus
            else:
                return False, False, lowest_roll, attack_bonus
        else:
            highest_roll = max(initial_attack_roll[0], second_attack_roll[0])
            if highest_roll >= crit_floor:
                return True, True, highest_roll, attack_bonus
            elif highest_roll == 1:
                return False, False, highest_roll, attack_bonus
            elif highest_roll + attack_bonus > enemy_ac:
                return True, False, highest_roll, attack_bonus
            else:
                return False, False, highest_roll, attack_bonus


def roll_damage(dice, damage_bonus, dice_multiplier=1, re_rolls=None):
    resulting_dice = []
    for die, amount in dice.items():
        resulting_dice += roll_dice(int(die.replace("d", "")), amount * dice_multiplier, re_rolls)

    return sum(resulting_dice) + damage_bonus, resulting_dice, damage_bonus


if __name__ == "__main__":
    main()
