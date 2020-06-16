# most code copied from https://github.com/suriyadeepan/datasets/blob/master/seq2seq/twitter/data.py
import random
import sys
import nltk
import itertools
from collections import defaultdict
import numpy as np
import pickle
import json
import re

# word limits for questions and answers
limits = {
	'max_q_len': 50,
	'min_q_len': 1,
	'max_a_len': 50,
	'min_a_len': 1
}

vocab_size = 6000
start_token = [vocab_size]
end_token = [vocab_size + 1]

def filter_line(line):
	# return ''.join([ch for ch in line if ch in whitelisted_chars])
	line = line.lower().strip()
	line = re.sub(r"([?.!,])", r" \1 ", line)
	line = re.sub(r'[" "]+', " ", line)
	line = re.sub(r"[^a-zA-Z?.!,]+", " ", line)
	line = line.strip()

	return line

# build a dictionary that maps unique words found in the data to an index, an array of unique words, and a frequency distribution, which is an array of tuples of a word and its frequency
def make_word_dicts(tokenized_sentences, vocab_size):
	freq_dist = nltk.FreqDist(itertools.chain(*tokenized_sentences))
	vocab = freq_dist.most_common(vocab_size - 2)
	idx_to_word = [word[0] for word in vocab]
	word_to_idx = dict([(word, i) for i, word in enumerate(idx_to_word)])

	return idx_to_word, word_to_idx, freq_dist

# build an array of questions and answers that fall within the specified word limits
def filter_data(sequences):
	filtered_q = []
	filtered_a = []
	raw_data_len = len(sequences)//2

	for i in range(0, len(sequences), 2):
		q_num_words = len(sequences[i].split(' '))
		a_num_words = len(sequences[i + 1].split(' '))

		if q_num_words >= limits['min_q_len'] and q_num_words <= limits['max_q_len'] and a_num_words >= limits['min_a_len'] and a_num_words <= limits['max_a_len']:
			filtered_q.append(sequences[i])
			filtered_a.append(sequences[i + 1])

	filtered_pct = int((len(filtered_q)/(len(sequences)//2)) * 100)
	print(str(filtered_pct) + '% content kept from original data...', len(filtered_q), 'exchanges kept among', len(sequences)//2, 'total exchanges...')

	return filtered_q, filtered_a

# create one row of a word matrix populated with the indices of words in the word dictionary
def build_word_matrix_row(sequence, word_to_idx, max_len):
	indices = []
	for word in sequence:
		if word in word_to_idx:
			indices.append(word_to_idx[word])

	return start_token + indices + end_token + [0] * (max_len - len(indices))

# create a word matrix of word indices for questions and answers where each row is a question or answer
def build_word_matrix(tokenized_q, tokenized_a, word_to_idx):
	data_len = len(tokenized_q)

	qidx = np.zeros([data_len, limits['max_q_len'] + 2], dtype = np.int32)
	aidx = np.zeros([data_len, limits['max_a_len'] + 2], dtype = np.int32)

	for i in range(data_len):
		q_indices = build_word_matrix_row(tokenized_q[i], word_to_idx, limits['max_q_len'])
		a_indices = build_word_matrix_row(tokenized_a[i], word_to_idx, limits['max_a_len'])

		qidx[i] = np.array(q_indices)
		aidx[i] = np.array(a_indices)

	return qidx, aidx

# load data and create metadata to feed into the neural network
def process_data():
	# load data and put all exchanges in one array
	print('Processing data...')
	print('Loading data...')
	with open('chopped_conversations.json') as json_file:
		conversations = json.load(json_file)['conversations']

	lines = []

	for conversation in conversations:
		for msg_obj in conversation:
			# lines.append(filter_line(msg_obj['msg'].lower(), whitelisted_chars))
			lines.append(filter_line(msg_obj['msg']))

	# split exchanges into tokenized list quesions and answers 
	q_lines, a_lines = filter_data(lines)
	tokenized_q = [q_line.split(' ') for q_line in q_lines]
	tokenized_a = [a_line.split(' ') for a_line in a_lines]

	# create metadata for neural network and save values
	print('Creating metadata...')

	idx_to_word, word_to_idx, freq_dist = make_word_dicts(tokenized_q + tokenized_a, vocab_size + 2)
	qidx, aidx = build_word_matrix(tokenized_q, tokenized_a, word_to_idx)

	np.save('../metadata/qidx.npy', qidx)
	np.save('../metadata/aidx.npy', aidx)

	metadata = {
		'word_to_idx': word_to_idx,
		'idx_to_word': idx_to_word,
		'limits': limits,
		'freq_dist': freq_dist
	}

	print('Saving data in pickle file...')
	with open('../metadata/metadata.pkl', 'wb') as pkl_file:
		pickle.dump(metadata, pkl_file)

# load data and create metadata for the Cornell movie conversations corpus
def process_movie_data():
	# load data and put all exchanges in one array
	print('Processing data...')
	print('Loading data...')
	with open('movie_conversations.json') as json_file:
		conversations = json.load(json_file)['conversations']

	lines = []

	for conversation in conversations:
		for msg_obj in conversation:
			# lines.append(filter_line(msg_obj['msg'].lower(), whitelisted_chars))
			lines.append(filter_line(msg_obj['msg']))

	# split exchanges into tokenized list quesions and answers 
	q_lines, a_lines = filter_data(lines)
	tokenized_q = [q_line.split(' ') for q_line in q_lines]
	tokenized_a = [a_line.split(' ') for a_line in a_lines]

	# create metadata for neural network and save values
	print('Creating metadata...')

	idx_to_word, word_to_idx, freq_dist = make_word_dicts(tokenized_q + tokenized_a, vocab_size + 2)
	qidx, aidx = build_word_matrix(tokenized_q, tokenized_a, word_to_idx)

	np.save('../metadata/m_qidx.npy', qidx)
	np.save('../metadata/m_aidx.npy', aidx)

	metadata = {
		'word_to_idx': word_to_idx,
		'idx_to_word': idx_to_word,
		'limits': limits,
		'freq_dist': freq_dist
	}

	print('Saving data in pickle file...')
	with open('metadata/m_metadata.pkl', 'wb') as pkl_file:
		pickle.dump(metadata, pkl_file)

# load data from saved files
def load_data(path = ''):
	with open(path + 'metadata.pkl', 'rb') as pkl_file:
		metadata = pickle.load(pkl_file)

	qidx = np.load(path + 'qidx.npy')
	aidx = np.load(path + 'aidx.npy')

	return metadata, qidx, aidx

# load movie data from saved files
def load_movie_data(path = ''):
	with open(path + 'm_metadata.pkl', 'rb') as pkl_file:
		metadata = pickle.load(pkl_file)

	qidx = np.load(path + 'm_qidx.npy')
	aidx = np.load(path + 'm_aidx.npy')

	return metadata, qidx, aidx

if __name__ == '__main__':
	process_data()