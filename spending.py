import matplotlib,os,re
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import pandas as pd

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
                <tr class='bg-white border-b even:bg-gray-100 p-12 '>
                    <td class='px-6 py-4'>{date}</td>
                    <td class='px-6 py-4'>{description}</td>
                    <td class='px-6 py-4 {amount_class}'>{amount_bhd:.2f} BHD</td>
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
        with open('spending_log.txt', 'w') as file:
            file.write('')  # Clear the file
        return "Spending logs have been cleared."
    except Exception as e:
        return f"An error occurred while clearing the file: {str(e)}"

def log_spending(description, amount_bhd):
    try:
        date_str = datetime.now().strftime('%Y-%m-%d %I:%M %p')
        with open("spending_log.txt", "a") as file:
            file.write(f"{date_str} - {description} - {amount_bhd:.2f} BHD\n")
    except Exception as e:
        return f"An error occurred while logging the spending: {str(e)}"

def get_amount_class(amount_bhd):
    if amount_bhd >= 100:
        return 'text-red-600'
    elif amount_bhd >= 10:
        return 'text-yellow-600'
    else:
        return 'text-gray-800'

def spending_graph():
    file_path = 'spending_log.txt'
   # Initialize a dictionary to hold totals for each day
  # Initialize a dictionary with all days of the week set to zero
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_spending = {day: 0.0 for day in weekdays}

    with open(file_path, 'r') as file:
        for line in file:
            # Extract date and amount using regex
            match = re.match(r'(\d{4}-\d{2}-\d{2})\s.*-\s([\d.]+)\sBHD', line)
            if match:
                date_str = match.group(1)
                amount = float(match.group(2))

                # Convert date string to datetime object
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')

                # Get day of the week (e.g., Monday, Tuesday)
                day_of_week = date_obj.strftime('%A')

                # Sum amounts based on day of the week
                daily_spending[day_of_week] += amount

    # Step 2: Create lists of days and total amounts (ensure order of days)
    days = weekdays  # We keep this ordered for plotting
    totals = [daily_spending[day] for day in days]
    
    # Step 3: Color bars where spending is more than 20 BHD
    colors = ['red' if total >= 20 else 'yellow' for total in totals]
    # Step 3: Generate the graph
    plt.figure(figsize=(10, 6))
    bars = plt.bar(days, totals, color=colors)

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
    plt.savefig('static/images/week_spending.png')
    plt.close()  # Close the plot to free up memory