# -*- coding: utf-8 -*-
import numpy as np
"""
This file defines layer types that are commonly used for recurrent neural
networks.
"""
def rnn_step_forward(x, prev_h, Wx, Wh, b):
  """
  Run the forward pass for a single timestep of a vanilla RNN that uses a tanh
  activation function.
  The input data has dimension D, the hidden state has dimension H, and we use
  a minibatch size of N.
  Inputs:
  - x: Input data for this timestep, of shape (N, D).
  - prev_h: Hidden state from previous timestep, of shape (N, H)
  - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
  - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
  - b: Biases of shape (H,)
  Returns a tuple of:
  - next_h: Next hidden state, of shape (N, H)
  - cache: Tuple of values needed for the backward pass.  """
  # TODO: Implement a single forward step for the vanilla RNN. Store the next  #
  # hidden state and any values you need for the backward pass in the next_h   #
  # and cache variables respectively.                                          #
  next_h = np.tanh(x.dot(Wx) + prev_h.dot(Wh) + b)
  cache = (x, prev_h, Wx, Wh, next_h)
  return next_h, cache

def rnn_step_backward(dnext_h, cache):
  """
  Backward pass for a single timestep of a vanilla RNN.
  Inputs:
  - dnext_h: Gradient of loss with respect to next hidden state
  - cache: Cache object from the forward pass
  Returns a tuple of:
  - dx: Gradients of input data, of shape (N, D)
  - dprev_h: Gradients of previous hidden state, of shape (N, H)
  - dWx: Gradients of input-to-hidden weights, of shape (N, H)
  - dWh: Gradients of hidden-to-hidden weights, of shape (H, H)
  - db: Gradients of bias vector, of shape (H,) """
  # TODO: Implement the backward pass for a single step of a vanilla RNN.      #
  # HINT: For the tanh function, you can compute the local derivative in terms #
  # of the output value from tanh.                                             #
  x, prev_h, Wx, Wh, next_h = cache
  dh = dnext_h * (1 - next_h**2)
  db = np.sum(dh, 0)
  dWh = np.dot(prev_h.T, dh)
  dWx = np.dot(x.T, dh)
  dprev_h = dh.dot(Wh.T)
  dx = dh.dot(Wx.T)
  return dx, dprev_h, dWx, dWh, db


def rnn_forward(x, h0, Wx, Wh, b):
  """
  Run a vanilla RNN forward on an entire sequence of data. We assume an input
  sequence composed of T vectors, each of dimension D. The RNN uses a hidden
  size of H, and we work over a minibatch containing N sequences. After running
  the RNN forward, we return the hidden states for all timesteps.
  Inputs:
  - x: Input data for the entire timeseries, of shape (N, T, D).
  - h0: Initial hidden state, of shape (N, H)
  - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
  - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
  - b: Biases of shape (H,)
  
  Returns a tuple of:
  - h: Hidden states for the entire timeseries, of shape (N, T, H).
  - cache: Values needed in the backward pass  """
  # TODO: Implement forward pass for a vanilla RNN running on a sequence of    #
  # input data. You should use the rnn_step_forward function that you defined  #
  # above.                                                                     #
  N, T, D = x.shape
  H = len(b)
  h, cache = np.zeros([N, T, H]), []
  for i in xrange(T):
    h0, c = rnn_step_forward(x[:,i,:], h0, Wx, Wh, b)
    h[:,i,:] = h0
    cache.append(c)
  return h, cache


def rnn_backward(dh, cache):
  """
  Compute the backward pass for a vanilla RNN over an entire sequence of data.
  Inputs:
  - dh: Upstream gradients of all hidden states, of shape (N, T, H)
  Returns a tuple of:
  - dx: Gradient of inputs, of shape (N, T, D)
  - dh0: Gradient of initial hidden state, of shape (N, H)
  - dWx: Gradient of input-to-hidden weights, of shape (D, H)
  - dWh: Gradient of hidden-to-hidden weights, of shape (H, H)
  - db: Gradient of biases, of shape (H,) """
  # TODO: Implement the backward pass for a vanilla RNN running an entire      #
  # sequence of data. You should use the rnn_step_backward function that you   #
  # defined above.                                                             #
  N, T, H = dh.shape
  D = cache[0][0].shape[1]
  dx, dh0 = np.zeros([N, T, D]), np.zeros([N, H])
  dWx, dWh, db = np.zeros([T, D, H]), np.zeros([T, H, H]), np.zeros([T, H])
  for i in xrange(T - 1, -1, -1):
    dx[:,i,:], dh0, dWx[i], dWh[i], db[i] = rnn_step_backward(dh[:,i,:] + dh0, cache.pop())
  dWx, dWh, db = np.sum(dWx, 0), np.sum(dWh, 0), np.sum(db, 0)
  return dx, dh0, dWx, dWh, db


def word_embedding_forward(x, W):
  """
  Forward pass for word embeddings. We operate on minibatches of size N where
  each sequence has length T. We assume a vocabulary of V words, assigning each
  to a vector of dimension D.
  Inputs:
  - x: Integer array of shape (N, T) giving indices of words. Each element idx
    of x muxt be in the range 0 <= idx < V.
  - W: Weight matrix of shape (V, D) giving word vectors for all words.
  Returns a tuple of:
  - out: Array of shape (N, T, D) giving word vectors for all input words.
  - cache: Values needed for the backward pass  """
  # TODO: Implement the forward pass for word embeddings.                      #
  # HINT: This should be very simple.                                          #
  N, T = x.shape
  V, D = W.shape
  out = np.zeros((N, T, D))
  for n in xrange(N):
    for t in xrange(T):
      out[n, t, :] = W[x[n, t], :]
  cache = (x, W)
  return out, cache

def word_embedding_backward(dout, cache):
  """
  Backward pass for word embeddings. We cannot back-propagate into the words
  since they are integers, so we only return gradient for the word embedding
  matrix.
  Inputs:
  - dout: Upstream gradients of shape (N, T, D)
  - cache: Values from the forward pass
  Returns:
  - dW: Gradient of word embedding matrix, of shape (V, D).  """
  # TODO: Implement the backward pass for word embeddings.                     #
  # HINT: Look up the function np.add.at                                       #
  x, W = cache
  N, T, _ = dout.shape
  dW = np.zeros_like(W)
  for n in xrange(N):
    for t in xrange(T):
      dW[x[n,t], :] += dout[n, t, :]
  return dW


def sigmoid(x):
  """
  A numerically stable version of the logistic sigmoid function.
  """
  pos_mask = (x >= 0)
  neg_mask = (x < 0)
  z = np.zeros_like(x)
  z[pos_mask] = np.exp(-x[pos_mask])
  z[neg_mask] = np.exp(x[neg_mask])
  top = np.ones_like(x)
  top[neg_mask] = z[neg_mask]
  return top / (1 + z)


def lstm_step_forward(x, prev_h, prev_c, Wx, Wh, b):
  """
  Forward pass for a single timestep of an LSTM.
  The input data has dimension D, the hidden state has dimension H, and we use
  a minibatch size of N.
  Inputs:
  - x: Input data, of shape (N, D)
  - prev_h: Previous hidden state, of shape (N, H)
  - prev_c: previous cell state, of shape (N, H)
  - Wx: Input-to-hidden weights, of shape (D, 4H)
  - Wh: Hidden-to-hidden weights, of shape (H, 4H)
  - b: Biases, of shape (4H,)
  Returns a tuple of:
  - next_h: Next hidden state, of shape (N, H)
  - next_c: Next cell state, of shape (N, H)
  - cache: Tuple of values needed for backward pass.  """
  # TODO: Implement the forward pass for a single timestep of an LSTM.        #
  # You may want to use the numerically stable sigmoid implementation above.  #
  N, H = prev_c.shape
  a = x.dot(Wx) + prev_h.dot(Wh) + b          # [N, 4H]
  ai, af, ao, ag = a[:, 0:H], a[:, H:2 * H], a[:, 2 * H:3 * H], a[:, 3 * H:]
  i, f, o, g = sigmoid(ai), sigmoid(af), sigmoid(ao), np.tanh(ag)
  next_c = f * prev_c + i * g                 # [N, H]
  tnc = np.tanh(next_c)
  next_h = o * tnc
  cache = (x, prev_h, prev_c, Wx, Wh, i, f, o, g, tnc)
  return next_h, next_c, cache

def lstm_step_backward(dnext_h, dnext_c, cache):
  """
  Backward pass for a single timestep of an LSTM.
  Inputs:
  - dnext_h: Gradients of next hidden state, of shape (N, H)
  - dnext_c: Gradients of next cell state, of shape (N, H)
  - cache: Values from the forward pass
  Returns a tuple of:
  - dx: Gradient of input data, of shape (N, D)
  - dprev_h: Gradient of previous hidden state, of shape (N, H)
  - dprev_c: Gradient of previous cell state, of shape (N, H)
  - dWx: Gradient of input-to-hidden weights, of shape (D, 4H)
  - dWh: Gradient of hidden-to-hidden weights, of shape (H, 4H)
  - db: Gradient of biases, of shape (4H,)  """
  # TODO: Implement the backward pass for a single timestep of an LSTM.       #
  # HINT: For sigmoid and tanh you can compute local derivatives in terms of  #
  # the output value from the nonlinearity.                                   #
  x, prev_h, prev_c, Wx, Wh, i, f, o, g, tnc = cache
  dtnc = dnext_h * o
  dnext_c += dtnc * (1 - tnc**2)
  do = dnext_h * tnc
  df, dprev_c = dnext_c * prev_c, dnext_c * f
  di, dg = dnext_c * g, dnext_c * i
  dai = di * i * (1 - i)
  daf = df * f * (1 - f)
  dao = do * o * (1 - o)
  dag = dg * (1 - g**2)
  da = np.hstack((dai, daf, dao, dag))
  dx = np.dot(da, Wx.T)
  dprev_h = np.dot(da, Wh.T)
  dWx = np.dot(x.T, da)
  dWh = np.dot(prev_h.T, da)
  db = np.sum(da, 0)
  return dx, dprev_h, dprev_c, dWx, dWh, db


def lstm_forward(x, h0, Wx, Wh, b):
  """
    Forward pass for an LSTM over an entire sequence of data. We assume an input
  sequence composed of T vectors, each of dimension D. The LSTM uses a hidden
  size of H, and we work over a minibatch containing N sequences. After running
    the LSTM forward, we return the hidden states for all timesteps.
  Note that the initial cell state is passed as input, but the initial cell
  state is set to zero. Also note that the cell state is not returned; it is
  an internal variable to the LSTM and is not accessed from outside.
  Inputs:
  - x: Input data of shape (N, T, D)
  - h0: Initial hidden state of shape (N, H)
  - Wx: Weights for input-to-hidden connections, of shape (D, 4H)
  - Wh: Weights for hidden-to-hidden connections, of shape (H, 4H)
  - b: Biases of shape (4H,)
  Returns a tuple of:
  - h: Hidden states for all timesteps of all sequences, of shape (N, T, H)
  - cache: Values needed for the backward pass.  """
  # TODO: Implement the forward pass for an LSTM over an entire timeseries.   #
  # You should use the lstm_step_forward function that you just defined.      #
  N, T, D = x.shape
  H = h0.shape[1]
  h, c, cache = np.zeros([N, T, H]), np.zeros([N, H]), []
  for i in xrange(T):
    h0, c, ca = lstm_step_forward(x[:,i,:], h0, c, Wx, Wh, b)
    h[:,i,:] = h0
    cache.append(ca)
  return h, cache

def lstm_backward(dh, cache):
  """
  Backward pass for an LSTM over an entire sequence of data.]
  Inputs:
  - dh: Upstream gradients of hidden states, of shape (N, T, H)
  - cache: Values from the forward pass
  Returns a tuple of:
  - dx: Gradient of input data of shape (N, T, D)
  - dh0: Gradient of initial hidden state of shape (N, H)
  - dWx: Gradient of input-to-hidden weight matrix of shape (D, 4H)
  - dWh: Gradient of hidden-to-hidden weight matrix of shape (H, 4H)
  - db: Gradient of biases, of shape (4H,)  """
  dx, dh0, dWx, dWh, db = None, None, None, None, None
  # TODO: Implement the backward pass for an LSTM over an entire timeseries.  #
  # You should use the lstm_step_backward function that you just defined.     #
  N, T, H = dh.shape
  HH = 4 * H
  D = cache[0][0].shape[1]
  dx, dh0 = np.zeros([N, T, D]), np.zeros([N, H])
  dprev_c = dh0
  dWx, dWh, db = np.zeros([T, D, HH]), np.zeros([T, H, HH]), np.zeros([T, HH])
  for i in xrange(T - 1, -1, -1):
    dprev_h = dh[:,i,:] + dh0
    dx[:,i,:], dh0, dprev_c, dWx[i], dWh[i], db[i] = lstm_step_backward(dprev_h, dprev_c, cache.pop())
  dWx, dWh, db = np.sum(dWx, 0), np.sum(dWh, 0), np.sum(db, 0)
  
  return dx, dh0, dWx, dWh, db


def temporal_affine_forward(x, w, b):
  """
  Forward pass for a temporal affine layer. The input is a set of D-dimensional
  vectors arranged into a minibatch of N timeseries, each of length T. We use
  an affine function to transform each of those vectors into a new vector of
  dimension M.
  Inputs:
  - x: Input data of shape (N, T, D)
  - w: Weights of shape (D, M)
  - b: Biases of shape (M,)
  Returns a tuple of:
  - out: Output data of shape (N, T, M)
  - cache: Values needed for the backward pass """
  N, T, D = x.shape
  M = b.shape[0]
  out = x.reshape(N * T, D).dot(w).reshape(N, T, M) + b
  cache = x, w, b, out
  return out, cache


def temporal_affine_backward(dout, cache):
  """
  Backward pass for temporal affine layer.
  Input:
  - dout: Upstream gradients of shape (N, T, M)
  - cache: Values from forward pass
  Returns a tuple of:
  - dx: Gradient of input, of shape (N, T, D)
  - dw: Gradient of weights, of shape (D, M)
  - db: Gradient of biases, of shape (M,) """
  x, w, b, _ = cache
  N, T, D = x.shape
  M = b.shape[0]
  dx = dout.reshape(N * T, M).dot(w.T).reshape(N, T, D)
  dw = dout.reshape(N * T, M).T.dot(x.reshape(N * T, D)).T
  db = dout.sum(axis=(0, 1))
  return dx, dw, db


def temporal_softmax_loss(x, y, mask, verbose=False):
  """
  A temporal version of softmax loss for use in RNNs. We assume that we are
  making predictions over a vocabulary of size V for each timestep of a
  timeseries of length T, over a minibatch of size N. The input x gives scores
  for all vocabulary elements at all timesteps, and y gives the indices of the
  ground-truth element at each timestep. We use a cross-entropy loss at each
  timestep, summing the loss over all timesteps and averaging across the
  minibatch.

  As an additional complication, we may want to ignore the model output at some
  timesteps, since sequences of different length may have been combined into a
  minibatch and padded with NULL tokens. The optional mask argument tells us
  which elements should contribute to the loss.

  Inputs:
  - x: Input scores, of shape (N, T, V)
  - y: Ground-truth indices, of shape (N, T) where each element is in the range
       0 <= y[i, t] < V
  - mask: Boolean array of shape (N, T) where mask[i, t] tells whether or not
    the scores at x[i, t] should contribute to the loss.

  Returns a tuple of:
  - loss: Scalar giving loss
  - dx: Gradient of loss with respect to scores x.
  """

  N, T, V = x.shape
  
  x_flat = x.reshape(N * T, V)
  y_flat = y.reshape(N * T)
  mask_flat = mask.reshape(N * T)
  
  probs = np.exp(x_flat - np.max(x_flat, axis=1, keepdims=True))
  probs /= np.sum(probs, axis=1, keepdims=True)
  loss = -np.sum(mask_flat * np.log(probs[np.arange(N * T), y_flat])) / N
  dx_flat = probs.copy()
  dx_flat[np.arange(N * T), y_flat] -= 1
  dx_flat /= N
  dx_flat *= mask_flat[:, None]
  
  if verbose: print 'dx_flat: ', dx_flat.shape
  
  dx = dx_flat.reshape(N, T, V)
  
  return loss, dx

