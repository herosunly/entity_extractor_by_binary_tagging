from utils.logger import get_logger
from configure import Configure
from engines.train import train
from transformers import BertTokenizer, BertModel
from engines.predict import extract_entities
import argparse
import os
import torch


def fold_check(configures):
    checkpoints_dir = 'checkpoints_dir'
    if not os.path.exists(configures.checkpoints_dir) or not hasattr(configures, checkpoints_dir):
        print('checkpoints fold not found, creating...')
        paths = configures.checkpoints_dir.split('/')
        if len(paths) == 2 and os.path.exists(paths[0]) and not os.path.exists(configures.checkpoints_dir):
            os.mkdir(configures.checkpoints_dir)
        else:
            os.mkdir('checkpoints')

    log_dir = 'log_dir'
    if not os.path.exists(configures.log_dir) or not hasattr(configures, log_dir):
        print('log fold not found, creating...')
        os.mkdir(configures.log_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entity extractor by binary tagging')
    parser.add_argument('--config_file', default='system.config', help='Configuration File')
    args = parser.parse_args()
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    configs = Configure(config_file=args.config_file)
    fold_check(configs)
    logger = get_logger(configs.log_dir)
    configs.show_data_summary(logger)
    mode = configs.mode.lower()
    if mode == 'train':
        logger.info('mode: train')
        train(configs, device, logger)
    elif mode == 'interactive_predict':
        logger.info('mode: predict_one')
        tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        bert_model = BertModel.from_pretrained('bert-base-chinese').to(device)
        model = torch.load(os.path.join(configs.checkpoints_dir, 'best_model.pkl'))
        while True:
            logger.info('please input a sentence (enter [exit] to exit.)')
            sentence = input()
            if sentence == 'exit':
                break
            results = extract_entities(configs, tokenizer, sentence, bert_model, model, device, mode='predict')
            print(results)
