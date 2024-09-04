from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import re,spacy,secrets
from datetime import datetime ,timedelta
from collections import defaultdict


app = Flask(__name__)
app.secret_key = secrets.token_hex(24)  
nlp = spacy.load('en_core_web_sm')

def usd_to_bhd(usd_amount):
    conversion_rate = 0.38  
    return usd_amount * conversion_rate

def EUR_to_bhd(EUR_amount):
    conversion_rate = 0.42
    return EUR_amount * conversion_rate


def log_spending(description, amount_bhd):
    date_str = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    with open("spending_log.txt", "a") as file:
        file.write(f"{date_str} - {description} - {amount_bhd:.2f} BHD\n")

@app.route('/')
def index():
    # Initialize budget in session if not set
    if 'budget' not in session:
        session['budget'] = 0.0
    return render_template('index.html', budget=session['budget'])

@app.route('/budget', methods=['POST'])
def budget():
    try:
        budget = float(request.form.get('budget'))
        session['budget'] = budget
        return redirect(url_for('display'))
    except ValueError:
        return jsonify({'error': 'Invalid input. Please enter valid numbers.'})

@app.route('/display')
def display():
    budget = session.get('budget', 0.0)
    return render_template('display.html', budget=budget)

def parse_message(message):

    doc = nlp(message)

    transformed_text = []
    for token in doc:
        if token.pos_ == 'VERB' and token.tag_ not in ['VB', 'VBG', 'VBP', 'VBZ']:
            transformed_text.append(token.lemma_)
        else:
            transformed_text.append(token.text)


    return ' '.join(transformed_text)





def clear_spending_logs():
    with open('spending_log.txt', 'w') as file:
        return "Spending logs have been cleared."

def show_spending_logs():
    try:
        with open('spending_log.txt', 'r') as file:
            spending_log = file.readlines()

        if not spending_log:
            return "No spending records found."
        table_rows = ''
        for line in spending_log:
            parts = line.strip().split(' - ')
            if len(parts) == 3:
                date, description, amount_bhd = parts
                amount_bhd = float(amount_bhd.split()[0])  # Extract numeric part and convert to float
                amount_class = get_amount_class(amount_bhd)
                table_rows += f"""
                <tr class='bg-white border-b even:bg-gray-100'>
                    <td class='px-6 py-4'>{date}</td>
                    <td class='px-6 py-4'>{description}</td>
                    <td class='px-6 py-4 {amount_class}'>{amount_bhd:.2f} BHD</td>
                </tr>
                """

        return f"""
        <body class='bg-gray-100 p-8'>
            <h2 class='text-2xl font-semibold mb-4'>Your Spending Log</h2>
            <div class='overflow-x-auto'>
                <table class='min-w-full bg-white border border-gray-200 rounded-lg shadow-md'>
                    <thead class='bg-gray-200 text-gray-600'>
                        <tr>
                            <th class='px-6 py-3 border-b border-gray-200'>Date</th>
                            <th class='px-6 py-3 border-b border-gray-200'>Description</th>
                            <th class='px-6 py-3 border-b border-gray-200'>Amount (BHD)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </body>
        """
    except FileNotFoundError:
        return "Spending log file not found."
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"

def get_amount_class(amount_bhd):
    if amount_bhd >= 100:
        return 'text-red-600'
    elif amount_bhd >= 10:
        return 'text-yellow-600'
    else:
        return 'text-gray-800'


def display_wishlist() :
    try:
        with open('wishlist.txt', 'r') as file:
            wishlist = file.readlines()

        if not wishlist:
            return "No spending records found."

        # Prepare HTML table with Tailwind CSS
        table_rows = ''
        for line in wishlist:
            parts = line.strip().split('=')
            if len(parts) == 2:
                date, description = parts
                table_rows += f"""
                <tr class='bg-white border-b even:bg-gray-100'>
                    <td class='px-6 py-4'>{date}</td>
                    <td class='px-6 py-4'>{description}</td>
                </tr>
                """

        return f"""
        <body class='bg-gray-100 p-8'>
            <h2 class='text-2xl font-semibold mb-4'>Your Wishlist</h2>
            <div class='overflow-x-auto'>
                <table class='min-w-full bg-white border border-gray-200 rounded-lg shadow-md'>
                    <thead class='bg-gray-200 text-gray-600'>
                        <tr>
                            <th class='px-6 py-3 border-b border-gray-200'>Date</th>
                            <th class='px-6 py-3 border-b border-gray-200'>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </body>
        """
    except FileNotFoundError:
        return "Spending log file not found."
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"

def saving_advice():
    with open('spending_log.txt', 'r') as file:
        spending_log = file.readlines()

    item_dates = defaultdict(list)
    total_spent = defaultdict(float)

    for line in spending_log:
        parts = line.strip().split(' - ')
        if len(parts) == 3:
            date_str, description, amount_bhd = parts
            date = datetime.strptime(date_str, '%Y-%m-%d %I:%M %p')
            amount_bhd = float(amount_bhd.split()[0])

            item_dates[description].append(date)
            total_spent[description] += amount_bhd

    advice_list = []
    items_list = []
    items_price = []
    total_savings = 0.0
    
    for item, dates in item_dates.items():
        dates.sort()
        first_date = dates[0]
        same_week_dates = [
            date for date in dates 
            if first_date - timedelta(days=first_date.weekday()) <= date <= first_date + timedelta(days=6)
        ]

        if len(same_week_dates) > 3:
            advice = (
                f"<br>This week, you've bought <b>{item}</b> {len(same_week_dates)} times and spent a total of "
                f"<span style='color: red;'>{total_spent[item]:.2f} BHD</span>.<br>"
            )
            items_list.append(item)
            items_price.append(f"{total_spent[item]:.2f} BHD")
            total_savings += total_spent[item]
            advice_list.append(advice)

    if items_list and items_price:
        saving_total = (
            f"Consider cutting back on your {', '.join(items_list)} purchases to save a total of "
            f"<span style='color: red;'>{total_savings:.2f} BHD</span>."
        )
    else:
        saving_total = "No items found that were purchased more than 3 times in the same week."

    return "<br>".join(advice_list) + "<br><br>" + saving_total


def handle_budget_modification(transformed_text_str):
    combined_pattern = re.compile(r'(add|remove|buy|purchase)\s*(.*?)\s*(\d+\.?\d*)\s*([$£]?)|(\d+\.?\d*)\s*([$£]?)\s*(.*?)(?:\s*(add|remove|buy|purchase))?', re.IGNORECASE)
    match = combined_pattern.search(transformed_text_str)
    if match:
        action = match.group(1)
        description = match.group(2).strip().replace("for", "").strip()
        amount_str = match.group(3)
        currency = match.group(4)
        
        if not amount_str:
            return {'error': 'No amount provided. Please specify the amount.'}
        
        try:
            amount = float(amount_str)
        except ValueError:
            return {'error': 'Invalid amount value provided.'}
        
        amount_bhd = convert_currency(amount, currency)
        
        if 'budget' not in session:
            session['budget'] = 0.0
        
        if action.lower() == "add":
            session['budget'] += amount_bhd
            return f"Added {amount_bhd:.2f} BHD to your budget."
        elif action.lower() in ['buy', 'purchase', 'remove']:
            session['budget'] -= amount_bhd
            log_spending(description, amount_bhd)
            return f"Recorded expense: {description} - {amount_bhd:.2f} BHD. Your updated budget is {session['budget']:.2f} BHD."
        else:
            return "Action not recognized. Please use 'add', 'buy', 'purchase', or 'remove'."

def convert_currency(amount, currency):
    if currency == '$':
        return usd_to_bhd(amount)
    elif currency == '£':
        return EUR_to_bhd(amount)
    else:
        return amount

def wishlist(transformed_text_str):
    transformed_text_str_lower = transformed_text_str.lower()
    if "want" in transformed_text_str_lower:
        want_index = transformed_text_str_lower.find("want") + len("want")
        desired_item = transformed_text_str[want_index:].strip()
        
        if desired_item:
            date_str = datetime.now().strftime('%Y-%m-%d')
            with open("wishlist.txt", "a") as file:
              file.write(f"{date_str} - {desired_item}\n")
            return f"'{desired_item}' added to wishlist."
        else:
            return "No item specified after 'want'. Nothing added to wishlist."
    else:
        return "No 'want' found in input. Nothing added to wishlist."
def reset():
    budget==0
    return "Your budget has been reset to zero"


@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message')
    if not message:
        return jsonify({'error': 'No message provided.'})
    
    transformed_text_str = parse_message(message)
    print(f"Transformed text: {transformed_text_str}")

    if "clear" in transformed_text_str.lower() or "delete" in transformed_text_str.lower():
        response = clear_spending_logs()
    elif "my spending" in transformed_text_str.lower() or "record" in transformed_text_str.lower():
        response = show_spending_logs()
    else:
        response = handle_budget_modification(transformed_text_str)
        if isinstance(response, dict):  # Check if response is an error dict
            return jsonify(response)
    if "want"in transformed_text_str.lower():
        response=wishlist(transformed_text_str)
    if "wishlist" in transformed_text_str.lower():
        response =display_wishlist() 
    if "reset" in transformed_text_str.lower():
        response =reset()
    if "advice"in transformed_text_str.lower():
        response =saving_advice() 
        
   

    
    return jsonify({
        'updated_budget': session.get('budget', 0.0),
        'response': response
    })


if __name__ == '__main__':
    app.run(debug=True)
