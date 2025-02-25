#Code by Joseph Capdevielle

import os
import numpy as np

from math import log2
from collections import Counter

import pefile

import pickle
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import StandardScaler

#gzip entropy method (not sure whether return type is the same so not using)
#import gzip
#import shutil


def extract(path_to_file, datapath):

	#Get Length
	length = os.path.getsize(path_to_file)

	#----------------------
	#with open(path_to_file, 'rb') as infile:
		#with gzip.open(temp_outfile_path, 'wb') as zipfile:
			#shutil.copyfileobj(infile, zipfile)
	#infile.close()
	#zipfile.close()
	#zipsize = os.path.getsize(temp_outfile_path)
	#entropy = zipsize / filesize #proportion of nonredundant material in file (tracks entropy)
	#----------------------

	#Calculate Entropy
	f = open(path_to_file, 'rb')
	s = f.read()
	f.close()

	p, lns = Counter(s), float(len(s))

	entropy = log2(lns) - sum(count * log2(count) for count in p.values()) / lns

	#Put Entropy and Length together in numpy data structure
	entropy_length = np.vstack((entropy, length))
	

	##Get API Calls

	#Load trained API calls
	trained_calls_file = open(datapath+"\\pickles\\unique_calls.pickle", 'rb')
	trained_calls = pickle.load(trained_calls_file)
	trained_calls_file.close()

	API_calls = list()
	try:
		in_PE = pefile.PE(path_to_file,fast_load=True)
		if in_PE.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']].VirtualAddress != 0:
			in_PE.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
			try:
				for entry in in_PE.DIRECTORY_ENTRY_IMPORT:
					for API in entry.imports:
						string = API.name.decode('utf8')
						if string in trained_calls:
							API_calls.append(string)
							#print("Call recognized: %s" % string)
						else:
							#print("Skipping unknown call: %s" % string)
							pass
			except AttributeError:
				pass        
		else: 
			pass
	except pefile.PEFormatError as e:
		pass
	print(len(API_calls))
	#Represent API calls
	mlb_file = open("pickles/mlb_v2.pickle", 'rb')
	mlb = pickle.load(mlb_file)
	mlb_file.close()
	#mlb = MultiLabelBinarizer()
	#trainer = mlb.fit_transform(list(trained_calls)+API_calls)
	api_vector = mlb.transform([API_calls])
	#Put into np array
	api_vector_encoded = np.array(api_vector)
	print(api_vector_encoded.shape)
	sample = np.concatenate((entropy_length.T, api_vector_encoded), axis=1)
	scaler_file = open("pickles/scaler.pickle", 'rb')
	scaler = pickle.load(scaler_file)
	scaler_file.close()
	sample_scaled = scaler.transform(sample)
	return sample_scaled, API_calls