import pandas as pd
import os
import sys
import random


# Directory containing 23andMe files
snp_directory = "data/23andme_files"

# Path to phenotype file
phenotype_file = "data/phenotype_file.csv"

# Load phenotype data
phenotype_data = pd.read_csv(phenotype_file)

# # First, create a dict and loop through the files, we only want SNPs that are present in at least 2 of the files (key: SNP, val: count)
snp_freq_dict = {}

i = 1
for dir in os.listdir(snp_directory):
    for file in os.listdir(os.path.join(snp_directory, dir)):

        try:
            print(f"Processing file {file}...")
            i += 1
            file_path = os.path.join(snp_directory, dir, file)
            snp_data = pd.read_csv(file_path, sep='\t', comment='#', header=None, names=['rsid', 'chromosome', 'position', 'genotype'], encoding='utf-8', dtype={'chromosome': str})
            
            for rsid in snp_data['rsid']:
                if rsid in snp_freq_dict:
                    snp_freq_dict[rsid] += 1
                else:
                    snp_freq_dict[rsid] = 1
        except Exception as e:
            print(f"Error processing {file}: {e}")

snp_set = {rsid for rsid, count in snp_freq_dict.items() if count >= 4}

combined_data = {}

OPN1LW_locations = [154144243,154159032]
OPN1MW_locations = [154182596,154196861]

def include_snp(rsid, position):
    if rsid in snp_set:
        if position >= OPN1LW_locations[0] and position <= OPN1LW_locations[1]:
            return True
        if position >= OPN1MW_locations[0] and position <= OPN1MW_locations[1]:
            return True
            
    return False


# Process each 23andMe file in the directory
for dir in os.listdir(snp_directory):
    for file in os.listdir(os.path.join(snp_directory, dir)):

        try:
            print(f"Processing {file}...")
            individual_id = os.path.splitext(file)[0]  # Extract individual ID from filename
            file_path = os.path.join(snp_directory, dir, file)
            
            # Load the SNP data, skipping comment lines
            snp_data = pd.read_csv(file_path, sep='\t', comment='#', header=None, names=['rsid', 'chromosome', 'position', 'genotype'], encoding='utf-8', dtype={'chromosome': str})
            
            # Add rsid as key with presence (1) for the individual if it is in the snp_set
            combined_data[individual_id] = {}
            my_iter = 0

            snp_data = snp_data[snp_data['chromosome'] == 'X']
            
            for index, row in snp_data.iterrows():
                rsid = row['rsid']
                position = row['position']
                if include_snp(rsid, position):
                    combined_data[individual_id][rsid] = 1

            if dir == "control":
                combined_data[individual_id]['color-blind'] = 0
                combined_data[individual_id]['normal-vision'] = 1
            elif dir == "red-green":
                combined_data[individual_id]['color-blind'] = 1
                combined_data[individual_id]['normal-vision'] = 0

        except Exception as e:
            print(f"Error processing {file}: {e}")
       

# Create a DataFrame from the combined SNP data
snp_df = pd.DataFrame.from_dict(combined_data, orient='index').fillna(0)  # Fill missing SNPs with 0

# Get shape of the SNP DataFrame
print(snp_df.shape)

# Add phenotype data
# Ensure the individual IDs in phenotype_data match the 23andMe file names
phenotype_data.set_index('individual_id', inplace=True)
print(phenotype_data.columns)

# Combine SNP data with phenotype data
# combined_df = snp_df.join(phenotype_data, how='inner')  # Join on individual ID (index)

# Save the combined dataset to a CSV file
output_path = "full_combined_23andme_binary_with_phenotypes.csv"
snp_df.to_csv(output_path)

# Display the combined dataset (optional)
print(snp_df.head())
