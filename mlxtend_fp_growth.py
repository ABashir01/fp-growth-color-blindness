import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import sys
import os
import ast
import re

try:
    frequent_itemsets = pd.read_csv("full_frequent_itemsets.csv")
    print(len(frequent_itemsets))

    def parse_frozenset(itemset_str):
        try:
            itemset_str = itemset_str.replace("frozenset(", "").replace(")", "").replace("{", "").replace("}", "").replace("'", "").strip()
            items = [item.strip() for item in itemset_str.split(",") if item.strip()]
            return frozenset(items)
        except Exception as e:
            print(f"NOOOOOOOOOOOOOOOOOOO ERROR {e}")
            raise ValueError(f"Cannot parse frozenset: {itemset_str}")

    frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(parse_frozenset)
except:
    def load_data():
        print("Loading data...")
        data = pd.read_csv("full_combined_23andme_binary_with_phenotypes.csv", index_col=0)

        print("Searching rows...")
        data_rows = []
        for _, row in data.iterrows():
            data_row = set(data.columns[row == 1])
            data_rows.append(data_row)

        print("Done loading data")
        return data_rows

    dataset = load_data()

    print("Encoding data...")
    te = TransactionEncoder()
    fitted = te.fit(dataset)
    encoded = fitted.transform(dataset, sparse=True)
    df = pd.DataFrame.sparse.from_spmatrix(encoded, columns=te.columns_)

    print("Running FP-Growth...")
    frequent_itemsets = fpgrowth(df, min_support=0.45, use_colnames=True, verbose=1)
    print(frequent_itemsets)
    f = open("full_frequent_itemsets.csv", "w")
    f.write(frequent_itemsets.to_csv())
    f.close()

frequent_itemsets = frequent_itemsets[frequent_itemsets['itemsets'].apply(len) <= 5]
print(frequent_itemsets)
print(len(frequent_itemsets))    

# Generate association rules
print("Generating association rules...")
rules = association_rules(df=frequent_itemsets, metric="lift", min_threshold=1, num_itemsets=len(frequent_itemsets))
print(rules)
f = open("full_association_rules.csv", "w")
f.write(rules.to_csv())
f.close()
print("Done")