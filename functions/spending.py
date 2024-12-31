import matplotlib,os,re
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import pandas as pd
matplotlib.use('Agg')

def show_spending_logs():
    try:
        with open('txt/spending_log.txt', 'r') as file:
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
                <tr class='bg-white border-b even:bg-gray-100 p-12 '>
                    <td class='px-6 py-4 dark:text-gray-500'>{date}</td>
                    <td class='px-6 py-4 dark:text-gray-500'>{description}</td>
                    <td class='px-6 py-4 dark:text-gray-500  {amount_class}'>{amount_bhd:.2f} BHD</td>
                </tr>
                """

        return f"""
        <body class='bg-gray-100 p-12'>
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

def clear_spending_logs():
    try:
        with open('txt/spending_log.txt', 'w') as file:
            file.write('') 
        return "Spending logs have been cleared."
    except Exception as e:
        return f"An error occurred while clearing the file: {str(e)}"

def log_spending(description, amount_bhd):
    try:
        date_str = datetime.now().strftime('%Y-%m-%d %I:%M %p')
        with open("txt/spending_log.txt", "a") as file:
            file.write(f"{date_str} - {description} - {amount_bhd:.2f} BHD\n")
    except Exception as e:
        return f"An error occurred while logging the spending: {str(e)}"

def get_amount_class(amount_bhd):
    if amount_bhd >= 100:
        return 'text-red-800'
    elif amount_bhd >= 10:
        return 'text-yellow-600'
    else:
        return 'text-gray-800'

def spending_graph():
    file_path = 'txt/spending_log.txt'
    date_format = "%Y-%m-%d"
    date_str = None
    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    daily_spending = {day: 0.0 for day in weekdays}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()  # Read all lines into a list
        if lines:
            last_line = lines[-1].strip()  # Get the last non-empty line
            match = re.match(r'(\d{4}-\d{2}-\d{2})\s.*-\s([\d.]+)\sBHD', last_line)
            if match:
                date_str = match.group(1)  # Extract the date string from the match
                
                print(f"Extracted date: {date_str}")
                print(type(date_str))
                print(f"Last date from file: {date_str}")
                
                # Proceed only if date_str is valid
                if date_str:
                    lastdate_obj = datetime.strptime(date_str, date_format)
                    week1 = lastdate_obj.isocalendar()[1]
                    print(f"Last date (datetime object): {lastdate_obj}, Week: {week1}")
                    
                    todayis = datetime.now().strftime('%Y-%m-%d')
                    print(f"Today's date: {todayis}")
                    today_obj = datetime.strptime(todayis, date_format)
                    week2 = today_obj.isocalendar()[1]
                    
                    if week1 == week2:
                        print("The dates are in the same week.")
                    else:
                        print("The dates are not in the same week.")
            else:
                print("No valid date found in the last line.")
        else:
            print("The file is empty.")

            
        for line in lines:
            #year-month-day - Price
            match = re.match(r'(\d{4}-\d{2}-\d{2})\s.*-\s([\d.]+)\sBHD', line)
           
            if match:
                date_str = match.group(1)
                amount = float(match.group(2))

                # date without time to map it with the day of the week 
                 
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                print(date_obj)
                
                # Get day of the week 
                day_of_week = date_obj.strftime('%A')
                print(day_of_week)
                
                # Sum amounts for each day in the week
                daily_spending[day_of_week] += amount
                print(daily_spending[day_of_week])
    totals = [daily_spending[day] for day in weekdays]
 
    # Step 3: Color bars where spending is more than 20 BHD
    colors = ['red' if total >= 50 else 'yellow' for total in totals]
    # Step 3: Generate the graph
    plt.figure(figsize=(10, 6))
    bars = plt.bar(weekdays, totals, color=colors)

     # Step 5: Add text (amounts) on top of each bar
    for bar, total in zip(bars, totals):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{total:.2f} BHD', ha='center', va='bottom')


    # Labeling the graph
    plt.xlabel('Day of the Week')
    plt.ylabel('Total Amount Spent (BHD)')
    plt.title('Spending by Day of the Week')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    # Save the graph to the static/images directory
    plt.savefig('static/images/week_spending.png', transparent=True)
    plt.close()  
    
def purchase_graph():
    print("Generating purchase graph...")
    file_path = 'txt/spending_log.txt'

    item_names = []
    prices = []
    item_totals = defaultdict(float)

    with open(file_path, 'r') as file:
        for line in file:
            print(line)
            pattern = r"-\s([a-zA-Z]+)\s-\s([\d,]+(?:\.\d{2})?)\sBHD"
            matches = re.findall(pattern, line)
            
            for match in matches:
                item_name, price = match
                item_totals[item_name] += float(price.replace(",", ""))  # Add price to the item total

        # Separate item names and their total prices for plotting
        item_names = list(item_totals.keys())
        prices = list(item_totals.values())
        pastel_colors = ['#baffc9', '#bae1ff', '#d4a5a5', '#a0d8a0', '#ffb3d9', '#ffdfba', '#baffc9', '#bae1ff', '#d4a5a5', '#a0d8a0', '#ffb3d9', '#ffdfba']
        
        # Plot the pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(prices, labels=[f'{name} ({total:.2f} BHD)' for name, total in zip(item_names, prices)], colors=pastel_colors, autopct='%1.f%%', startangle=140)
        plt.title("Personal Expense Report")
        plt.savefig('static/images/purchases.png', transparent=True)
        plt.close()