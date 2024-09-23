from flask import request


def decisiontree(user_item,budget):
    print(budget)
    # Convert user input to lowercase and strip extra spaces
    user_item = user_item.strip().lower()

    # Open both files within the same 'with' block to ensure proper closing
    with open('txt/spending_log.txt', 'r') as log_file, open('txt/decision.txt', 'r') as decision_file:
        decisions = decision_file.readlines()

    # Create a dictionary for decisions
    decision_dict = {}
    for decision in decisions:
        parts = decision.split('-')
        if len(parts) >= 2:
            item = parts[0].strip().lower()  # Ensure items are lowercased for case-insensitive comparison
            decision_type = parts[1].strip()
            decision_dict[item] = decision_type

    # Check if the user item is in the decision dictionary
    if user_item in decision_dict:
        if decision_dict[user_item]=="not important" and  budget<10 :
            
            return f"The {user_item.capitalize()} is not really necessary at the moment. You can save instead."
        elif decision_dict[user_item]=="important":
            print("hello")
            return f"The {user_item.capitalize()} is {decision_dict[user_item]}  you can get it "
        else:
            return f"The {user_item.capitalize()} is not really importent but  you can afford it right now"
            
    else:
        
        return f"No decision found for {user_item.capitalize()}." + categorize_item()


