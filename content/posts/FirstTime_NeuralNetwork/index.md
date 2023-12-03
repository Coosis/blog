---
title: "First-Time: Neural Network(overview)"
date: 2023-12-03T09:37:35+08:00
draft: false
tags: ["Machine Learning", "Neural Network"]
---

# Before Everything Else:
So one day, out of no where, I got thinking: How does a language model generate texts? I searched, and found a [neural network course](https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ) by [Andrej Karpathy](https://karpathy.ai/). Immediately I dived in.

# Structure/History:
The different stages of neural networks are the following:
Bigram (one character predicts the next one with a lookup table of counts)
MLP, following [Bengio et al. 2003](https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf)
CNN, following [DeepMind WaveNet 2016](https://arxiv.org/abs/1609.03499)
RNN, following [Mikolov et al. 2010](https://www.fit.vutbr.cz/research/groups/speech/publi/2010/mikolov_interspeech2010_IS100722.pdf)
LSTM, following [Graves et al. 2014](https://arxiv.org/abs/1308.0850)
GRU, following [Kyunghyun Cho et al. 2014](https://arxiv.org/abs/1409.1259)
Transformer, following [Vaswani et al. 2017](https://arxiv.org/abs/1706.03762)

The series mainly focused on Bigram models and MLP, and modern Transformers.

# Brief Summary:
A neural network first tokenizes inputs - transform inputs into tokens that the machine can understand. Then, it feed these tokens into its layers, in which mathematical functions are applied, then onto the next. During training, the results produced are evaluated using a loss function, and we backward on the loss function to get the gradiants of each individual parameters, and update each of them such that the loss function's value can be decreased accordingly.

# What I did:
I followed the series and build a clone of the makemore neural network by [Andrej Karpathy](https://karpathy.ai/). A lot of the other concepts I still find puzzling, but I will get to the end of them.