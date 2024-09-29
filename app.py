from flask import Flask, request, jsonify, render_template, send_from_directory
import re
from word2number import w2n
import spacy,os
import inflect, logging
from functions.spending import log_spending, clear_spending_logs, show_spending_logs,spending_graph,purchase_graph
from functions.wishlist import display_wishlist, wishlist
from functions.saving import saving_advice
from functions.Decisiontree import decisiontree
app = Flask(__name__)
p = inflect.engine()
nlp = spacy.load('en_core_web_sm')
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename)


#---------------------------------------------
def convert_currency(amount, currency):
    print(f"convert currrency func called line 20")
    if currency == '$':
        print(f"usd to bhd func called line 31")
        return usd_to_bhd(amount)
    
    elif currency == '£':
        print(f"Eur to bhd func called line 35")
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
    print(f"Reset budget func called  {budget} line 42")
    budget = 0
    return "Your budget has been reset to zero"
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
    old_image = ['static/images/week_spending.png','static/images/purchases.png']
    for image in old_image:
        if os.path.exists(image):
            os.remove(image)
            print(f"Old graph {image} deleted.")
    return render_template('display.html', budget=budget)

#--------------------------------------------------------------------------------------
def parse_message(message):
    doc = nlp(message)
    tokenisedword = []
    transformed_text = []
    message_tag = []
    Num_count = 0
    Num_list = []
    currency = ""  
    description=""
    for token in doc:
        
        tokenisedword.append(token.lemma_)
        message_tag.append(token.pos_)
        
        # Check for numeric tokens
        if token.pos_ == 'NUM':
            Num_count += 1
            Num_list.append(token.lemma_)
            print(f"Num_list contents before loop: {Num_list}")

            # Convert word numbers to digits
            for num in Num_list:
                if isinstance(num, str):
                    if num.isdigit():
                        print(f"'{num}' is a numeric string, type: {type(int(num))}")
                    else:
                        converted_num = w2n.word_to_num(num)
                        print(f"'{num}' is a word, converted to {converted_num}, type: {type(converted_num)}")
                        Num_list[Num_list.index(num)] = converted_num

        # Detect currency symbols in the sentence
        if token.text in ['$','£']:
            currency = token.text
            print(f"Currency detected: {currency}")

    # If there are more than two numbers, multiply the first two numbers (quantity * price)
    if len(Num_list) >= 2:
        Num_list = [float(x) for x in Num_list]  # Convert to float for multiplication
        quantity = Num_list[0]
        price = Num_list[1]
        total_amount = quantity * price  # Multiply the first two numbers
        print(f"Multiplication of {quantity} and {price} is: {total_amount}")
        amount_str = str(total_amount)  # Convert result to string for handle_budget_modification
    else:
        print("Not enough numbers in the list to multiply")
        amount_str = Num_list[0] if Num_list else '0'  # Fallback in case only one or no numbers
    
    for token in doc:
        if token.pos_ =='NOUN':  
            description=token.text
            
    # Remove adpositions and unnecessary parts of speech
    for token in doc:
        if token.pos_ in ['ADP', 'PART']:  # Skip adpositions like "for" or particles like "to"
            continue
        
        if token.pos_ == 'VERB':
            verb_count = 1  # Only consider the first verb
        transformed_text.append(token.lemma_)

    print(f"Transformed text: {' '.join(transformed_text)}")
    print(f"Numbers extracted: {Num_list}")
    print(f"tokenised and lemmatized message: {tokenisedword}")
    print(f"message tag: {message_tag}")
    print(f"message item: {description}")
    return ' '.join(transformed_text), amount_str, currency ,description # Return the transformed text, the calculated amount_str, and the currency



#--------------------------------------------------------------------------------------
def handle_budget_modification(transformed_text_str, amount_str, currency,description):
    global budget
    combined_pattern = re.compile(
        r'(add|remove|buy|purchase)\s*(.*?)\s*([$£]?)', 
        re.IGNORECASE
    )
    match = combined_pattern.search(transformed_text_str)

    if match:
        action = match.group(1)

        if not amount_str:
            return {'response': 'You didn\'t provide any amount. Please specify the amount.'}

        try:
            amount = float(amount_str)
        except ValueError:
            return {'response': 'Invalid amount value provided. Please enter a valid number.'}

        if currency and currency not in ['$','£']:
            return {'response': 'Invalid currency. Please use "$" or "£".'}

        # Apply currency conversion based on the currency provided
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
    image_url = None
    image_url1 = None
    response = ""
    message = request.form.get('message')
    
    if not message:
        return jsonify({'error': 'No message provided.'})

    transformed_text_str, amount_str, currency, description = parse_message(message)

    # Handling different phrases in the message
    if "need" in transformed_text_str.lower():
        parts = transformed_text_str.split("need")
        if len(parts) > 1:
            user_item = parts[1].strip()  # Get the first word after "need"
            response = decisiontree(user_item, budget)  # Pass user_item to decisiontree
    elif "wishlist" in transformed_text_str.lower():
        response = display_wishlist()
    elif "want" in transformed_text_str.lower():
        response = wishlist(transformed_text_str)
    elif "clear" in transformed_text_str.lower() or "delete" in transformed_text_str.lower():
        response = clear_spending_logs()
    elif "my spending" in transformed_text_str.lower() or "record" in transformed_text_str.lower():
        response = show_spending_logs()
    elif "reset" in transformed_text_str.lower():
        response = reset()
    elif "weekly spending" in transformed_text_str.lower():
        spending_graph()
        image_url = '/static/images/week_spending.png'
        response = 'Here is your weekly spending graph.'
    elif "advice" in transformed_text_str.lower():
        response = saving_advice()
    elif "report" in transformed_text_str.lower():
        purchase_graph()
        image_url1 = '/static/images/purchases.png'
        response = 'Here is your weekly purchases graph.'
    elif "budget" in transformed_text_str.lower():
        response = f"Your current budget is {budget}." if budget != 0 else "Your budget is zero."
    if not response:
        response = handle_budget_modification(transformed_text_str.replace(amount_str, ''), amount_str, currency, description)


    response = response if response else "Sorry, I don't understand."

    if isinstance(response, dict):
        return jsonify(response)

    return jsonify({
        'updated_budget': budget,
        'response': response,
        'image_url': image_url,
        'image_url1': image_url1
    })




if __name__ == '__main__':
    app.run(debug=True)