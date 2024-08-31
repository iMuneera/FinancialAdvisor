from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import re,spacy,secrets
from datetime import datetime ,timedelta

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

@app.route('/chat', methods=['POST'])
def chat():
  
    message = request.form.get('message')
    if not message:
        return jsonify({'error': 'No message provided.'})
    doc = nlp(message)
    transformed_text = []
    for token in doc:
        if token.pos_ == 'VERB' and token.tag_ not in ['VB', 'VBG', 'VBP', 'VBZ']:
            transformed_text.append(token.lemma_)
        else:
            transformed_text.append(token.text)
    transformed_text_str = ' '.join(transformed_text)


    print(f"Transformed text: {transformed_text_str}")

   






    if "clear" in transformed_text_str.lower() or "delete" in transformed_text_str.lower():
            with open('spending_log.txt', 'w') as file:
                response = "spending logs has been cleared"



   

    if "my spending" in transformed_text_str.lower() or "record" in transformed_text_str.lower():
  
        try:
            with open('spending_log.txt', 'r') as file:
                spending_log = file.readlines()
            
            if not spending_log:
                response = "No spending records found."
            else:
                # Prepare HTML table with Tailwind CSS
                table_rows = ''
                for line in spending_log:
                    parts = line.strip().split(' - ')
                    if len(parts) == 3:
                        date, description, amount_bhd = parts
                        amount_bhd = float(amount_bhd.split()[0])  # Extract numeric part and convert to float
                        if amount_bhd >= 100:
                            amount_class = 'text-red-600'
                        elif amount_bhd >= 10:
                            amount_class = 'text-yellow-600'
                        else:
                            amount_class = 'text-gray-800'
                        
                        table_rows += f"""
                        <tr class='bg-white border-b even:bg-gray-100'>
                            <td class='px-6 py-4'>{date}</td>
                            <td class='px-6 py-4'>{description}</td>
                            <td class='px-6 py-4 {amount_class}'>{amount_bhd:.2f} BHD</td>
                        </tr>
                        """
                
                response = f"""
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
            response = "Spending log file not found."
        except Exception as e:
            response = f"An error occurred while reading the file: {str(e)}"


    else:
        combined_pattern = re.compile(r'(add|remove|buy|purchase)\s*(.*?)\s*(\d+\.?\d*)\s*([$£]?)|(\d+\.?\d*)\s*([$£]?)\s*(.*?)(?:\s*(add|remove|buy|purchase))?', re.IGNORECASE)

    
        match = combined_pattern.search(transformed_text_str)
        if match:
            action = match.group(1)  
            description = match.group(2).strip()  
            description = description.replace("for", "").strip()
            amount_str = match.group(3)  
            currency = match.group(4)  
            print(f"Action: {action}")
            print(f"Description: '{description}'")
            print(f"Amount : {amount_str}")
            print(f"Currency: {currency}")

            if not amount_str:
                return jsonify({'error': 'No amount provided. Please specify the amount.'})

            try:
                amount = float(amount_str)
                print(amount)
            except ValueError:
                return jsonify({'error': 'Invalid amount value provided.'})

            if currency == '$':
                amount_bhd = usd_to_bhd(amount)
                print(amount_bhd)
            elif currency == '£':
                amount_bhd = EUR_to_bhd(amount)
                print(amount_bhd)
            else:
                amount_bhd = amount

            if 'budget' not in session:
                session['budget'] = 0.0

            if action.lower() == "add":
                session['budget'] += amount_bhd
                response = f"Added {amount_bhd:.2f} BHD to your budget."
            elif action.lower() in ['buy', 'purchase', 'remove']:
                session['budget'] -= amount_bhd
                log_spending(description, amount_bhd)
                response = f"Recorded expense: {description} - {amount_bhd:.2f} BHD. Your updated budget is {session['budget']:.2f} BHD."
            else:
                response = "Action not recognized. Please use 'add', 'buy', 'purchase', or 'remove'."
        elif "want" in transformed_text_str.lower():
        # Get today's date
            today = datetime.today()
            print(today)
            target_date = today.replace(day=26)
            print(target_date)
            if today.day > 26:
                # Move to the first day of the next month
                next_month = today.replace(day=1) + timedelta(days=31)
                # Set the target date to the 26th of the next month
                target_date = next_month.replace(day=26)
                print(target_date)

                days_until_target = (target_date - today).days
                # Output the current day and days until the 26th
                print(f"Today is: {today.strftime('%A, %Y-%m-%d')}")
                print(f"Days until the 26th: {days_until_target} days")
                response = "ok"
        elif "$" in user_input:
            amount = float(user_input.replace("$", "").strip())
        if amount > 10:  # Example condition, you can adjust this
            response = "No need"
        else:
            response = "You can buy it!"
    else:
        response = "Please enter a valid amount or item."

    return jsonify({'result': response})

        





    return jsonify({
        'updated_budget': session.get('budget', 0.0),
        'response': response
    })


if __name__ == '__main__':
    app.run(debug=True)
