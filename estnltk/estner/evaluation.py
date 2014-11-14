'''  
Module contains functions for NER performance estimation based on standard 
precision, recall and F1-score metrics. Functions should support different NE 
tagging formats e.g. simple, BIO, BILOU, etc. 
'''

from collections import defaultdict
import os
from estner import settings
import subprocess
import re
import sys


def eval_token_simple(predicted_labels, true_labels, classes):
    ''' Treats NEs as single tokens. Assumes simple NE tagging format (PER, ORG, LOC, FAC) '''
    guess_cnt = defaultdict(int)
    ans_cnt = defaultdict(int)
    tps = defaultdict(int)
    for guess, ans in zip(predicted_labels, true_labels):
        guess_cnt[guess] += 1
        ans_cnt[ans] += 1
        if guess == ans:
            tps[ans] += 1
    
    stat = get_stat(guess_cnt, ans_cnt, tps, classes)
    return stat

def conlleval(predicted_labels, true_labels, tokens=False):
    ''' Preferred evaluation method which uses official cnll evaluation script.
        Expects BIO-formatted labels. '''
    assert (len(predicted_labels) == len(true_labels))
    lbls = "\n".join("%s %s" %(t_lbl, p_lbl)
                     for t_lbl, p_lbl in zip(true_labels, predicted_labels))
    script = os.path.join(settings.PATH, "scripts", "ner", "conlleval.pl")
    p = subprocess.Popen(["perl", script], stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(lbls)
    p, r, f = {}, {}, {}
    stat = dict(p=p, r=r, f=f)
    for m in re.finditer(r'(?P<lbl>[A-Z]+): precision:\s+(?P<p>\d+\.\d+)%; recall:\s+(?P<r>\d+\.\d+)%; FB1:\s+(?P<f>\d+\.\d+)\s+(?P<c>\d+)', stdout):
        lbl = m.group('lbl')
        p[lbl] = float(m.group('p')) / 100
        r[lbl] = float(m.group('r')) / 100
        f[lbl] = float(m.group('f')) / 100
    m = re.search(r'accuracy:\s+.+%; precision:\s+(?P<p>\d+\.\d+)%; recall:\s+(?P<r>\d+\.\d+)%; FB1:\s+(?P<f>\d+\.\d+)',  stdout)
    stat['wap'] = float(m.group('p')) / 100
    stat['war'] = float(m.group('r')) / 100
    stat['waf'] = float(m.group('f')) / 100
    stat['str'] = stdout
    return stat

def _eval_seq_boi(predicted_labels, true_labels, classes):
    ''' Evaluates NE sequences, expects BOI-formatted input.  
        NB! DOESN'T WORK RIGHT! USE CONLLEVAL INSTEAD! '''
    p_guess = None
    p_ans = None
    err = False
    guess_cnt = defaultdict(int)
    ans_cnt = defaultdict(int)
    tps = defaultdict(int)
    
    for guess, ans in zip(predicted_labels + ['-'], true_labels + ['*']):
        is_new_guess = (guess != p_guess and bool(p_guess)) or guess[:2] == 'B-'
        is_new_ans   = (ans != p_ans and bool(p_ans)) or ans[:2] == 'B-'
        
        # get rid of B- prefix
        if guess[:2] == 'B-':
            guess = guess[2:]
        if ans[:2] == 'B-':
            ans = ans[2:]
        
        # register previous record
        
        if is_new_guess:
            guess_cnt[p_guess] += 1
            
        if is_new_ans:
            ans_cnt[p_ans] += 1
        
        if is_new_guess and is_new_ans and not err:
            tps[p_ans] += 1
        
        # check mismatch
        
        if is_new_guess and is_new_ans:
            err = False
            
        if is_new_guess != is_new_ans:
            err = True
        
        if guess != ans:
            err = True
        
        p_guess = guess
        p_ans = ans
    
    print guess_cnt
    print ans_cnt
    print tps
    
    stat = get_stat(guess_cnt, ans_cnt, tps, classes)
    
    return stat

def eval_seq_two_stage(predicted_labels, true_labels, classes, yesnolabels=None):
    ''' Evaluates NE sequences, expects BOI format input. '''
    p_guess = None
    p_ans = None
    err = False
    guess_cnt = defaultdict(int)
    ans_cnt = defaultdict(int)
    tps = defaultdict(int)
    
    for idx, (guess, ans) in enumerate(zip(predicted_labels + ['-'], true_labels + ['*'])):
        # if we have a list of positions of yes no labels, then use them
        if yesnolabels != None:
            if idx < len(yesnolabels) and yesnolabels[idx].startswith("Y"):
                if guess[:2] != 'B-':
                    guess = 'B-' + guess
        is_new_guess = (guess != p_guess and bool(p_guess)) or guess[:2] == 'B-'
        is_new_ans   = (ans != p_ans and bool(p_ans)) or ans[:2] == 'B-'
        
        # get rid of B- prefix
        if guess[:2] == 'B-':
            guess = guess[2:]
        if ans[:2] == 'B-':
            ans = ans[2:]
        
        # register previous record
        
        if is_new_guess:
            guess_cnt[p_guess] += 1
            
        if is_new_ans:
            ans_cnt[p_ans] += 1
        
        if is_new_guess and is_new_ans and not err:
            tps[p_ans] += 1
        
        # check mismatch
        
        if is_new_guess and is_new_ans:
            err = False
            
        if is_new_guess != is_new_ans:
            err = True
        
        if guess != ans:
            err = True
        
        p_guess = guess
        p_ans = ans
    
    stat = get_stat(guess_cnt, ans_cnt, tps, classes)
    
    return stat



def get_stat(guess_cnt, ans_cnt, tps, classes):
    ''' 
    Returns precision, recall, F1-score for each NE type individually and 
    their weighted averages over all NE types.   
    @param guess_cnt: dict  
    @param ans_cnt: dict
    @param tps: dict of true positives
    @param classes: list of NE types
    '''
    p, r, f = {}, {}, {}
    stat = dict(p=p, r=r, f=f)
    
    for cls in classes:
        p[cls] = tps[cls] / float(guess_cnt[cls]) if guess_cnt[cls] > 0 else 1.0
        r[cls] = tps[cls] / float(ans_cnt[cls]) if ans_cnt[cls] > 0 else 1.0
        f[cls] = 2.0 * p[cls] * r[cls] / (p[cls] + r[cls]) if p[cls] + r[cls] > 0 else 0.0
        
        p[cls] = round(p[cls], 4)
        r[cls] = round(r[cls], 4)
        f[cls] = round(f[cls], 4)
    
    total_guess_cnt = sum(guess_cnt[cls] for cls in classes)
    total_ans_cnt = sum(ans_cnt[cls] for cls in classes)
    if total_guess_cnt:
        stat["wap"] = sum(p[cls] * guess_cnt[cls] for cls in classes) / total_guess_cnt 
        stat["war"] = sum(r[cls] * ans_cnt[cls] for cls in classes) / total_ans_cnt
        stat["waf"] = 2.0 * stat["war"] * stat["wap"] / (stat["war"] + stat["wap"])
        
        stat["wap"] = round(stat["wap"], 4)
        stat["war"] = round(stat["war"], 4)
        stat["waf"] = round(stat["waf"], 4)
    else:
        stat["wap"] = stat["war"] = stat["waf"] = -1
        stat["ap"] = stat["ar"] = stat["af"] = -1
    return stat

if __name__ == "__main__":
    data = '''
    B-PER B-PER
    B-PER B-LOC
    O O
    O O
    O O
    B-LOC B-LOC
    O O
    O B-LOC
    
    '''
    print "DATA:\n", data 
    
    ans, gs = zip(*[line.strip().split(" ") 
                    for line in data.split("\n") if line.strip()])
    ans, gs = list(ans), list(gs)
    print "ANS:", ans
    print "GS: ", gs
    
    cs =  ['PER', 'LOC']
    
    print "CONLL EVAL"
    stat = conlleval(gs, ans)
    for c in cs:
        print c, stat["p"][c], stat["r"][c], stat["f"][c]
    print stat["wap"], stat["war"], stat["waf"]
    print stat["str"]
    
    print "ESTNER EVAL"
    stat = _eval_seq_boi(gs, ans, cs)
    for c in cs:
        print c, stat["p"][c], stat["r"][c], stat["f"][c]
    print stat["wap"], stat["war"], stat["waf"]
    