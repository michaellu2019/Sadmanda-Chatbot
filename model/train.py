# code reference https://blog.tensorflow.org/2019/05/transformer-chatbot-tutorial-with-tensorflow-2.html
import tensorflow as tf
from transformer import transformer
from data_preprocessor import filter_line, build_word_matrix_row, load_data, load_movie_data
import os

class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
	def __init__(self, d_model, warmup_steps = 4000):
		super(CustomSchedule, self).__init__()

		self.d_model = d_model
		self.d_model = tf.cast(self.d_model, dtype = tf.float32)
		self.warmup_steps = warmup_steps

	def __call__(self, step):
		arg1 = tf.math.rsqrt(step)
		arg2 = step * (self.warmup_steps**-1.5)

		return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)

def loss_function(y_true, y_pred):
	y_true = tf.reshape(y_true, shape = (-1, limits['max_a_len'] + 1))
	loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits = True, reduction = 'none')(y_true, y_pred)
	mask = tf.cast(tf.not_equal(y_true, 0), dtype = tf.float32)
	loss = tf.multiply(loss, mask)

	return tf.reduce_mean(loss)

def accuracy(y_true, y_pred):
	y_true = tf.reshape(y_true, shape = (-1, limits['max_a_len'] + 1))
	return tf.keras.metrics.sparse_categorical_accuracy(y_true, y_pred)

def evaluate(sentence):
	sentence = filter_line(sentence)
	sentence = tf.expand_dims(build_word_matrix_row(sentence, metadata['word_to_idx'], limits['max_q_len']), axis = 0)
	output = tf.expand_dims(start_token, 0)

	for i in range(limits['max_a_len']):
		predictions = model(inputs = [sentence, output], training = False)

		predictions = predictions[:, -1:, :]
		predicted_id = tf.cast(tf.argmax(predictions, axis = -1), dtype = tf.int32)

		if tf.equal(predicted_id, end_token[0]):
			break

		output = tf.concat([output, predicted_id], axis = -1)

	return tf.squeeze(output, axis = 0)

def predict(sentence):
	prediction = evaluate(sentence)
	predicted_sentence = ' '.join([metadata['idx_to_word'][i] for i in prediction[1:]])
	return predicted_sentence

def train_model(dataset, epochs = 10):
	checkpoint_path = 'training_checkpoints/cp.ckpt'
	checkpoint_dir = os.path.dirname(checkpoint_path)
	cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath = checkpoint_path, save_weights_only = True, verbose = 1)

	model.fit(dataset, epochs = epochs, callbacks = [cp_callback])

def load_model():
	model.load_weights('training_checkpoints/cp.ckpt')

metadata, questions, answers = load_data(path = 'metadata/')
# metadata, questions, answers = load_movie_data(path = 'metadata/')

batch_size = 64
buffer_size = 20000
vocab_size = 6000
start_token = [vocab_size]
end_token = [vocab_size + 1]
vocab_size += 2
limits = metadata['limits']

num_layers = 2
d_model = 256
num_heads = 8
units = 512
dropout = 0.1
# epochs = 50

dataset = tf.data.Dataset.from_tensor_slices((
	{
		'inputs': questions,
		'dec_inputs': answers[:, :-1]
	},
	{
		'outputs': answers[:, 1:]
	}
))

dataset = dataset.cache()
dataset = dataset.shuffle(buffer_size)
dataset = dataset.batch(batch_size)
dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)

tf.keras.backend.clear_session()
model = transformer(vocab_size = vocab_size + 2, num_layers = num_layers, units = units, d_model = d_model, num_heads = num_heads, dropout = dropout)

learning_rate = CustomSchedule(d_model = d_model)
optimizer = tf.keras.optimizers.Adam(learning_rate, beta_1 = 0.9, beta_2 = 0.98, epsilon = 1e-9)

model.compile(optimizer = optimizer, loss = loss_function, metrics = [accuracy])

# train_model(dataset, epochs = 1)