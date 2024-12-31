from functions.utils import convert_currency
import re
from functions.spending import log_spending
from functions.utils import nlp
budget = 250.0 



def handle_budget_modification(action, amount_str, currency, description):
    print("handle_budget_modification function called")
    global budget  # Declare as global to modify the budget
    print(f"action: {action} amount_str: {amount_str} currency: {currency} description: {description}")
    
    if not amount_str or amount_str == "0":
        print("No amount has been provided or amount is zero.")
        return {'response': 'You didn\'t provide any amount. Please specify the amount.'}

    try:
        amount = float(amount_str)
    except ValueError:
        return {'response': 'Invalid amount value provided. Please enter a valid number.'}

    if currency and currency not in ['$','€']:
        return {'response': 'Invalid currency. Please use "$" or "€".'}
    # Apply currency conversion based on the currency provided
    amount_bhd = convert_currency(amount, currency)
    print("Amount in BHD:", amount_bhd)

    print(f"Action: {action},print:{(len(action))}")
    if 'add' in action:
        budget += amount_bhd
        return {'response':f"Added {amount_bhd:.2f} BHD to your budget.",
                    'updated_budget': budget 
                    }
    elif any(action_word in ['buy', 'purchase', 'remove'] for action_word in action):
        budget -= amount_bhd
        print("Action buy, purchase, or remove has been called")
        
        description = description[0].strip().capitalize()
        log_spending(description, amount_bhd)
        
        with open('txt/wishlist.txt', 'r') as file:
            lines = file.readlines()
        
        updated_lines = []
        max_similarity = 0
        item_to_remove = None
        match=False
        for line in lines:
            item_details = line.lower().strip().split(' - ')
            if len(item_details) == 2:
                item = item_details[1].strip()
                # Calculate the similarity between the item and the description
                description_processed = nlp(description.lower())
                item_processed = nlp(item.lower())
                
                similarity_score = description_processed.similarity(item_processed)
                print(f"{item_processed} and {description_processed} similarity {similarity_score}")
                
                # Check if this similarity is the largest we've seen
                if similarity_score > max_similarity:
                    max_similarity = similarity_score
                    item_to_remove = line  

            updated_lines.append(line)  

        # If an item to remove was found and its similarity is above the threshold
        if item_to_remove and max_similarity >= 0.58:
            match=True
            print(f"Item found in the wishlist with the highest similarity and will be removed: {item_to_remove.strip()}")
            updated_lines.remove(item_to_remove)  # Remove the item from updated_lines
        
        with open('txt/wishlist.txt', 'w') as file:
            file.writelines(updated_lines)
        
        response = f"Recorded expense: {description} - {amount_bhd:.2f} BHD. Your updated budget is {budget:.2f} BHD."
        if match:
            print(f"Item to remove: {item_to_remove.strip()}")
            print(type(item_to_remove))
            item_to_remove=list(item_to_remove.split(' - '))
            print(f"Item to remove: {item_to_remove}")
            print(type(item_to_remove))
            response += f" The {item_to_remove[1]} has been removed from the wishlist."
        
        return {
            'response': response,
            'updated_budget': budget 
        }

     
    else:
        response = "Action not recognized. Please use  'buy', 'purchase'."
        return { 'response' :response,
                 'updated_budget': budget
        },budget


