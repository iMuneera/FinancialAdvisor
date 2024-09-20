from flask import Flask, request, jsonify, render_template, send_from_directory
import re
import spacy,os
import inflect, logging
from spending import log_spending, clear_spending_logs, show_spending_logs,spending_graph
from wishlist import display_wishlist, wishlist
from saving import saving_advice
from Decisiontree import decisiontree
app = Flask(__name__)
p = inflect.engine()
nlp = spacy.load('en_core_web_sm')
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename)


#---------------------------------------------
def convert_currency(amount, currency):
    if currency == '$':
        return usd_to_bhd(amount)
    elif currency == '£':
        return EUR_to_bhd(amount)
    else:
        return amount
#---------------------------------------------    
def usd_to_bhd(usd_amount):
    conversion_rate = 0.38  
    return usd_amount * conversion_rate

def EUR_to_bhd(EUR_amount):
    conversion_rate = 0.42
    return EUR_amount * conversion_rate
#---------------------------------------------    
def reset():
    global budget
    budget = 0
    return "Your budget has been reset to zero", budget
#---------------------------------------------



#--------------------------------------------------------------------
budget = 250
@app.route('/budget', methods=['POST'])
def update_budget():
    try:
        global budget  
        data = request.form['amount']
        budget += float(data)  
        return jsonify({'updated_budget': budget})
    except ValueError:
        return jsonify({'error': 'Invalid input. Please enter valid numbers.'})
#--------------------------------------------------------------------------------------

@app.route('/')
def display():
   
    return render_template('display.html', budget=budget)

#--------------------------------------------------------------------------------------
def parse_message(message):
    doc = nlp(message)
    transformed_text = []
    for token in doc:
        if token.pos_ == 'VERB' and token.tag_ not in ['VB', 'VBG', 'VBP', 'VBZ']:
            transformed_text.append(token.lemma_)
        elif token.pos_ == 'NOUN' and token.tag_ == 'NNS': 
            singular_form = p.singular_noun(token.text)
            if singular_form:
                transformed_text.append(singular_form)
            else:
                transformed_text.append(token.text)
        else:
            transformed_text.append(token.text)
    
    return ' '.join(transformed_text)
#--------------------------------------------------------------------------------------
def handle_budget_modification(transformed_text_str):
    global budget
    combined_pattern = re.compile(
        r'(add|remove|buy|purchase)\s*(.*?)\s*(\d+\.?\d*)\s*([$£]?)|(\d+\.?\d*)\s*([$£]?)\s*(.*?)(?:\s*(add|remove|buy|purchase))?', 
        re.IGNORECASE
    )
    match = combined_pattern.search(transformed_text_str)
    
    if match:
        action = match.group(1)
        description = match.group(2).strip().replace("for", "").strip()
        amount_str = match.group(3)
        currency = match.group(4)

        if not amount_str:
            return {'response': 'You didn\'t provide any amount. Please specify the amount.'}
        
        try:
            amount = float(amount_str)
        except ValueError:
            return {'response': 'Invalid amount value provided. Please enter a valid number.'}

        if currency and currency not in ['$','£']:
            return {'response': 'Invalid currency. Please use "$" or "£".'}

        amount_bhd = convert_currency(amount, currency)
        
        if action.lower() == "add":
            budget += amount_bhd
            return f"Added {amount_bhd:.2f} BHD to your budget."
        elif action.lower() in ['buy', 'purchase', 'remove']:
            budget -= amount_bhd
            log_spending(description, amount_bhd)
            return f"Recorded expense: {description} - {amount_bhd:.2f} BHD. Your updated budget is {budget:.2f} BHD."
        else:
            return "Action not recognized. Please use 'add', 'buy', 'purchase', or 'remove'."
        
#---------------------------------------------------------------------------------------------------------        




@app.route('/chat', methods=['POST'])
def chat():
    image_url=None
    response = ""
    message = request.form.get('message')
    if not message:
        return jsonify({'error': 'No message provided.'})
    
    transformed_text_str = parse_message(message)
    if "need" in transformed_text_str.lower():
        parts = transformed_text_str.split("need")
        if len(parts) > 1:
            user_item = parts[1].strip()  # Get the first word after "check"
            response = decisiontree(user_item)  # Pass user_item to decisiontree
    if "wishlist" in transformed_text_str.lower():
        response = display_wishlist()
    elif "want" in transformed_text_str.lower():
        response = wishlist(transformed_text_str)
    elif "clear" in transformed_text_str.lower() or "delete" in transformed_text_str.lower():
        response = clear_spending_logs()
    if "my spending" in transformed_text_str.lower() or "record" in transformed_text_str.lower():
        response = show_spending_logs()
    elif "reset" in transformed_text_str.lower():
        response = reset()
    if "weekly spending" in transformed_text_str.lower():
        spending_graph()  # This will save the image
        image_url = '/static/images/week_spending.png'
        response = 'Here is your weekly spending graph.'
    elif "advice" in transformed_text_str.lower():
        response = saving_advice()
    elif "budget" in transformed_text_str.lower():
        response = budget
    if not response:
        response = handle_budget_modification(transformed_text_str)
    
    # If response is a dictionary (like budget modification), return it as JSON
    if isinstance(response, dict):
        return jsonify(response)
    
    return jsonify({
        'updated_budget': budget,
        'response': response,
        'image_url': image_url
    })




if __name__ == '__main__':
    app.run(debug=True)

