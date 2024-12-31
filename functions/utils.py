import spacy
from word2number import w2n
nlp = spacy.load('en_core_web_lg')
def convert_currency(amount, currency):
    print(f"convert currrency func called line 20")
    if currency == '$':
        print(f"usd to bhd func called line 31")
        return usd_to_bhd(amount)

    else:
        return amount
#---------------------------------------------    
def usd_to_bhd(usd_amount):
    conversion_rate = 0.38  
    return usd_amount * conversion_rate

def parse_message(doc):
    action = []
    quantity = 1  
    amount_str = None
    description = []
    number = None  
    currency = None
    currency_dict = {"dollar": "$"}

    for token in doc:
        print(f"Token: {token.text}, POS: {token.pos_}, DEP: {token.dep_}, LEMMA: {token.lemma_} ,head: {token.head.pos_}, head_text: {token.head.text}")
        # Detect currency
        if token.lemma_.lower() in currency_dict:
            currency = currency_dict[token.lemma_.lower()]  
            print(f"Detected currency from lemma: {currency}")
        elif token.pos_ == 'SYM' and token.text in ['$']:
            currency = token.text
            print(f"Detected currency from symbol: {currency}")

        # Detect numbers
        if token.pos_ == 'NUM':
            if (token.dep_ in ['nummod', 'pobj'] and token.head.pos_ in ['SYM', 'ADP', 'VERB']) or (token.head.lemma_ in currency_dict):
                try:
                    number = float(token.text) if token.text.replace('.', '', 1).isdigit() else w2n.word_to_num(token.text)
                    print(f"Detected price: {number}")
                except ValueError:
                    print(f"Error converting {token.text} to number")
            elif token.dep_ == 'nummod' and token.head.pos_ == 'NOUN':
                try:
                    quantity = float(token.text) if token.text.replace('.', '', 1).isdigit() else w2n.word_to_num(token.text)
                    print(f"Detected quantity: {quantity}")
                except ValueError:
                    print(f"Error converting {token.text} to quantity")
            else:
                raise ValueError("No valid number words found! Please enter a valid number word (eg. two million twenty three thousand and forty nine)")

        # Detect item description
        if token.pos_ == 'NOUN' and token.lemma_ not in currency_dict and token.dep_ is not None and token.dep_ not in ['det','npadvmod']:
            description.append(token.text.lower())
            print(f"Description: {description}")

        # Process verbs
        if token.pos_ == 'VERB' and token.dep_ == 'ROOT':
            action.append(token.lemma_)
            print(f"Verb: {token.text}")
    if len(action) == 0:
        return None,None,None,None

    # Calculate amount_str as quantity * price if both are detected
    elif number is not None and quantity is not None:
        print(f"Quantity: {quantity}, Price: {number}")
        amount_str = str(number * quantity)
        print(f"Amount string: {amount_str}")
    else:
        amount_str = "0"  
        print(f"Amount: {amount_str}, Currency: {currency}, Description: {description}, Action: {action}")
    return amount_str, currency, description, action
