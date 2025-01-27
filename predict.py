
from utils import *
# from optparse import OptionParser
import pandas as pd
import torch
import math
import argparse

col = ['E. coli ATCC11775', 'P. aeruginosa PAO1', 'P. aeruginosa PA14', 'S. aureus ATCC12600', 'E. coli AIG221',
       'E. coli AIG222', 'K. pneumoniae ATCC13883', 'A. baumannii ATCC19606', 'A. muciniphila ATCC BAA-835',
       'B. fragilis ATCC25285', 'B. vulgatus ATCC8482', 'C. aerofaciens ATCC25986', 'C. scindens ATCC35704',
       'B. thetaiotaomicron ATCC29148', 'B. thetaiotaomicron Complemmented', 'B. thetaiotaomicron Mutant',
       'B. uniformis ATCC8492', 'B. eggerthi ATCC27754', 'C. spiroforme ATCC29900', 'P. distasonis ATCC8503',
       'P. copri DSMZ18205', 'B. ovatus ATCC8483', 'E. rectale ATCC33656', 'C. symbiosum', 'R. obeum', 'R. torques',
       'S. aureus (ATCC BAA-1556) - MRSA', 'vancomycin-resistant E. faecalis ATCC700802',
       'vancomycin-resistant E. faecium ATCC700221', 'E. coli Nissle', 'Salmonella enterica ATCC 9150 (BEIRES NR-515)',
       'Salmonella enterica (BEIRES NR-170)', 'Salmonella enterica ATCC 9150 (BEIRES NR-174)',
       'L. monocytogenes ATCC 19111 (BEIRES NR-106)']
ecoli_cols = ['E. coli ATCC11775', 'E. coli AIG222', 'E. coli AIG221'] # Nissle excluded as non-virulent
saureus_cols = ['S. aureus ATCC12600', 'S. aureus (ATCC BAA-1556) - MRSA']

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', type=str)
    parser.add_argument('output_path', type=str)
    parser.add_argument('benchmark_mode', choices=['min', 'ecoli', 'saureus'])
    args = parser.parse_args()
    input_path = args.input_path
    output_path = args.output_path
    benchmark_mode = args.benchmark_mode




    max_len = 52  # maximun peptide length

    word2idx, idx2word = make_vocab()
    emb, AAindex_dict = AAindex('./aaindex1.csv', word2idx)
    vocab_size = len(word2idx)
    emb_size = np.shape(emb)[1]

    model_num = 8
    repeat_num = 5

    f = open('./best_key_list', 'r')
    lines = f.readlines()
    f.close()

    model_list = []
    for line in lines:
        parsed = line.strip('\n').strip('\r')
        model_list.append(parsed)

    all_list = []
    ensemble_num = model_num * repeat_num

    deep_model_list = []
    for a_model_name in model_list:
        for a_en in range(repeat_num):
            key = 'trained_all_model_' + a_model_name + '_ensemble_' + str(a_en)

            if torch.cuda.is_available():
                model = torch.load('./trained_models/' + key)
            else:
                model = torch.load('./trained_models/' + key, map_location=torch.device('cpu'))
            model.eval()
            deep_model_list.append(model)

    seq_list = []
    f = open(input_path, 'r')
    lines = f.readlines()
    f.close()

    for line in lines:
        seq_list.append(line.strip('\n').strip('\r'))

    seq_list = np.array(seq_list)

    ensemble_counter = 0
    for ensemble_id in range(ensemble_num):

        if torch.cuda.is_available():
            AMP_model = deep_model_list[ensemble_id].cuda().eval()
        else:
            AMP_model = deep_model_list[ensemble_id].eval()

        data_len = len(seq_list)
        batch_size = 3000  # change according to your GPU memory
        for i in range(int(math.ceil(data_len / float(batch_size)))):
            # if (i * batch_size) % 1000 == 0:
            #     print('progress', i * batch_size, data_len)

            seq_batch = seq_list[i * batch_size:(i + 1) * batch_size]
            seq_rep, _, _ = onehot_encoding(seq_batch, max_len, word2idx)

            if torch.cuda.is_available():
                X_seq = torch.LongTensor(seq_rep).cuda()
            else:
                X_seq = torch.LongTensor(seq_rep)

            AMP_pred_batch = AMP_model(X_seq).cpu().detach().numpy()
            AMP_pred_batch = 10 ** (6 - AMP_pred_batch)  # transform back to MICs

            if i == 0:
                AMP_pred = AMP_pred_batch
            else:
                AMP_pred = np.vstack([AMP_pred, AMP_pred_batch])

        if ensemble_id == 0:
            AMP_sum = AMP_pred
        else:
            AMP_sum += AMP_pred
        ensemble_counter += 1

    AMP_pred = AMP_sum / float(ensemble_counter)

    df = pd.DataFrame(data=AMP_pred, columns=col, index=seq_list)

    if benchmark_mode == 'ecoli':
        selected_cols = ecoli_cols
    elif benchmark_mode == 'saureus':
        selected_cols = saureus_cols

    df = df[selected_cols].mean(axis=1).reset_index()
    df.columns = ['Sequence', 'MIC']
    df['MIC_unit'] = 'uM'
    print(df)

    df.to_csv(output_path)
