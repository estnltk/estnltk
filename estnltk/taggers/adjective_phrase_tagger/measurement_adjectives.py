from estnltk import Text

measurement_adjs = ['paksune', 'pikkune', 'ealine', 'aegne', 'suurune', 'jämedune', 'vanune', 'kõrgune',
                    'raskune', 'ajaline', 'ajane', 'sügavune', 'tagune', 'täis', 'tunnine', 'meetrine',
                    'laiune', 'kuuline', 'protsendine', 'tonnine', 'süllane', 'liitrine', 'hektarine',
                    'sekundine', 'kilomeetrine', 'minutine', 'nädalane', 'grammine', 'kilogrammine', 'kilone',
                    'tolline']


def is_measurement(word):
    if word in measurement_adjs:
        return True
    # kilogrammiline -> kilogrammine
    if word[0:-4] == 'line':
        word2 = word[0:-4] + 'ne'
        if word2 in measurement_adjs:
            return True
    return False


def is_number(word):
    text = Text(word, disambiguate=False)
    pos = text.postags[0].split('|')
    if 'N' in pos:
        return True
    else:
        try:
            # Check if the adjective has been derived from a number
            if word[0:-2] == 'ne':
                pos1 = Text(word[0:-2], disambiguate=False).postags[0].split('|')  # kuuene - > kuue
                pos2 = Text(word[0:-4], disambiguate=False).postags[0].split('|')  # kümneline -> kümne
                if 'N' in pos1 or 'N' in pos2:
                    return True
        except IndexError:
            pass
    return False


def is_measurement_adjective(adj):
    decision = 0
    analysed = Text(adj).analysis
    for an in analysed:
        root_tokens = Text(adj).analysis[0][0]['root_tokens']
        for i in root_tokens:
            # If at least one token is a number, adjective derived from number
            # or a measurement adjective, the adjective is a measurement adjective
            if len(i) > 0: ### To avoid the issue with negative numbers: -17 root tokens are ['', '17']
                if is_measurement(i) == True or is_number(i) == True:
                    decision = 1
    if decision == 0:
        return False
    else:
        return True
