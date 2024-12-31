from datetime import datetime, timedelta
import spacy,os
from functions.utils import convert_currency
nlp = spacy.load('en_core_web_sm')
from datetime import datetime, timedelta
from functions.budget import budget
        

def display_subscription():
    global budget
    subscriptions = []
    list_of_subscriptions = []
    
    try:
        with open('txt/subscription.txt', 'r') as file:
            subscription = file.readlines()
            print(subscription)  
            
        if not subscription:
            return "No subscription records found."
        
        for line in subscription:
            parts = line.strip().split(',')
            print(line) 
            print(parts) 
            
            if len(parts) == 5:
                service_name, duration, start_date, renewal_date_str, amount = parts
                renewal_date = datetime.strptime(renewal_date_str.strip(), '%Y-%m-%d').date()
                amount = float(amount.replace(' BHD', '').strip())
                print(f"Service name: {service_name}, Renewal date: {renewal_date}, Amounsadasdasdasdt: {amount}")
                # Calculate days remaining for renewal
                days_remaining = (renewal_date - datetime.now().date()).days
                
           
                if days_remaining <= 4:
                    days_class="text-red-600"
                else:
                    days_class="text-green-600"
                
                subscriptions.append((service_name.capitalize(), renewal_date, amount, days_remaining, days_class))
        
        for service_name, renewal_date, amount, days_remaining, days_class in subscriptions:
          
            list_of_subscriptions.append(
                    f"<div class=' px-6'>"
                    f"<li>You have a subscription for <strong>{service_name}</strong> that will renew on <strong> {renewal_date.strftime('%Y-%m-%d')} </strong>"
                    f"for <strong >{amount:.2f} </strong> BHD  <br> You have <strong class='{days_class}'>{days_remaining} days </strong> remaining.</li> <br> </div>" 
                )
        
        # Return as an unordered list in HTML
        return f"<ul class='list-disc'>{''.join(list_of_subscriptions)} </ul>"

    except FileNotFoundError:
        return "Subscription log file not found."




def log_subscription(service_name, start_date, renewal_date, duration, amount):
    try:
        start_date = datetime.now().strftime('%Y-%m-%d')
        with open("txt/subscription.txt", "a") as file:
            file.write(f"{service_name} , {duration} , {start_date} , {renewal_date} , {amount:.2f} BHD\n")
    except Exception as e:
        return f"An error occurred while logging the subscriptions: {str(e)}"
    


def handle_subscription(service_name, start_date, renewal_date, duration, amount):
    global budget
    print(f"Budget before subscription: {budget}")
    budget -= float(amount)
    log_subscription(service_name, start_date, renewal_date, duration, amount)
    print(service_name, duration, start_date, renewal_date, amount)
    print(f"Budget after subscription: {budget}")
    response = (
        f"You have successfully subscribed to {service_name} for {duration} days for {amount:.2f} BHD. "
        f"Your updated budget is {budget:.2f} BHD."
    )
    return response, budget



def subscription_message(doc):
    tokenisedword = []
    service_name = ''
    message_tag = []
    amount = 0
    currency = ""  
    start_date = datetime.now().strftime('%Y-%m-%d')
    renewal_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')  
    duration = 30

    for token in doc:
        print(token.text, token.tag_)
        tokenisedword.append(token.lemma_)
        message_tag.append(token.pos_)
        
        if token.pos_ == 'NUM':
            amount = float(token.text)
            print(f"Amount found: {amount}")

        if token.pos_ == 'PROPN':
            service_name = token.text 
            print(f"Service name found: {service_name}")

        if token.pos_ == 'SYM':
            if token.text in ['$','£']: 
                currency = token.text  
                print(f"Currency detected: {currency}")

    if currency:
        amount = convert_currency(float(amount), currency)  
        print(f"Converted amount: {amount}")

    return service_name, start_date, renewal_date, duration, amount
