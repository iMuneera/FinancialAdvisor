def decisiontree(user_item):
    with open('txt\spending_log.txt', 'r') as log_file, open('txt\decision.txt', 'r') as decision_file:
        decisions = decision_file.readlines()

    # Create a dictionary for decisions
    decision_dict = {}
    for decision in decisions:
        parts = decision.split('-')
        if len(parts) >= 2:
            item = parts[0].strip()
            decision_type = parts[1].strip()
            decision_dict[item] = decision_type

    # Check if the user item is in the decision dictionary
    if user_item in decision_dict:
        return f"{user_item} is {decision_dict[user_item]}"
    else:
        return f"No decision found for {user_item}"
