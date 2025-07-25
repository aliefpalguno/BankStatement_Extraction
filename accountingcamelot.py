# -*- coding: utf-8 -*-
"""AccountingCamelot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PcudjSURjrH3mpWsxQs-msbkMHSTtbCS

# Dependencies and Libraries
"""

!pip install camelot-py[cv]
!pip install pandas openpyxl

!apt-get install -y ghostscript

"""Check Dependencies"""

import camelot

print("Camelot version:", camelot.__version__)
!gs --version

!pip install ipywidgets
!pip install openpyxl

import camelot
import pandas as pd

# Step 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

"""---


#Extract Bank Statement Data
**PLEASE ADJUST TABLE AREA AND COLUMNS WITH EVERY BANK STATEMENT FILES**

```
# Parameter

#Define the area(s) to extract tables from
table_areas = ["30,610,580,90/60"]  # Modify or add more areas as needed

# Define the column area
columns = ["80,190,300,350,450,490"]

```
"""

import camelot
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

# Path to the PDF file
pdf_path = r"/content/drive/MyDrive/Akuntansi/BankStatementBCA.pdf"

# Define the area(s) to extract tables from
table_areas = ["30,610,580,50"]  # Modify or add more areas as needed

# Define the column area
columns = ["80,190,300,350,450,490"]

# Specify pages to process ("all" for all pages, or "1,2,3" for specific pages)
pages_to_process = "all"

# Extract tables from the specified pages and areas
tables = camelot.read_pdf(pdf_path, flavor="stream", table_areas=table_areas, columns=columns, pages=pages_to_process)

# Check if any tables were found
if tables.n == 0:
    print("No tables were found in the specified PDF and areas.")
else:
    # List to store individual DataFrames
    dataframes = []

    # Process each extracted table
    for i, table in enumerate(tables):
        print(f"Processing table {i + 1}...")

        # Get the table DataFrame
        df = table.df

        # If the table is from the second page onward, drop the first row
        if i > 0:
            df = df.iloc[1:]  # Drop the first row

        # Append the adjusted DataFrame to the list
        dataframes.append(df)

        # Optional: Save each table as a separate CSV for debugging
        # df.to_csv(f"table_page_{i + 1}.csv", index=False)
        # print(f"Table {i + 1} saved as 'table_page_{i + 1}.csv'.")

        # Plot the contour for the table
        camelot.plot(table, kind="contour")
        plt.title(f"Table {i + 1} Contour Plot")
        plt.show()

    # Merge all DataFrames into a single DataFrame
    merged_table = pd.concat(dataframes, ignore_index=True)

    # Use the first row of the merged table as the header
    merged_table.columns = merged_table.iloc[0]  # Set the first row as the header
    merged_table = merged_table[1:]  # Drop the first row as it's now the header
    merged_table.reset_index(drop=True, inplace=True)  # Reset the index

    # Display the merged table
    print("Merged Table:")
    display(merged_table)

    # Save the merged table to a single CSV file
    # merged_table.to_csv("merged_table.csv", index=False)
    # print("Merged table saved as 'merged_table.csv'.")

"""DF1 as ALSO THE MERGED TABLE

Dont Forget to RUN THIS CODE AND FIX THE COLUMN INDEXING
"""

df1 = pd.DataFrame(merged_table)

# Inspect column names
print(df1.columns)

# Check initial column names
print("Before renaming:", merged_table.columns)

# Rename the second and sixth columns
merged_table.columns.values[1] = "TRANSAKSI"  # Rename the second column
merged_table.columns.values[5] = "DEBIT"  # Rename the sixth column

# Confirm the changes
print("After renaming:", merged_table.columns)

# Check for duplicate column names
print("Column names before fixing:", merged_table.columns)
print("Duplicate column names:", merged_table.columns[merged_table.columns.duplicated()])

# Make column names unique by appending suffixes
merged_table.columns = pd.Series(merged_table.columns).apply(
    lambda x: f"{x}_{merged_table.columns.tolist().count(x)}" if merged_table.columns.tolist().count(x) > 1 else x
)

# Confirm unique column names
print("Column names after fixing:", merged_table.columns)

"""Merge Rows with TANGGAL rows"""

# Define the condition for rows to be deleted (e.g., rows where KETERANGAN is empty)
condition = df1["DEBIT"] == "Bersambung ke Halaman berikut"  # Delete rows where KETERANGAN is empty

# Delete rows based on the condition
df1 = df1[~condition].reset_index(drop=True)  # Use ~ to negate the condition

from IPython.display import display
display(df1)

def merge_rows(df1):
    merged_data = []
    temp_row = None  # Temporary storage for merging rows

    for _, row in df1.iterrows():
        # Check if TANGGAL is not empty or NaN
        if isinstance(row['TANGGAL'], str) and row['TANGGAL'].strip():
            # Save the current temp_row if it exists
            if temp_row is not None:
                merged_data.append(temp_row)
            temp_row = row.copy()
        else:
            # If TANGGAL is empty, merge KETERANGAN with the previous row
            if temp_row is not None:
                temp_row['KETERANGAN'] = f"{temp_row['KETERANGAN']} {row['KETERANGAN']}".strip()

    # Append the last temp_row
    if temp_row is not None:
        merged_data.append(temp_row)

    return pd.DataFrame(merged_data)

# Apply the function to clean the extracted table
cleaned_table = merge_rows(merged_table)

# Reset the index for readability
cleaned_table = cleaned_table.reset_index(drop=True)

# Display the DataFrame
print("Extracted Table:")
from IPython.display import display
display(cleaned_table)  # This will show a nicely formatted table in Colab

"""Keterangan cleaning to only obtain ACCOUNT HOLDER NAME"""

# Convert to DataFrame
df2 = pd.DataFrame(cleaned_table)

# Define a function to filter uppercase words
def filter_uppercase(keterangan):
    words = keterangan.split()
    # Define the words to exclude
    exclude_words = {"BIF", "TRANSFER", "DR"}
    # Select only words that are all uppercase and have no digits
    filtered = [
        word for word in words
        if word.isupper() and not any(char.isdigit() for char in word) and word not in exclude_words
    ]
    return " ".join(filtered)

# Apply the function to the KETERANGAN column
df2['KETERANGAN'] = df2['KETERANGAN'].apply(filter_uppercase)

# Display the updated DataFrame
from IPython.display import display
display(df2)

"""If Want to Obtain The Cleaned Table
**ONLY IF NECESARRY**
"""

# Export to Excel
excel_path = "/content/drive/MyDrive/Akuntansi/cleanedTable_bankState.xlsx"  # Specify the output file path
df2.to_excel(excel_path, index=False, engine="openpyxl")
print(f"Merged table exported to '{excel_path}'.")

"""

---
# Accounting Program
To multiple every transaction and debit credit decision
"""

# Drop the TRANSAKSI and SALDO columns
df2_cleaned = df2.drop(columns=["TRANSAKSI", "SALDO"])

# Display the duplicated DataFrame
from IPython.display import display
display(df2_cleaned)

# Rename CBG to NAMA_AKUN
df2_cleaned.rename(columns={"CBG": "NAMA_AKUN"}, inplace=True)

# Add new columns
df2_cleaned.insert(df2_cleaned.columns.get_loc("NAMA_AKUN") + 1, "AKUN", "")  # Add AKUN column after NAMA_AKUN
df2_cleaned.rename(columns={"MUTASI": "DEBET"}, inplace=True)  # Rename MUTASI to DEBET
df2_cleaned.insert(df2_cleaned.columns.get_loc("DEBET") + 1, "KREDIT", "")  # Add KREDIT column after DEBET

# Display the rearranged DataFrame
from IPython.display import display
display(df2_cleaned)

# Duplicate each row
df2_duplicated = df2_cleaned.loc[df2_cleaned.index.repeat(2)].reset_index(drop=True)

# Apply logic to modify DEBET and KREDIT columns
for i in range(0, len(df2_duplicated), 2):
    # First (real) transaction
    if df2_duplicated.loc[i, "DEBIT"] == "DB":
        # Keep DEBET in the first row, move it to KREDIT in the second row
        df2_duplicated.loc[i + 1, "KREDIT"] = df2_duplicated.loc[i, "DEBET"]
        df2_duplicated.loc[i + 1, "DEBET"] = ""
    else:
        # Move DEBET to KREDIT in the first row, leave it in DEBET in the second row
        df2_duplicated.loc[i, "KREDIT"] = df2_duplicated.loc[i, "DEBET"]
        df2_duplicated.loc[i, "DEBET"] = ""
        df2_duplicated.loc[i + 1, "DEBET"] = df2_duplicated.loc[i, "KREDIT"]
        df2_duplicated.loc[i + 1, "KREDIT"] = ""

# Display the duplicated DataFrame
from IPython.display import display
display(df2_duplicated)

# Convert TANGGAL to DD/MM/YYYY with year 2024
df2_duplicated["TANGGAL"] = pd.to_datetime(df2_duplicated["TANGGAL"] + "/2024", format="%d/%m/%Y").dt.strftime("%d/%m/%Y")

# Display the duplicated DataFrame
from IPython.display import display
display(df2_duplicated)

# Export to Excel
excel_path = "/content/drive/MyDrive/Akuntansi/BankStateBCA.xlsx"  # Specify the output file path
df2_duplicated.to_excel(excel_path, index=False, engine="openpyxl")
print(f"Merged table exported to '{excel_path}'.")