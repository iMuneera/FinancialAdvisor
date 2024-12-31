from datetime import datetime 

def wishlist(description):
        if description:
            date_str = datetime.now().strftime('%Y-%m-%d')
            description=description[0].strip().capitalize()
            with open("txt/wishlist.txt", "a") as file:
                file.write(f"{date_str} - {description}\n")
            return f"'{description}' added to wishlist."
        else:
            return "No item specified after 'want'. Nothing added to wishlist."
    
def display_wishlist():
    try:
        with open('txt/wishlist.txt', 'r') as file:
            wishlist = file.readlines()

        if not wishlist:
            return "No items in wishlist."

        table_rows = ''
        for line in wishlist:
            parts = line.strip().split(' - ')
            if len(parts) == 2:
                date, description = parts
                table_rows += f"""
                <tr class='bg-white border-b even:bg-gray-100 p-12'>
                    <td class='px-6 py-4'>{description}</td>
                </tr>
                """

        return f"""
        <body class='bg-gray-100 p-12'>
            <h2 class='text-2xl font-semibold mb-4'>Your Wishlist</h2>
            <div class='overflow-x-auto'>
                <table class='min-w-full bg-white border border-gray-200 rounded-lg shadow-md dark:text-gray-500 '>
                    <thead class='bg-gray-200 text-gray-600'>
                        <tr class='dark:text-gray-500'>
                            <th class='px-6 py-3 border-b border-gray-200'>Items</th>
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
        return "Wishlist file not found."
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"