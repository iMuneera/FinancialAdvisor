from collections import defaultdict
from datetime import datetime, timedelta

def saving_advice():
    print("Saving advice function has been called")
    
    # Reading the spending log
    with open('spending_log.txt', 'r') as file:
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
    items_price = []
    total_savings = 0.0
    
    # Analyzing purchases by item and date
    for item, dates in item_dates.items():
        dates.sort()
        print(f"\nProcessing item: {item} with dates: {dates}")

        first_date = dates[0]  # Use the earliest date as the reference
        same_week_dates = []

        for date in dates:
            # Print each date for debugging
            print(f"Checking date: {date}")

            # Compare the week of the current date to the first date's week
            if first_date.isocalendar()[1] == date.isocalendar()[1]:
                same_week_dates.append(date)

        print(f"Item: {item}, Same week dates: {same_week_dates}")

        # give advice if more than 3 purchases of the same item  in the same week
        if len(same_week_dates) >= 3:
            advice = (
                f"<br>This week, you've bought <b>{item}</b> {len(same_week_dates)} times and spent a total of "
                f"<span style='color: red;'>{total_spent[item]:.2f} BHD</span>.<br>"
            )
            items_list.append(item)
            items_price.append(f"{total_spent[item]:.2f} BHD")
            total_savings += total_spent[item]
            advice_list.append(advice)
        else:
            print(f"{item} was not purchased more than 3 times this week.")

    # Create the total savings advice
    if items_list and items_price:
        saving_total = (
            f"Consider cutting back on your {', '.join(items_list)} purchases to save a total of "
            f"<span style='color: red;'>{total_savings:.2f} BHD</span>."
        )
    else:
        saving_total = "No items found that were purchased more than 3 times in the same week."

    return "<br>".join(advice_list) + "<br><br>" + saving_total