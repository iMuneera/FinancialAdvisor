from datetime import datetime 

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
    
def display_wishlist():
    try:
        with open('wishlist.txt', 'r') as file:
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
                    <td class='px-6 py-4'>{date}</td>
                    <td class='px-6 py-4'>{description}</td>
                </tr>
                """

        return f"""
        <body class='bg-gray-100 p-12'>
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
        return "Wishlist file not found."
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"