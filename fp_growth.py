import pandas as pd


def load_data():
    data = pd.read_csv("combined_23andme_binary_with_phenotypes.csv", index_col=0)

    data_rows = []
    for _, row in data.iterrows():
        data_row = set(data.columns[row == 1])
        data_rows.append(data_row)

    return data_rows


def create_frequency_table(data_rows, min_support):
    frequency_table = {}
    for row in data_rows:
        for item in row:
            if item in frequency_table:
                frequency_table[item] += 1
            else:
                frequency_table[item] = 1

    for item in list(frequency_table.keys()):
        if frequency_table[item] < min_support:
            del frequency_table[item]

    return frequency_table


def create_ordered_data_rows(data_rows, frequency_table):
    ordered_data_rows = []
    for row in data_rows:
        ordered_row = [item for item in frequency_table if item in row]
        ordered_row.sort(key=lambda x: (-frequency_table[x], x))
        ordered_data_rows.append(ordered_row)

    return ordered_data_rows


class FPTreeNode:
    def __init__(self, item, frequency, parent):
        self.item = item
        self.frequency = frequency
        self.parent = parent
        self.children = {}

class FPTree:
    def __init__(self):
        self.root = FPTreeNode(None, None, None)
        self.instance_table = {}

    def add_transaction(self, transaction):
        current_node = self.root
        for item in transaction:
            if item in current_node.children:
                child = current_node.children[item]
                child.frequency += 1
            else:
                child = FPTreeNode(item, 1, current_node)
                current_node.children[item] = child
                if item in self.instance_table:
                    self.instance_table[item].append(child)
                else:
                    self.instance_table[item] = [child]
            current_node = child
    
    def get_frequent_patterns(self, min_support):
        frequent_patterns = {}

        def mine_tree(tree, prefix, frequent_patterns):
            sorted_items = sorted(tree.instance_table.keys(), key=lambda x: sum(node.frequency for node in tree.instance_table[x]))
            for item in sorted_items:
                new_prefix = prefix + [item]
                frequency = sum(node.frequency for node in tree.instance_table[item])
                if frequency >= min_support:
                    frequent_patterns[tuple(new_prefix)] = frequency

                    conditional_tree = FPTree()
                    for node in tree.instance_table[item]:
                        path = []
                        parent = node.parent
                        while parent and parent.item is not None:
                            path.append(parent.item)
                            parent = parent.parent
                        path.reverse()
                        for _ in range(node.frequency):
                            conditional_tree.add_transaction(path)

                    if len(conditional_tree.root.children) > 0:
                        mine_tree(conditional_tree, new_prefix, frequent_patterns)

        mine_tree(self, [], frequent_patterns)
        return frequent_patterns

                



    
    def print_tree(self, node=None, indent=0):
        if node is None:
            node = self.root
        print('  ' * indent + f'Item: {node.item}, Frequency: {node.frequency}')
        for child in node.children.values():
            self.print_tree(child, indent + 1)
    

def fp_growth(data_rows, min_support):
    print("Rows: ", data_rows)
    frequency_table = create_frequency_table(data_rows, min_support)
    print("Frequency Table:", frequency_table)
    ordered_data_rows = create_ordered_data_rows(data_rows, frequency_table)
    fp_tree = FPTree()
    for row in ordered_data_rows:
        fp_tree.add_transaction(row)

    return fp_tree.get_frequent_patterns(min_support)



def main():
    data_rows = load_data()
    min_support = 3
    patterns = fp_growth(data_rows, min_support)
    f = open("output.txt", "w")
    print("Frequent Patterns:")

    for pattern, frequency in patterns.items():
        f.write(str(pattern) + " : " + str(frequency) + "\n")
        print(pattern, ":", frequency)
        
    f.close()


if __name__ == "__main__":
    main()
