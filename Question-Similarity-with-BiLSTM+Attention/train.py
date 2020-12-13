from time import time
import pandas as pd
from sklearn.model_selection import train_test_split
import keras
from gensim.models import KeyedVectors
from keras.models import Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Input, Embedding, LSTM, Dense, Flatten, Activation, RepeatVector, Permute, Lambda, \
	Bidirectional, TimeDistributed, Dropout, Conv1D, GlobalMaxPool1D
from keras.layers.merge import multiply, concatenate
import keras.backend as K
from util import make_w2v_embeddings, split_and_zero_padding, ManDist



TRAIN_CSV = './data/train.csv'
flag = 'en'
embedding_path = 'GoogleNews-vectors-negative300.bin.gz'
embedding_dim = 300
max_seq_length = 10
savepath = './data/SiameseLSTM.h5'

print("Loading word2vec model, may takes 2-3 minutes...")
embedding_dict = KeyedVectors.load_word2vec_format(embedding_path, binary=True)


train_df = pd.read_csv(TRAIN_CSV, encoding = 'gb18030')
for q in ['question1', 'question2']:
	train_df[q + '_n'] = train_df[q]

train_df, embeddings = make_w2v_embeddings(embedding_dict, train_df, embedding_dim=embedding_dim)

X = train_df[['question1_n', 'question2_n']]
Y = train_df['is_duplicate']
X_train, X_validation, Y_train, Y_validation = train_test_split(X, Y, test_size=0.2, random_state=42)
X_train = split_and_zero_padding(X_train, max_seq_length)
X_validation = split_and_zero_padding(X_validation, max_seq_length)

Y_train = Y_train.values
Y_validation = Y_validation.values

assert X_train['left'].shape == X_train['right'].shape
assert len(X_train['left']) == len(Y_train)


def shared_model(_input):
	embedded = Embedding(len(embeddings), embedding_dim, weights=[embeddings], input_shape=(max_seq_length,),
						 trainable=False)(_input)

	# Bi-LSTM
	activations = Bidirectional(LSTM(n_hidden, return_sequences=True), merge_mode='concat')(embedded)
	activations = Bidirectional(LSTM(n_hidden, return_sequences=True), merge_mode='concat')(activations)

	# dropout
	activations = Dropout(0.5)(activations)

	# Attention
	attention = TimeDistributed(Dense(1, activation='tanh'))(activations)
	attention = Flatten()(attention)
	attention = Activation('softmax')(attention)
	attention = RepeatVector(n_hidden * 2)(attention)
	attention = Permute([2, 1])(attention)
	sent_representation = multiply([activations, attention])
	sent_representation = Lambda(lambda x_lambda: K.sum(x_lambda, axis=1))(sent_representation)

	# dropout
	sent_representation = Dropout(0.1)(sent_representation)

	return sent_representation


if __name__ == '__main__':

	batch_size = 1024
	n_epoch = 50
	n_hidden = 50

	left_input = Input(shape=(max_seq_length,), dtype='float32')
	right_input = Input(shape=(max_seq_length,), dtype='float32')
	left_sen_representation = shared_model(left_input)
	right_sen_representation = shared_model(right_input)


	man_distance = ManDist()([left_sen_representation, right_sen_representation])
	sen_representation = concatenate([left_sen_representation, right_sen_representation, man_distance])
	similarity = Dense(1, activation='sigmoid')(Dense(2)(Dense(4)(Dense(16)(sen_representation))))
	model = Model(inputs=[left_input, right_input], outputs=[similarity])

	model.compile(loss='mean_squared_error', optimizer=keras.optimizers.Adam(), metrics=['accuracy'])
	model.summary()
	#earlyStopping = EarlyStopping(monitor='val_accuracy', patience=10, verbose=0, mode='min')
	mcp_save = ModelCheckpoint('./data/intermediate_model.h5', save_best_only=True, monitor='val_accuracy', mode='max')


	training_start_time = time()
	malstm_trained = model.fit([X_train['left'], X_train['right']], Y_train,
							   batch_size=batch_size, epochs=n_epoch,
							   validation_data=([X_validation['left'], X_validation['right']], Y_validation),
							   callbacks=[mcp_save])
	training_end_time = time()
	print("Training time finished.\nCompleted %d epochs in %0.2f seconds." % (n_epoch, training_end_time - training_start_time))

	# Plot accuracy
	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt

	plt.subplot(211)
	plt.plot(malstm_trained.history['accuracy'])
	plt.plot(malstm_trained.history['val_accuracy'])
	plt.title('Model Accuracy')
	plt.ylabel('Accuracy')
	plt.xlabel('Epoch')
	plt.legend(['Train', 'Validation'], loc='upper left')

	# Plot loss
	plt.subplot(212)
	plt.plot(malstm_trained.history['loss'])
	plt.plot(malstm_trained.history['val_loss'])
	plt.title('Model Loss')
	plt.ylabel('Loss')
	plt.xlabel('Epoch')
	plt.legend(['Train', 'Validation'], loc='upper right')

	plt.tight_layout(h_pad=1.0)
	plt.savefig('./data/history-graph.png')

	model.save(savepath)
	print(str(malstm_trained.history['val_accuracy'][-1])[:6] +
		  "(max: " + str(max(malstm_trained.history['val_accuracy']))[:6] + ")")
	print("Done.")
