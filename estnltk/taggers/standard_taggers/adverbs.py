
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

                      
