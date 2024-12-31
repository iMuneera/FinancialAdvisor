from collections import defaultdict
from datetime import datetime

def saving_advice():
    print("Saving advice function has been called")
    
    # Reading the spending log
    with open('txt/spending_log.txt', 'r') as file:
        spending_log = file.readlines()

    item_dates = defaultdict(list)
    total_spent = defaultdict(float)
    
    # Parse the spending log
    for line in spending_log:
        parts = line.strip().split(' - ')
        if len(parts) == 3:
            date_str, description, amount_bhd = parts
            date = datetime.strptime(date_str, '%Y-%m-%d %I:%M %p')
            amount_bhd = float(amount_bhd.split()[0])

            # Append date to the item description and add the amount to the total spent
            item_dates[description].append(date)
            total_spent[description] += amount_bhd

    # Print to verify parsing
    print(f"Item dates: {item_dates}")
    print(f"Item total spent: {total_spent}")

    advice_list = []
    items_list = []
    total_savings = 0.0
    
    for item, dates in item_dates.items():
        dates.sort()
        print(f"\nProcessing item: {item} with dates: {dates}")

        first_date = dates[0] 
        same_week_dates = []

        for date in dates:
            print(f"Checking date: {date}")
            if first_date.isocalendar()[1] == date.isocalendar()[1]:
                same_week_dates.append(date)

        print(f"Item: {item}, Same week dates: {same_week_dates}")

        # Give advice if more than 3 purchases of the same item in the same week
        if len(same_week_dates) >= 3:
            advice = (
                f"<div style='margin-bottom: 10px;'>"
                f" You bought <strong> {item}</strong> <b>{len(same_week_dates)} times</b> and spent a total of "
                f"<span style='color: red;'>{total_spent[item]:.2f} BHD  </span>."
                f"</div>"
            )
            items_list.append(item)
            total_savings += total_spent[item]
            advice_list.append(advice)
        else:
            print(f"{item} was not purchased more than 3 times this week.")

    # Create the total savings advice
    if items_list:
        saving_total = (
            f"<div>Consider cutting back on your purchases of "
            f"<strong>{', '.join(items_list)}</strong> to save a total of "
            f"<span style='color: red;'>{total_savings:.2f} BHD</span> , weekly.</div>"
        )
    else:
        saving_total = "I didnt find any item that was purchased more than 3 times in the same week. so i don't have any advice for you."

    return "".join(advice_list) + saving_total
