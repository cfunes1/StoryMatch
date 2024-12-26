# display_tables.py
import pandas as pd
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)        # Wider display
pd.set_option('display.max_colwidth', 50)   # Limit column width for readability

def try_read_csv(filename):
    """Try reading CSV with different encodings"""
    encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'latin1']
    
    for encoding in encodings:
        try:
            return pd.read_csv(filename, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading {filename}: {str(e)}")
            return None
    
    print(f"Failed to read {filename} with any of the attempted encodings")
    return None

def display_table(filename, table_name):
    """Read and display first 5 rows of a CSV file"""
    df = try_read_csv(filename)
    if df is not None:
        print(f"\n{'-'*80}")
        print(f"{table_name} - First 5 rows:")
        print(f"{'-'*80}")
        print(df.head())
        print(f"\nColumns in {table_name}:")
        print(df.columns.tolist())
        print(f"\nShape of {table_name}: {df.shape}")
        
        # Display data types
        print(f"\nData types in {table_name}:")
        for col, dtype in df.dtypes.items():
            print(f"{col}: {dtype}")
            
        # Display null counts
        null_counts = df.isnull().sum()
        if null_counts.any():
            print(f"\nNull values in {table_name}:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"{col}: {count} null values")

def main():
    # Display each table
    display_table('Stories.csv', 'Stories')
    display_table('questions.csv', 'Questions')  # Updated filename
    display_table('Questions_Stories.csv', 'Questions-Stories Mapping')

if __name__ == "__main__":
    main()