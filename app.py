from flask import Flask, request, jsonify, render_template, send_from_directory
import spacy,os
import inflect
from textblob import TextBlob
from functions.spending import  clear_spending_logs, show_spending_logs,spending_graph,purchase_graph
from functions.wishlist import display_wishlist, wishlist
from functions.saving import saving_advice
from functions.Decisiontree import decisiontree
from functions.subscription import display_subscription,handle_subscription,subscription_message
from functions.utils import parse_message 
from functions.budget import budget,handle_budget_modification
app = Flask(__name__)
p = inflect.engine()
nlp = spacy.load('en_core_web_lg')

@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename)
#---------------------------------------------
# Update the budget    
@app.route('/budget', methods=['POST'])
def update_budget():
    global budget  
    try:
        data = request.form['amount']
        budget += float(data)  
        return jsonify({'updated_budget': budget})
    except ValueError:
        return jsonify({'error': 'Invalid input. Please enter valid numbers.'})
#--------------------------------------------------------------------------------------
@app.route('/')
def display():
    global budget,flag,remining,flag_explain
    old_image = ['static/images/week_spending.png','static/images/purchases.png']
    flag = False
    remining = ""
    flag_explain=False
    for image in old_image:
        if os.path.exists(image):
            os.remove(image)
            print(f"Old graph {image} deleted.")
    return render_template('display.html', budget=budget)
#---------------------------------------------------------------------------------------------------------        
flag = False
remining = ""
days_left = 0
flag_explain=False
# Chat route
@app.route('/chat', methods=['POST'])
def chat():

    global budget, flag, remining, days_left, flag_explain
    image_url = None
    image_url_purchases = None
    response = ""
    # Get the message from the JS
    message_unchecked = request.form.get('message')
    print(f"The unchecked message is {message_unchecked}")
    # Correct the spelling of the message
    blob = TextBlob(message_unchecked)
    message = str(blob.correct())
    print(f"The corrected message is {message}")

    if not message:
        return jsonify({'error': 'No message provided.'})
    # Parse the message using spaCy
    doc = nlp(message)
    for token in doc:
        # Subscription handling
        if token.dep_ == "ROOT" and token.lemma_.lower() == 'subscribe':
            service_name, start_date, renewal_date, duration, amount = subscription_message(doc)
            response, updated_budget = handle_subscription(service_name, start_date, renewal_date, duration, amount)
            return jsonify({
                "response": response,
                "updated_budget": f"{updated_budget:.2f}"  # Format budget as a string for JSON
            })

        # Budget reset
        if token.head.pos_ == 'AUX' and token.lemma_.lower() == 'budget':
            print("Budget reset")
            for num_token in doc:
                if num_token.pos_ == 'NUM':
                    budget = float(num_token.text)
            return {
                'response': f"Your budget has been reset to {budget:.2f} BHD.",
                'updated_budget': budget
            }

    # Check for clear/delete action
    if any(token.text.lower() in ["clear", "delete"] for token in doc):
        response = clear_spending_logs()

    # Parsing non-subscription-related actions
    else:
        # Handling "why" questions first
        if any((token.pos_ == "advmod" or token.pos_ == "SCONJ") and (token.text.lower() == "why") for token in doc):
            if flag:
                response = (
                    f"You only have {budget:.2f} left. You can only spend {remining:.2f} each day for {days_left} days "
                    "to ensure you have enough money for the rest of the month."
                )
            elif flag_explain:
                response = (
                    f"You have {budget:.2f}, and there is only {days_left} day left. You can manage it to the end of the month."
                )
            else:
                response = "Could you please clarify what you mean by 'why'? I'm not entirely sure what you are asking."
            return {"response": response}  # Ensure an early return to prevent further checks

        # Parse the message for other actions
     
        amount_str, currency, description, action = parse_message(doc)
        if action and any(act in action for act in ['buy', 'purchase', 'remove', 'add']) and (amount_str or description):
            response = handle_budget_modification(action, amount_str, currency, description) 
            if 'updated_budget' in response:
                budget = response['updated_budget']
                response = response['response']
            else:
               response= 'No amount has been provided or amount is zero.'
            
            print(f"Budget updated to {budget:.2f}")
            print(f"Action: {action}, Amount: {amount_str}, Currency: {currency}, Description: {description}")
            return{'response':response, 'updated_budget': f"{budget:.2f}"}
        # Decision tree logic for "need"
        if action and "need" in action:
            description = parse_message(doc)[2]
            answer = decisiontree(description, budget, flag, remining, flag_explain)
            flag = answer["flag"]
            flag_explain = answer["flag_explain"]
            remining = answer["remining"]
            days_left = answer["days_left"]
            print(f"Need called: flag is {flag} and remining is {remining}")
            response = answer['response']

        # Wishlist handling
        elif description and "wishlist" in description:
            response = display_wishlist()

        elif any(token.dep_ == "ROOT" and token.text == "want" for token in doc):
            response = wishlist(description)
        if action and description and any(action_word in action for action_word in ["show", "display"]) and any(keyword in description for keyword in ["spending", "graph", "purchases"]):
            if "spending" in description:
                if "graph" in description:
                    spending_graph()
                    image_url = '/static/images/week_spending.png'
                    response = 'Here is your spending graph.'
                else:
                    response = show_spending_logs()
            elif "graph" in description:
                if "purchases" in description:
                    response = purchase_graph()
                    image_url_purchases = '/static/images/purchases.png'
                    response = 'Here is your purchases graph.'
                else:
                    response = "Do you want to see your spending or purchases graph?"
            else:
                response = "What do you want to display?"
                # Saving advice handling
        if action and description and any(word in action for word in ["give", "need"]) and any(keyword in description for keyword in ["saving", "advice"]):
            response = saving_advice()
                # Show subscription
        elif any(token.dep_ == "ROOT" and token.lemma_.lower() == 'show' and 
                    any(child.lemma_.lower() == 'subscription' for child in token.children) for token in doc):
            response = display_subscription()
                
    # Default response if no matches
    if not response:
        response = "Sorry, I don't understand."

    return jsonify({
        'updated_budget': f"{budget:.2f}",
        'response': response,
        'image_url': image_url,
        'image_url_purchases': image_url_purchases,
        'flag': flag,
        'remining': remining,
        "flag_explain": flag_explain
    })

if __name__ == '__main__':
    app.run(debug=True)