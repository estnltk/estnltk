from estnltk.taggers.system.rule_taggers.regex_library.string_list import StringList
from estnltk.taggers.system.rule_taggers.regex_library.choice_group import ChoiceGroup
from estnltk.taggers.system.rule_taggers.regex_library.regex_element import RegexElement
from estnltk.taggers.system.rule_taggers.regex_library.regex_pattern import RegexPattern

#=========================================
#  Dose patterns and tests by swenlaur         
#=========================================

def test_regex_dose_patterns():
    # Various numeric expressions
    INTEGER = RegexElement('[0-9]+')
    INTEGER.full_match('123')
    INTEGER.full_match('012')
    INTEGER.test()

    SPACED_INTEGER = RegexElement('[0-9]+(?: 000)*')
    SPACED_INTEGER.full_match('1234')
    SPACED_INTEGER.full_match('123 000')
    SPACED_INTEGER.full_match('123 000 000')
    SPACED_INTEGER.test()

    DECIMAL_FRACTION = RegexElement(r'(?:[0-9]+\s*(?:,|\.)\s*)?[0-9]+')
    DECIMAL_FRACTION.full_match('123')
    DECIMAL_FRACTION.full_match('012')
    DECIMAL_FRACTION.full_match('1.2')
    DECIMAL_FRACTION.full_match('1,2')
    DECIMAL_FRACTION.full_match('0.12')
    DECIMAL_FRACTION.full_match('0,12')
    DECIMAL_FRACTION.full_match('1, 3')
    DECIMAL_FRACTION.full_match('1. 3')
    DECIMAL_FRACTION.full_match('1 , 3')
    DECIMAL_FRACTION.full_match('1 . 3')
    DECIMAL_FRACTION.no_match('.f')
    DECIMAL_FRACTION.no_match(',x')
    DECIMAL_FRACTION.test()

    INTEGER_ABBREVIATION = StringList(['milj.', 'milj'])
    SEMI_WORD_INTEGER = RegexPattern(r'{NUMBER}\s*{TEXT}').format(NUMBER=DECIMAL_FRACTION, TEXT=INTEGER_ABBREVIATION)
    SEMI_WORD_INTEGER.full_match('10 milj.')
    SEMI_WORD_INTEGER.full_match('1,5 milj.')
    SEMI_WORD_INTEGER.full_match('1 , 5milj.')
    SEMI_WORD_INTEGER.test()

    NUMBER_EXPRESSION = ChoiceGroup([SEMI_WORD_INTEGER, SPACED_INTEGER, DECIMAL_FRACTION])
    NUMBER_EXPRESSION.full_match('123')
    NUMBER_EXPRESSION.full_match('12.35')
    NUMBER_EXPRESSION.full_match('12.35 milj.')
    NUMBER_EXPRESSION.test()

    NUMBER_OR_RANGE = RegexPattern(r'{NUMBER}(?:\s*-\s*{NUMBER})?').format(
        NUMBER=ChoiceGroup([DECIMAL_FRACTION, SPACED_INTEGER]))
    NUMBER_OR_RANGE.full_match('236')
    NUMBER_OR_RANGE.full_match('23,6')
    NUMBER_OR_RANGE.full_match('236 000')
    NUMBER_OR_RANGE.full_match('185-740')
    NUMBER_OR_RANGE.full_match('185 - 740')
    NUMBER_OR_RANGE.full_match('185 000 - 740 000')
    NUMBER_OR_RANGE.test()

    NUMBER_SLASH_NUMBER = RegexPattern(r'{NUMBER}\s*/\S*{NUMBER}').format(NUMBER=DECIMAL_FRACTION)
    NUMBER_SLASH_NUMBER.full_match('185/300')
    NUMBER_SLASH_NUMBER.full_match('18,5/30')
    NUMBER_SLASH_NUMBER.full_match('185/30.3')
    NUMBER_SLASH_NUMBER.test()

    NUMERIC_SUM = RegexPattern(r'\(\s*{NUMBER}\s*\+\s*{NUMBER}\s*\)').format(NUMBER=INTEGER)
    NUMERIC_SUM.full_match('(20+5)')
    NUMERIC_SUM.test()

    # Dose units
    MASS_UNIT = StringList([
        'MG', 'MICROGRAMS', 'MIKROGRAMMI', 'MCG', 'MG I',
        'G', 'GRAMMI',
        'mg', 'mikrogrammi', 'mcg', 'g', 'grammi'
    ])
    TIME_UNIT = StringList(['H', 'h', 'TUNNIS', 'tunnis'])
    VOLUME_UNIT = StringList(['ML', 'ml', 'mL', 'L', 'l'])
    AMOUNT_UNIT = StringList(['MMOL', 'MOL'])
    RADIATION_UNIT = StringList(['GBq', 'MBq'])
    BIOLOGICAL_UNIT = StringList(['IU', 'ANTI-XA IU', 'MEGA IU', 'TÜ', 'RÜ', 'Ü', 'U', 'IR'])
    INJECTION_UNIT = StringList(['I.M.', 'I.M', 'I.V.', 'I.V'])
    DRUG_DOSE_UNIT = StringList(['ANNUS', 'ANNUSES', 'DOSE'])

    ANY_UNIT = ChoiceGroup([MASS_UNIT, TIME_UNIT, VOLUME_UNIT, AMOUNT_UNIT, INJECTION_UNIT, RADIATION_UNIT, BIOLOGICAL_UNIT])
    ANY_UNIT.full_match('MG')
    ANY_UNIT.full_match('ML')
    ANY_UNIT.full_match('MOL')
    ANY_UNIT.full_match('RÜ')
    ANY_UNIT.full_match('TUNNIS')
    ANY_UNIT.full_match('MBq')
    ANY_UNIT.full_match('I.M.')
    ANY_UNIT.test()

    INJECTION_PREFIX = StringList(['I.V.', 'I.V', 'I.M.', 'I.M'])

    # Simple dosages
    MASS_DOSE = RegexPattern(r'(?:{PREFIX}\s)?{NUMBER}\s*{UNIT}').format(
        PREFIX=INJECTION_PREFIX,
        NUMBER=ChoiceGroup([NUMERIC_SUM, DECIMAL_FRACTION]),
        UNIT=MASS_UNIT
    )
    MASS_DOSE.full_match('5 MG')
    MASS_DOSE.full_match('1,5 G')
    MASS_DOSE.full_match('1.5 MIKROGRAMMI')
    MASS_DOSE.full_match('(20+5) MG')
    MASS_DOSE.full_match('I.V. 40 MG')
    MASS_DOSE.full_match('0 , 05MG')
    MASS_DOSE.test()

    VOLUME_DOSE = RegexPattern(r'{NUMBER}\s*{UNIT}').format(NUMBER=DECIMAL_FRACTION, UNIT=VOLUME_UNIT)
    VOLUME_DOSE.full_match('40 L')
    VOLUME_DOSE.full_match('0 , 25 ML')
    VOLUME_DOSE.full_match('0 , 5 ml')
    VOLUME_DOSE.test()

    AMOUNT_DOSE = RegexPattern(r'{NUMBER}\s*{UNIT}').format(NUMBER=DECIMAL_FRACTION, UNIT=AMOUNT_UNIT)
    AMOUNT_DOSE.full_match('2 MMOL')
    AMOUNT_DOSE.full_match('1 , 25 MMOL')
    AMOUNT_DOSE.test()

    RADIATION_DOSE = RegexPattern(r'{NUMBER}\s*{UNIT}').format(NUMBER=NUMBER_OR_RANGE, UNIT=RADIATION_UNIT)
    RADIATION_DOSE.full_match('1 GBq')
    RADIATION_DOSE.full_match('1.5 MBq')
    RADIATION_DOSE.full_match('185-740 MBq')
    RADIATION_DOSE.test()

    BIOLOGICAL_DOSE = RegexPattern(r'{NUMBER}\s*{UNIT}').format(NUMBER=NUMBER_EXPRESSION, UNIT=BIOLOGICAL_UNIT)
    BIOLOGICAL_DOSE.full_match('4IU')
    BIOLOGICAL_DOSE.full_match('6 000 000 IU')
    BIOLOGICAL_DOSE.full_match('10000 TÜ')
    BIOLOGICAL_DOSE.full_match('1 , 5milj.TÜ')
    BIOLOGICAL_DOSE.full_match('500 RÜ')
    BIOLOGICAL_DOSE.full_match('20 000 U')
    BIOLOGICAL_DOSE.full_match('300 IR')
    BIOLOGICAL_DOSE.full_match('2,4 MEGA IU')
    BIOLOGICAL_DOSE.test()

    INJECTION_DOSE = RegexPattern(r'{NUMBER}\s*{UNIT}').format(NUMBER=DECIMAL_FRACTION, UNIT=INJECTION_UNIT)
    INJECTION_DOSE.full_match('1000 I.V.')
    INJECTION_DOSE.full_match('1000 I.M.')
    INJECTION_DOSE.full_match('250 I.V')
    INJECTION_DOSE.full_match('1000 I.M')
    INJECTION_DOSE.test()

    PERCENTAGE_SUFFIX = StringList(['INFUSIONSLÖSUNG'])

    PERCENTAGE_DOSE = RegexPattern(r'{DOSE}\s*%(?:(?:\s|-){SUFFIX})?').format(
        DOSE=DECIMAL_FRACTION,
        SUFFIX=PERCENTAGE_SUFFIX
    )
    PERCENTAGE_DOSE.full_match('5%')
    PERCENTAGE_DOSE.full_match('0 , 9%')
    PERCENTAGE_DOSE.full_match('1.2%')
    PERCENTAGE_DOSE.full_match('5%-INFUSIONSLÖSUNG')
    PERCENTAGE_DOSE.test()

    SIMPLE_DOSE = ChoiceGroup([
        MASS_DOSE,
        VOLUME_DOSE,
        AMOUNT_DOSE,
        RADIATION_DOSE,
        BIOLOGICAL_DOSE,
        INJECTION_DOSE,
        PERCENTAGE_DOSE
    ])
    SIMPLE_DOSE.full_match('5 MG')
    SIMPLE_DOSE.full_match('50 MICROGRAMS')
    SIMPLE_DOSE.full_match('40 L')
    SIMPLE_DOSE.full_match('1 GBq')
    SIMPLE_DOSE.full_match('4IU')
    SIMPLE_DOSE.full_match('1000 I.M.')
    SIMPLE_DOSE.full_match('1.2%')
    SIMPLE_DOSE.full_match('1 , 5milj.TÜ')
    SIMPLE_DOSE.full_match('185-740 MBq')
    SIMPLE_DOSE.test()

    # Various concentrations
    MASS_PER_VOLUME_UNIT = RegexPattern(r'{DOSE}\s*/\s*{UNIT}').format(DOSE=MASS_DOSE, UNIT=VOLUME_UNIT)
    MASS_PER_VOLUME_UNIT.full_match('5MG/ML')
    MASS_PER_VOLUME_UNIT.full_match('13 , 6 MG/ML')
    MASS_PER_VOLUME_UNIT.full_match('40 mg/ml')
    MASS_PER_VOLUME_UNIT.no_match('4 MMOL/L')
    MASS_PER_VOLUME_UNIT.full_match('(20+5) MG/ML')
    MASS_PER_VOLUME_UNIT.test()

    AMOUNT_PER_VOLUME_UNIT = RegexPattern(r'{DOSE}\s*/\s*{UNIT}').format(DOSE=AMOUNT_DOSE, UNIT=VOLUME_UNIT)
    AMOUNT_PER_VOLUME_UNIT.full_match('1 , 25 MMOL/L')
    AMOUNT_PER_VOLUME_UNIT.full_match('3 MMOL/L')
    AMOUNT_PER_VOLUME_UNIT.test()

    BIOLOGICAL_PER_VOLUME_UNIT = RegexPattern(r'{DOSE}\s*/\s*{UNIT}').format(DOSE=BIOLOGICAL_DOSE, UNIT=VOLUME_UNIT)
    BIOLOGICAL_PER_VOLUME_UNIT.full_match('5000TÜ/ml')
    BIOLOGICAL_PER_VOLUME_UNIT.full_match('85 000TÜ/ML')
    BIOLOGICAL_PER_VOLUME_UNIT.full_match('500 RÜ/ml')
    BIOLOGICAL_PER_VOLUME_UNIT.full_match('50 Ü/ML')
    BIOLOGICAL_PER_VOLUME_UNIT.test()

    RADIATION_PER_VOLUME_UNIT = RegexPattern(r'{DOSE}\s*/\s*{UNIT}').format(DOSE=RADIATION_DOSE, UNIT=VOLUME_UNIT)
    RADIATION_PER_VOLUME_UNIT.full_match('1 GBq/ml')
    RADIATION_PER_VOLUME_UNIT.full_match('185-740 MBq/ml')
    RADIATION_PER_VOLUME_UNIT.test()

    MASS_PER_MASS_UNIT = RegexPattern(r'{MASS}\s*/\s*{UNIT}').format(MASS=MASS_DOSE, UNIT=MASS_UNIT)
    MASS_PER_MASS_UNIT.full_match('25MG/G')
    MASS_PER_MASS_UNIT.full_match('1,5MG/G')
    MASS_PER_MASS_UNIT.test()

    VOLUME_PER_VOLUME_UNIT = RegexPattern(r'{DOSE}\s*/\s*{UNIT}').format(DOSE=VOLUME_DOSE, UNIT=VOLUME_UNIT)
    VOLUME_PER_VOLUME_UNIT.full_match('1ML/ML')
    VOLUME_PER_VOLUME_UNIT.test()

    # Various speed or rate specifications
    MASS_PER_TIME_UNIT = RegexPattern(r'{MASS_DOSE}\s*/\s*{UNIT}').format(MASS_DOSE=MASS_DOSE, UNIT=TIME_UNIT)
    MASS_PER_TIME_UNIT.full_match('25MCG/H')
    MASS_PER_TIME_UNIT.full_match('12mcg/h')
    MASS_PER_TIME_UNIT.full_match('25 MCG/TUNNIS')
    MASS_PER_TIME_UNIT.test()

    MASS_PER_DRUG_DOSE = RegexPattern(r'{MASS_DOSE}\s*/\s*{UNIT}').format(MASS_DOSE=MASS_DOSE, UNIT=DRUG_DOSE_UNIT)
    MASS_PER_DRUG_DOSE.full_match('50 MCG/DOSE')
    MASS_PER_DRUG_DOSE.full_match('200 MIKROGRAMMI/ANNUSES')
    MASS_PER_DRUG_DOSE.test()

    DOSE_PER_UNIT = ChoiceGroup([
        MASS_PER_VOLUME_UNIT,
        MASS_PER_TIME_UNIT,
        MASS_PER_VOLUME_UNIT,
        MASS_PER_MASS_UNIT,
        MASS_PER_DRUG_DOSE,
        AMOUNT_PER_VOLUME_UNIT,
        BIOLOGICAL_PER_VOLUME_UNIT,
        RADIATION_PER_VOLUME_UNIT,
        VOLUME_PER_VOLUME_UNIT
    ])
    DOSE_PER_UNIT.full_match('5MG/ML')
    DOSE_PER_UNIT.full_match('1 , 25 MMOL/L')
    DOSE_PER_UNIT.full_match('5000TÜ/ml')
    DOSE_PER_UNIT.full_match('1 GBq/ml')
    DOSE_PER_UNIT.full_match('1,5MG/G')
    DOSE_PER_UNIT.full_match('1ML/ML')
    DOSE_PER_UNIT.full_match('12mcg/h')
    DOSE_PER_UNIT.test()

    # Double dosages and alternative descriptions of the same dose in different units
    MASS_AND_MASS = RegexPattern(r'{DOSE}\s*(?:\+|/)\s*{DOSE}').format(DOSE=MASS_DOSE)
    MASS_AND_MASS.full_match('160 MG/25 MG')
    MASS_AND_MASS.full_match('0 , 05MG/5MG')
    MASS_AND_MASS.full_match('160 MG/12 , 5 MG')
    MASS_AND_MASS.full_match('300mg+50mg')
    MASS_AND_MASS.full_match('300mg + 50mg')
    MASS_AND_MASS.test()

    NUMBER_SLASH_MASS = RegexPattern(r'{DOSE}\s*{UNIT}').format(DOSE=NUMBER_SLASH_NUMBER, UNIT=MASS_UNIT)
    NUMBER_SLASH_MASS.full_match('100/25 MG')
    NUMBER_SLASH_MASS.full_match('100.3/25 MG')
    NUMBER_SLASH_MASS.test()

    MASS_AND_VOLUME = RegexPattern(r'{DOSE1}\s*(?:\*|\+|/)\s*{DOSE2}').format(DOSE1=MASS_DOSE, DOSE2=VOLUME_DOSE)
    MASS_AND_VOLUME.full_match('125MG/5ML')
    MASS_AND_VOLUME.full_match('312 , 5 MG/5ML')
    MASS_AND_VOLUME.full_match('125MG + 5ML')
    MASS_AND_VOLUME.test()

    MASS_AND_BIOLOGICAL = RegexPattern(r'{DOSE1}\s*(?:\+|/)\s*{DOSE2}').format(DOSE1=MASS_DOSE, DOSE2=BIOLOGICAL_DOSE)
    MASS_AND_BIOLOGICAL.full_match('500 MG/800 IU')
    MASS_AND_BIOLOGICAL.full_match('500MG+440 TÜ')
    MASS_AND_BIOLOGICAL.test()

    BIOLOGICAL_AND_BIOLOGICAL = RegexPattern(r'{DOSE}\s*(?:\+|&|/)\s*{DOSE}').format(DOSE=BIOLOGICAL_DOSE)
    BIOLOGICAL_AND_BIOLOGICAL.full_match('500 RÜ/375 RÜ')
    BIOLOGICAL_AND_BIOLOGICAL.full_match('500 RÜ + 375 RÜ')
    BIOLOGICAL_AND_BIOLOGICAL.full_match('100 IR & 300 IR')
    BIOLOGICAL_AND_BIOLOGICAL.test()

    BIOLOGICAL_SLASH_VOLUME = RegexPattern(r'{DOSE1}\s*/\s*{DOSE2}').format(DOSE1=BIOLOGICAL_DOSE, DOSE2=VOLUME_DOSE)
    BIOLOGICAL_SLASH_VOLUME.full_match('14000 ANTI-XA IU/0,7 ML')
    BIOLOGICAL_SLASH_VOLUME.test()


    DOUBLE_DOSE = ChoiceGroup([
        MASS_AND_MASS,
        MASS_AND_VOLUME,
        MASS_AND_BIOLOGICAL,
        BIOLOGICAL_AND_BIOLOGICAL,
        BIOLOGICAL_SLASH_VOLUME,
        NUMBER_SLASH_MASS
    ], merge_positive_tests=True)
    DOUBLE_DOSE.full_match('160 MG/25 MG')
    DOUBLE_DOSE.full_match('300mg+50mg')
    DOUBLE_DOSE.full_match('125MG/5ML')
    DOUBLE_DOSE.full_match('500MG+440 TÜ')
    DOUBLE_DOSE.full_match('500 RÜ + 375 RÜ')
    DOUBLE_DOSE.full_match('100/25 MG')
    DOUBLE_DOSE.test()

    # Double doses per unit
    MASS_AND_MASS_PER_VOLUME_UNIT = ChoiceGroup([
        RegexPattern(r'{DOSE}\s*/\s*{VOLUME}').format(DOSE=MASS_AND_MASS, VOLUME=VOLUME_UNIT),
        RegexPattern(r'{DOSE}\s*\+\s*{DOSE}').format(DOSE=MASS_PER_VOLUME_UNIT)
    ])
    MASS_AND_MASS_PER_VOLUME_UNIT.full_match('3 MG/50 MG/ML')
    MASS_AND_MASS_PER_VOLUME_UNIT.full_match('0 , 05MG/5MG/ML')
    MASS_AND_MASS_PER_VOLUME_UNIT.no_match('1 , 25 MMOL/L')
    MASS_AND_MASS_PER_VOLUME_UNIT.full_match('3 MG + 50 MG/ML')
    MASS_AND_MASS_PER_VOLUME_UNIT.full_match('5MG/ML+5MCG/ML')
    MASS_AND_MASS_PER_VOLUME_UNIT.test()

    MASS_SLASH_MASS_PER_MASS_UNIT = RegexPattern(r'{MASS_DOSE}\s*/\s*{VOLUME}').format(
        MASS_DOSE=MASS_AND_MASS, VOLUME=MASS_UNIT)
    MASS_SLASH_MASS_PER_MASS_UNIT.full_match('1MG/20MG/G')
    MASS_SLASH_MASS_PER_MASS_UNIT.test()

    DOUBLE_DOSE_PER_UNIT = ChoiceGroup([
        MASS_AND_MASS_PER_VOLUME_UNIT,
        MASS_SLASH_MASS_PER_MASS_UNIT
    ])
    DOUBLE_DOSE_PER_UNIT.full_match('3 MG/50 MG/ML')
    DOUBLE_DOSE_PER_UNIT.full_match('3 MG + 50 MG/ML')
    DOUBLE_DOSE_PER_UNIT.full_match('5MG/ML+5MCG/ML')
    DOUBLE_DOSE_PER_UNIT.full_match('1MG/20MG/G')
    DOUBLE_DOSE_PER_UNIT.test()

    # Other doses
    MASS_SLASH_MASS_SLASH_VOLUME = RegexPattern(r'{MASS}\s*/\s*{MASS}\s*/\s*{VOLUME}').format(
        MASS=MASS_DOSE, VOLUME=VOLUME_DOSE)
    MASS_SLASH_MASS_SLASH_VOLUME.full_match(r'160MG/48MG/5ML')
    MASS_SLASH_MASS_SLASH_VOLUME.test()

    MASS_SLASH_MASS_SLASH_MASS = RegexPattern(r'{MASS}\s*/\s*{MASS}\s*/\s*{MASS}').format(MASS=MASS_DOSE)
    MASS_SLASH_MASS_SLASH_MASS.full_match('10MG/5MG/5MG')
    MASS_SLASH_MASS_SLASH_MASS.test()

    QUALITATIVE_DOSE = StringList([
        'VÕRDSETES OSADES',
        'ÜKS KORD NÄDALAS',
    ])

    DOSE = ChoiceGroup([
        MASS_SLASH_MASS_SLASH_MASS,
        MASS_SLASH_MASS_SLASH_VOLUME,
        DOUBLE_DOSE_PER_UNIT,
        DOUBLE_DOSE,
        DOSE_PER_UNIT,
        SIMPLE_DOSE,
        QUALITATIVE_DOSE,
    ], merge_positive_tests=True)

    DOSE.test()