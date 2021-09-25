import random
import matplotlib.pyplot as plt


def main():
    settings = {"amount_of_attacks": 1000000,
                "enemy_ac_lower": 11,
                "enemy_ac_higher": 21,
                "attack_bonus": 7,
                "damage_dice": {"d8": 1},
                "damage_bonus": 1,
                "re_rolls": []}

    stats, min_damage, max_damage = simulate(settings["amount_of_attacks"],
                                             settings["enemy_ac_lower"], settings["enemy_ac_higher"],
                                             settings["attack_bonus"], settings["damage_dice"],
                                             settings["damage_bonus"], settings["re_rolls"])

    plt.axhline(y=min_damage, color="darkgreen", linestyle='dashed')
    plt.text(settings["enemy_ac_lower"] - 0.75, -9.5, "Min damage: " + str(min_damage),
             verticalalignment="center")
    plt.axhline(y=max_damage, color="darkgreen", linestyle='dashed')
    plt.text(settings["enemy_ac_lower"] - 0.75, max_damage + 1.5, "Max damage: " + str(max_damage),
             verticalalignment="center")

    highest_precision = 0
    highest_accuracy = 0
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

        if data_key == "mean_damage":
            plt.bar(x_axis, y_axis, color="green", label="Mean damage")
        elif data_key == "accuracy":
            plt.plot(x_axis, y_axis, color="blue", label="Accuracy", linestyle='solid')
        elif data_key == "precision":
            plt.plot(x_axis, y_axis, color="red", label="Precision on hit", linestyle='solid')

    plt.title("DnD simulation results")
    plt.legend()
    plt.xlabel("Enemy AC")
    plt.ylabel("Accuracy/precision as %, damage as absolute")
    settings_formatted = str(settings).replace("{", "")
    settings_formatted = settings_formatted.replace("}", "")
    settings_formatted = settings_formatted.replace("'", "")
    settings_formatted = settings_formatted.split(", ")
    settings_formatted_line1 = str(settings_formatted[:3])
    settings_formatted_line2 = str(settings_formatted[3:])
    settings_formatted = settings_formatted_line1 + "\n" + settings_formatted_line2
    settings_formatted = settings_formatted.replace("[", "")
    settings_formatted = settings_formatted.replace("]", "")
    settings_formatted = settings_formatted.replace("'", "")

    plt.text(settings["enemy_ac_lower"] - 2.25, max(highest_precision, highest_accuracy) + 16, settings_formatted,
             verticalalignment="center")
    plt.show()


def simulate(amount_of_attacks, enemy_ac_lower, enemy_ac_higher, attack_bonus, damage_dice, damage_bonus, re_rolls=None,
             disadvantage=False, advantage=False, crit_floor=20):
    stats = {}
    min_damage = 0
    max_damage = 0

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

        accuracy = to_percentage(amount_of_hits, amount_of_attacks, 0)
        precision = to_percentage(amount_of_crits, amount_of_hits, 0)
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

    return stats, min_damage, max_damage


def modify_string(original_string, index, value):
    new_string = list(original_string)
    for i in range(0, len(new_string)):
        if i == index:
            new_string[i] = value

    resulting_string = "".join(new_string)
    return resulting_string


def precise_rounding(digit_whole, digit_decimals=0, precision=0):
    # Turn the input into a float, and then into a string
    digit_str = str(digit_whole) + "." + str(digit_decimals)

    # Find the index location of the comma
    comma_index = digit_str.index(".")
    # Determine the index location of the value which will be rounded up/down
    target_index = comma_index + precision

    # Some quick analytical results
    if target_index > len(digit_str):
        return digit_whole, digit_decimals
    elif target_index < 0:
        return 0, 0

    else:
        # If we're 'moving backwards', move back one more to account for the comma
        if precision < 1:
            target_index -= 1

        target_int = int(digit_str[target_index])

        # Figure out the value of the number which is next(behind) of the target index
        try:
            trailing_int = int(digit_str[target_index + 1])
        # If we get a value error, it's because of the comma, in which case we instead look one more index further
        except ValueError:
            trailing_int = int(digit_str[target_index + 2])

        # If the trailing int is above 5, increment the target index by 1
        if trailing_int > 5:
            new_target_int = target_int + 1
            digit_str = modify_string(digit_str, target_index, str(new_target_int))
        # If the trailing int is exactly 5, increment the target index by 1 only if that makes an even number
        elif trailing_int == 5:
            if (target_int + 1) % 2 == 0:
                new_target_int = target_int + 1
                digit_str = modify_string(digit_str, target_index, str(new_target_int))

        # This if statement accounts for the fence-post problem in the for loop beneath
        if len(digit_str) - 1 == target_index + 1:
            if not digit_str[-1] == ".":
                digit_str = modify_string(digit_str, len(digit_str) - 1, "0")
        else:
            # Set all numbers behind the target index to 0
            for index in range(target_index + 1, len(digit_str)):
                if not digit_str[index] == ".":
                    digit_str = modify_string(digit_str, index, "0")

        # Find the start of the trailing zeroes
        start_trailing_zeroes = comma_index + 1
        for index in range(len(digit_str) - 1, 0, -1):
            if digit_str[index] != "0":
                start_trailing_zeroes = index + 1
                break

        # Remove trailing zeroes
        digit_str = digit_str[:start_trailing_zeroes]
        if digit_str[-1] == ".":
            digit_str = digit_str[:comma_index]

        # Return the resulting whole and decimal numbers
        digit_str_split = digit_str.split(".")
        resulting_digit_whole = int(digit_str_split[0])
        if len(digit_str_split) < 2:
            resulting_digit_decimals = 0
        else:
            resulting_digit_decimals = int(digit_str_split[1])
        return resulting_digit_whole, resulting_digit_decimals


def to_percentage(frequency, max_frequency, precision):
    decimal = frequency / max_frequency
    decimal *= 100
    whole = int(str(decimal).split(".")[0])
    decimal = int(str(decimal).split(".")[1])
    percentage = precise_rounding(whole, decimal, precision)[0]
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
