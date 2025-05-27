# import pandas as pd

# data = {
#     "calories": [420, 540, 123, 65, 560, 354],
#     "duration": [50, 40, 45, 46, 56, 16],
# }
#
# df = pd.DataFrame(data)
#
# df.tail()

import pandas as pd
import os

data = {
    "Name": ['John', 'Ivan', 'Peter', 'Legolas'],
    "Age": [34, 32, 25, 345],
    "City": ['New York', 'Plovdiv', 'Paris', 'Merkwood'],
}

df = pd.DataFrame(data)

file_path = 'example.xlsx'

df.to_excel(file_path, index=False)

os.startfile(file_path)

print(f"Excel file '{file_path} created successfully!")