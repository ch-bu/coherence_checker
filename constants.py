# coding: utf8

import os

# File_path
file_path = os.path.dirname(os.path.realpath(__file__))

# RFTagger variables
tokenizer = file_path + "/RFTagger/cmd/tokenize.perl"
rftagger = file_path + "/RFTagger/bin/rft-annotate"
german_par = file_path + "/RFTagger/lib/german-utf8.par"

# Temporary files
temp_text = file_path + "/temp/text.txt"
temp_tokens = file_path + "/temp/tokens.txt"
temp_tags = file_path + "/temp/tags.txt"
temp_dir = file_path + "/temp"