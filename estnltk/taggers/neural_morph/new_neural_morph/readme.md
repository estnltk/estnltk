# Neural morphological tagger

* This directory contains 4 different neural models for morphological tagging, which are located in directories softmax_emb_tag_sum,
softmax_emb_cat_sum, seq2seq_emb_tag_sum and seq2seq_emb_cat_sum. All four models were trained by Kermo Saarse and Kairit Sirts in 
June-August 2019 using High Performance Cluster in Univerity of Tartu.
* Each one of these directories contains files model.py, config.py, config_holder.py and a directory named output, which contains
model weights and data.
* Neural morphological tagging is performed by the class NeuralMorphTagger in neural_morph_tagger, which uses these models. It also
needs helper methods defined in vabamorf_2_neural.py and neural_2_vabamorf.py.
