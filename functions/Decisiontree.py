from flask import request
from datetime import datetime, timedelta

def decisiontree(description,budget,flag,remining,flag_explain):
    # Convert user input to lowercase and strip extra spaces
    print(f"Decision tree function called")
    print(f"Description: {description}")
    response = "No decision made."
    if len(description) == 1:
        description = description[0].lower().strip()
    today = datetime.today()

# Create a datetime object for the 26th of the same month
    target_date = datetime(today.year, today.month, 26)

# Calculate the difference in days
    if target_date.weekday() == 4:  # Friday (4th index)
        target_date -= timedelta(days=1)  # Move to Thursday
    elif target_date.weekday() == 5:  # Saturday (5th index)
        target_date -= timedelta(days=2)  # Move to Thursday

    days_left = (target_date - today).days
    print(f"days_left is {days_left}")

# Print the result
    if days_left > 0:
        print(f"The adjusted date is {target_date.strftime('%A, %B %d')} ({days_left} day(s) left).")
    else:
        print(f"The adjusted date {target_date.strftime('%A, %B %d')} has already passed.")
    
    
    description = description

    # Open both files within the same 'with' block to ensure proper closing
    with open('txt/spending_log.txt', 'r') as log_file, open('txt/decision.txt', 'r') as decision_file:
        decisions = decision_file.readlines()

    # Create a dictionary for decisions
    decision_dict = {}
    for decision in decisions:
        parts = decision.split('-')
        if len(parts) >= 2:
            item = parts[0].strip().lower() 
            decision_type = parts[1].strip()
            decision_dict[item] = decision_type

    # Check if the user item is in the decision dictionary
    remining=budget/days_left if days_left>0 else budget 
    print(remining)
    if isinstance(description, list):
        description = ' '.join(description)
    if description in decision_dict:
        if days_left == 0:
            response = f"today is the last day of the month you can buy it tomorrow."
        if decision_dict[description] == "not important" and remining < 1 and budget > 0:
            flag = True
            print(f"remining is less than 1 {remining} and flag is {flag} the decision is {decision_dict[description]}")
            response = f"The {description.capitalize()} is {decision_dict[description]}. You don't need to pay for it now."
        elif decision_dict[description] == "important":
            response = f"The {description.capitalize()} is {decision_dict[description]}. You have to pay for it now."
        elif decision_dict[description] == "not important" and days_left != 0 and budget > 0:
            flag_explain = True
            response = f"The {description.capitalize()} is not really important but you can afford it right now."
        elif budget < 0 and decision_dict[description] == "not important":
            response = f"Your budget is {budget}. You can't afford it, maybe after {days_left} days you can buy it."
    else:
        response= f"No decision found for {description.capitalize()}." 
        
    return {
                'response': response,
                "decision": decision_dict.get(description, "No decision found"),
                "remining": remining,
                "flag": flag,
                "flag_explain": flag_explain,
                "days_left": days_left
            }