# -*- coding: utf-8 -*-
import re
from gensim.utils import simple_preprocess
import os


def prepare_digit_format(digit_code, digits_format):
    if digits_format == 'No_Change':
        output = digit_code
    fa_digits = list(range(1776, 1786))
    ar_digits = list(range(1632, 1642))
    en_digits = list(range(ord('0'), ord('9') + 1))
    if digits_format == 'En':
        if digit_code in fa_digits:
            output = digit_code - (fa_digits[0] - en_digits[0])
        elif digit_code in ar_digits:
            output = digit_code - (ar_digits[0] - en_digits[0])
        else:
            output = digit_code
    elif digits_format == 'Fa':
        if digit_code in fa_digits:
            output = digit_code
        elif digit_code in ar_digits:
            output = digit_code - (ar_digits[0] - fa_digits[0])
        else:
            output = digit_code - (en_digits[0] - fa_digits[0])
    elif digits_format == 'Ar':
        if digit_code in ar_digits:
            output = digit_code
        elif digit_code in fa_digits:
            output = digit_code - (fa_digits[0] - ar_digits[0])
        else:
            output = digit_code - (en_digits[0] - ar_digits[0])
    if digits_format == '|NUM|':
        return '|NUM|'
    else:
        return chr(output)


def remove_stop_words(text, stop_words):
    if type(stop_words) != 'set':
        stop_words = set(stop_words)
    final_words = []
    for word in text.split():
        if word not in stop_words:
            final_words.append(word)

    return ' '.join(final_words)


# digits_format in ('En', 'Fa','Ar','No_Change', '|NUM|')
# nim_fasele_action in ('Remove', 'No_Change', 'Space', 'Unified')
# enter_action in ('Space', 'No_Change', 'Unified')
# ok_characters=['fa', 'en', 'fa_digits', 'fa_signs', 'en_digits', 'en_signs']
def persian_pre_process(ww,
                        for_view=False,
                        print_log=False,
                        ok_characters=['fa', 'en', 'fa_digits', 'en_digits'],
                        special_characters=['@', '#', '$', '%'],
                        digits_format='|NUM|',
                        nim_fasele_action='Remove',
                        enter_action='Space',
                        stop_words=[]):
    if for_view:
        change_alef_kolahdar = False
        change_ye_hamze = False
        remove_erab = False
        remove_hamze_koochak = False
    else:
        change_alef_kolahdar = True
        change_ye_hamze = True
        remove_erab = True
        remove_hamze_koochak = True

    # [alef,be]+range(te,gheyn)+range(lam,vav)+[fe,ghaf]+[ye(farsi),kaf(farsi)]+[gaf,zhe,che,pe]
    alefbaFa = [1575, 1576] + list(range(1578, 1595)) + list(range(1604, 1609)) + [1601, 1602] + \
               [1705, 1740] + [1711, 1688, 1670, 1662]
    if change_alef_kolahdar == False:
        alefbaFa += [1570]
    if change_ye_hamze == False:
        alefbaFa += [1574]
    if remove_erab == False:
        alefbaFa += list(range(1611, 1618))
    if remove_hamze_koochak == False:
        alefbaFa += [1569]

    # range(0,9)
    arghamFa = list(range(1776, 1786))
    # Nim fasele
    nimFasele = [8203, 8204, 8205, 8288, 65279, 160]

    # enters
    enters = [10, 11, 12, 13, 133, 8232, 8233]

    # Alamat
    alamatFa = [1548, 1563, 1567] + list(range(1642, 1646))

    # Argham Arabic
    arghamAr = list(range(1632, 1642))
    # ok
    okFa = []
    nokFa = []
    if 'fa' in ok_characters:
        okFa += alefbaFa
    else:
        nokFa += alefbaFa
    if 'fa_digits' in ok_characters:
        okFa += (arghamFa + arghamAr)
    else:
        nokFa += arghamFa
    if 'fa_signs' in ok_characters:
        okFa += alamatFa
    else:
        nokFa += alamatFa

    # alefbaEn
    alfbaEn = list(range(ord('A'), ord('Z') + 1)) + list(range(ord('a'), ord('z') + 1))
    arghamEn = list(range(ord('0'), ord('9') + 1))
    alamatEn = ['.', ',', ';', '!', '~', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '|',
                ']', '[', '{', '}', ':', '>', '<', '?', '/', '`', chr(171), chr(187), chr(8211), chr(39)]
    for i in range(len(alamatEn)):
        alamatEn[i] = ord(alamatEn[i])

    okEn = []
    nokEn = []
    if 'en' in ok_characters:
        okEn += alfbaEn
    else:
        nokEn += alfbaEn
    if 'en_digits' in ok_characters:
        okEn += arghamEn
    else:
        nokEn += arghamEn
    if 'en_signs' in ok_characters:
        okEn += alamatEn
    else:
        nokEn += alamatEn

    ok = okFa + okEn
    nok = nokFa + nokEn
    # changeWith yeFarsi
    change1740 = [1740, 1568, 1574, 1597, 1598, 1599, 1609, 1610, 1656, 1741, 1742, 1744, 1745, 1746, 1747]
    # changeWith alef(bedoone sarkesh)
    change1575 = [1575, 1570, 1571, 1573, 1649, 1650, 1651, 1653]
    # changeWith Vav
    change1608 = [1608, 1572, 1654, 1655, 1743] + list(range(1732, 1740))
    # change with he(gerd)
    change1607 = [1607, 1577, 1726, 1749, 1791] + list(range(1728, 1732))
    # changeWith kaf
    change1705 = [1705, 1595, 1596, 1603] + list(range(1706, 1711))
    # changeWith gaf
    change1711 = [1711] + list(range(1712, 1717))
    # changeWith lam
    change1604 = [1604] + list(range(1717, 1721))
    # changeWith noon
    change1606 = [1606] + list(range(1721, 1726))
    # Remove arbic
    removeArabic = list(range(1536, 1548)) + list(range(1549, 1563)) + list(range(1750, 1774)) + [1789, 1790, 1564,
                                                                                                  1566, 1569, 1600,
                                                                                                  1648,
                                                                                                  1652, 1748] + list(
        range(1611, 1632))

    # changeWith be
    change1576 = [1576, 1646, 1659, 1664]
    # changeWith ghaf
    change1602 = [1602, 1647, 1703, 1704]
    # changeWith Te
    change1578 = [1578, 1657, 1658, 1660, 1661, 1663]
    # changeWith che
    chenge1670 = [1670, 1671, 1727]
    # changeWith he (jimi)
    change1581 = [1581] + list(range(1665, 1670))
    # changeWith dal
    change1583 = [1583, 1774] + list(range(1672, 1681))
    # changeWith re
    change1585 = [1585] + list(range(1681, 1688)) + [1689, 1775]
    # changeWith sin
    change1587 = [1587, 1690, 1691, 1692]
    # changeWith shin
    change1588 = [1588, 1786]
    # changeWith sad
    change1589 = [1589, 1693, 1694]
    # changeWith zad
    change1590 = [1590, 1787]
    # changeWith Ta(dastedar)
    change1591 = [1591, 1695]
    # changeWith ayn
    change1593 = [1593, 1696]
    # changeWith ghayn
    change1594 = [1594, 1788]
    # changeWith fe
    change1601 = [1601] + list(range(1696, 1703))
    # AllChanges
    allChanges = [change1587, change1594, change1593, change1591, change1590, change1589, change1588,
                  change1601, change1585, change1583, change1581, chenge1670, change1578, change1602,
                  change1576, change1606, change1604, change1711, change1705, change1607, change1608,
                  change1575, change1740]

    new_word = '';
    for ci in range(len(ww)):
        c = ord(ww[ci])
        if c in ok:
            if c in arghamAr + arghamEn + arghamFa:
                new_word += prepare_digit_format(c, digits_format)
            else:
                new_word = new_word + chr(c)
        elif chr(c) in special_characters:
            if c in arghamAr + arghamEn + arghamFa:
                new_word += prepare_digit_format(c, digits_format)
            else:
                new_word = new_word + chr(c)
        elif c in nok:
            new_word = new_word + chr(32)
        elif c in removeArabic:
            pass
        elif c in nimFasele:
            if nim_fasele_action == 'Remove':
                pass
            elif nim_fasele_action == 'No_Change':
                new_word = new_word + chr(c)
            elif nim_fasele_action == 'Space':
                new_word = new_word + ' '
            elif nim_fasele_action == 'Unified':
                new_word += chr(nimFasele[0])
        elif c in [32, ord('\t')]:
            new_word = new_word + ' '
        elif c in enters:
            if enter_action == 'No_Change':
                new_word = new_word + chr(c)
            elif enter_action == 'Space':
                new_word = new_word + ' '
            elif enter_action == 'Unified':
                new_word += chr(enters[0])
        else:
            flag = 0
            for ii in range(len(allChanges)):
                if c in allChanges[ii]:
                    new_word = new_word + chr(allChanges[ii][0])
                    flag = 1
            if flag == 0 and print_log:
                print(ci, c, chr(c), ww)
                pass
        while '|NUM||NUM|' in new_word:
            new_word = new_word.replace('|NUM||NUM|', '|NUM|')
        # new_word = re.sub('[\|NUM\|]+', '|NUM|', new_word)
        new_word = re.sub(' +', ' ', new_word)
        # while '  ' in new_word:
        #     new_word = new_word.replace('  ', ' ')
        # new_word = new_word.strip()
    if stop_words:
        # in this situation, some actions will be ignored
        # (for example we will have only space between words and enters are removed)
        return remove_stop_words(new_word, stop_words)
    return new_word


# output_type = ('list', 'string')
def persian_tokenizer(text, stem=True, remove_stop=True, min_word_length=1, max_word_length=50,
                      stop_words_path=None, output_type='list', stop_words=[]):
    if stem:
        text = persian_pre_process(text)
    if remove_stop:
        if stop_words:
            stop_words = set(stop_words)
        else:
            if not stop_words_path:
                stop_words_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\',
                                                                                                      '/') + '/datasets/persian_stop_words.txt'
            stop_words = set([persian_pre_process(w) for w in
                              open(stop_words_path, encoding='utf-8').read().split()])
    result = []
    out_put_str = ''

    for token in simple_preprocess(text, min_len=min_word_length, max_len=max_word_length):
        # print(token)
        if not remove_stop or token not in stop_words:
            result.append(token)
            out_put_str += token + ' '
            # print "selected"
    if output_type == 'list':
        return result
    elif output_type == 'string':
        if out_put_str:
            return out_put_str[:-1]
        else:
            return out_put_str
