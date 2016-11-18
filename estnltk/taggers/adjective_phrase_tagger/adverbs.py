from estnltk import Lemmas

ADJ_MODIFIERS = Lemmas('ääretult', 'äärmiselt', 'absoluutselt', 'aina', 'aiva', 'äkiliselt', 'äraütlemata',
                       'arusaamatult', 'ebainimlikult', 'ebatavaliselt', 'ehmatavalt', 'ekstra', 'emotsionaalselt',
                       'erakordselt', 'eriliselt', 'eriti', 'geniaalselt', 'häbematult', 'häirivalt', 'hämmastavalt',
                       'harjumatult', 'harukordselt', 'haruldaselt', 'hästi', 'hästi-hästi', 'hiigla', 'hiiglama',
                       'hirmuäratavalt', 'hirmus', 'hirmutavalt', 'hoopis', 'hoopiski', 'hullult', 'hullumeelselt',
                       'hullupööra', 'igamoodi', 'igapidi', 'igatemoodi', 'igati', 'igatpidi', 'ilgelt', 'iseäranis',
                       'jaburalt', 'jahmatavalt', 'jõle', 'jube', 'kahtlaselt', 'karjuvalt', 'kaunikesti', 'kaunis',
                       'kirjeldamatult', 'koguni', 'kogunisti', 'kohatult', 'kohutavalt', 'kõigiti', 'kole', 'koletult',
                       'kuigivõrd', 'kuitahes', 'kujuteldamatult', 'küllalt', 'küllaltki', 'kummaliselt', 'kuradima',
                       'kuratlikult', 'kurvastavalt', 'läbinisti', 'lämmatavalt', 'lapsemeelselt', 'lausa',
                       'lavaliselt',
                       'liialt', 'liiga', 'liigselt', 'lõpmata', 'lõpmatu', 'lõpmatult', 'maani', 'masendavalt',
                       'meeldivalt', 'meeletult', 'metsikult', 'muinasjutuliselt', 'müstiliselt', 'naiselikult',
                       'naljakalt', 'natike',
                       'nats', 'natuke', 'natukene', 'naturaalselt', 'neetult', 'nii', 'niigi', 'niiii', 'nii-nii',
                       'niipalju',
                       'niivõrd', 'nõnda', 'õige', 'õudselt', 'paganama', 'parajalt', 'parasjagu', 'päris', 'päriselt',
                       'peaaegu', 'pealtnäha', 'petlikult', 'pigem', 'piinavalt', 'piinlikult', 'piisavalt',
                       'pimestavalt',
                       'pisut', 'pööraselt', 'põrgulikult', 'rabavalt', 'röögatult', 'saati', 'sajaprotsendiliselt',
                       'sedavõrd', 'seesmiselt', 'seletamatult', 'silmatorkavalt', 'suht', 'suhteliselt', 'suisa',
                       'sümpaatselt', 'sünnipäraselt', 'täielikult', 'täiesti', 'täitsa', 'talumatult', 'tapvalt',
                       'tavatult', 'tobedalt', 'tõeliselt', 'tõepoolest', 'tõesti', 'tohutult', 'tõsi', 'totaalselt',
                       'totralt', 'tüütult', 'ühtviisi', 'ülearu', 'üleliia', 'ülemäära', 'ületamatult', 'ülevoolavalt',
                       'ülimalt', 'üllatavalt', 'umbes', 'umbkaudu', 'üpris', 'uskumatult', 'üsna', 'ütlemata', 'väga',
                       'väga-väga', 'vähe', 'väheke', 'väljakannatamatult', 'vanamoodsalt', 'vapustavalt', 'vastikult',
                       'veidi', 'veidike', 'veidikene', 'võimalikult', 'võimatult', 'võõrastavalt', 'võrdlemisi')

COMP_MODIFIERS = Lemmas('parasjagu', 'natuke', 'palju', 'kõige', 'veel', 'aina', 'tunduvalt', 'veelgi', 'veidi',
                        'pisut', 'üha', 'märksa', 'hoopis', 'oluliselt', 'järjest', 'mõnevõrra', 'kõvasti',
                        'märgatavalt', 'kuidagi', 'vähe', 'tublisti', 'vähegi', 'märkimisväärselt', 'sugugi',
                        'sootuks', 'natukene', 'selgelt', 'võrratult', 'sellevõrra', 'sedavõrd', 'tsipa', 'veidike',
                        'üksjagu', 'võrreldamatult', 'mõõtmatult')

# words that cannot form an adjective phrase with a participle
NOT_ADJ_MODIFIERS = ['võib-olla', 'arvatavasti', 'vist', 'kahjuks', 'kas', 'las', 'ju', 'siis', 'ka', 'samuti',
                     'eelkõige', 'veel', 'hoopis', 'küll', 'no', 'ometi', 'jah', 'vaat', 'eks', 'nagu', 'ikka',
                     'tegelikult', 'samas', 'üldse', 'väidetavalt', 'isegi', 'ilmselt', 'lihtsalt', 'ometi',
                     'kindlasti', 'vaid', 'seejärel', 'kah', 'pealegi', 'muidugi', 'enam', 'siiski', 'ainult',
                     'vaid', 'järjest', 'kõige', 'kuidas', 'ei', 'mil', 'või', 'kui']
                     
                     
ADVERB_CLASSES = {'diminisher' : [ 'natike', 'nats', 'natuke', 'natukene', 'pisut', 'vähe', 'väheke', 'veidi', 'veidike', 'veidikene' ],
'doubt' : ['kuigivõrd', 'küllalt', 'küllaltki', 'päris', 'peaaegu', 'pigem', 'suht', 'suhteliselt', 'täitsa', 'umbes', 'umbkaudu', 'üpris', 'üsna', 'võrdlemisi', 'õige', 'kaunikesti', 'kaunis' ],
'affirmation' : ['läbinisti', 'kõigiti', 'igamoodi', 'igapidi', 'igatemoodi', 'igati', 'igatpidi', 'päriselt', 'tõeliselt', 'tõepoolest', 'tõesti', 'sajaprotsendiliselt', 'täielikult', 'täiesti', 'absoluutselt', 'totaalselt', 'parajalt', 'parasjagu', 'piisavalt'],
'strong_intensifier' : [ 'ääretult', 'äärmiselt', 'äraütlemata', 'lõpmata', 'lõpmatu', 'lõpmatult', 'ütlemata', 'erakordselt', 'eriliselt', 'eriti', 'hästi-hästi', 'hiigla', 'hiiglama', 'iseäranis', 'kirjeldamatult', 'kujuteldamatult', 'meeletult', 'metsikult', 'muinasjutuliselt', 'müstiliselt', 'seletamatult', 'uskumatult', 'tohutult', 'pimestavalt', 'ülimalt', 'väga', 'väga-väga', 'hästi', 'hullult', 'hullumeelselt', 'hullupööra', 'jõle', 'jube', 'ilgelt', 'kole', 'koletult', 'neetult', 'paganama', 'põrgulikult', 'hirmus', 'hirmutavalt', 'kohutavalt', 'õudselt', 'hirmuäratavalt', 'nii', 'niigi', 'niii', 'nii-nii', 'niipalju', 'niivõrd', 'nõnda', 'sedavõrd'],
'surprise' : [ 'jahmatavalt', 'ehmatavalt', 'ebatavaliselt', 'üllatavalt', 'hämmastavalt', 'harjumatult', 'harukordselt', 'haruldaselt', 'rabavalt', 'vapustavalt', 'kummaliselt', 'pööraselt', 'tavatult'],
'excess' : [ 'liialt', 'liiga', 'liigselt', 'ülearu', 'üleliia', 'ülemäära', 'häirivalt', 'karjuvalt', 'kohatult', 'piinavalt', 'röögatult', 'talumatult', 'tapvalt', 'tobedalt', 'totralt', 'tüütult', 'väljakannatamatult', 'vastikult', 'jaburalt', 'piinlikult', 'ületamatult', 'võimatult']}


CLASSES = {}

for adv_cl in ADVERB_CLASSES:
    for adverb in ADVERB_CLASSES[adv_cl]:
        CLASSES[adverb] = adv_cl   
        
WEIGHTS = {'diminisher': 0.5, 'doubt': 0.7, 'affirmation' : 1.5, 'strong_intensifier' : 2, 'surprise' : 3, 'excess' : 4}

                      
