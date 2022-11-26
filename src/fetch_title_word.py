#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Fetch title words from Wikipedia
# (C) Yasuking0304, MIT License.
import bz2
from flask import Flask
import os
import requests
import sys
import threading
import time

hira_tbl =  'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん' \
            'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゐゑゔ' \
            'ぁぃぅぇぉっゃゅょー・〜～'
kata_tbl =  'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン' \
            'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポヰヱヴ' \
            'ァィゥェォッャュョー・〜～'
kana_tbl =  hira_tbl + kata_tbl

def to_hira(in_str: str):
    out_str :str = in_str
    for i, moji in enumerate(kata_tbl):
        out_str = out_str.replace(moji, hira_tbl[i:i+1])
    return str(out_str)

def to_hirayomi(in_str: str):
    out_str :str = in_str
    out_str = out_str.replace('・', '').replace('〜', 'ー').replace('～', 'ー').replace('☆', '')
    out_str = out_str.replace('”', '').replace('“', '').replace('’', '').replace('‘', '')
    out_str = out_str.replace('「', '').replace('」', '').replace('『', '').replace('』', '')
    out_str = out_str.replace('＝', '').replace('。', '').replace('、', '').replace(',', '')
    out_str = out_str.replace('！', '').replace('!', '').replace('♡', '').replace('♥', '')
    out_str = out_str.replace('×', '')
    non_str = out_str
    for i, moji in enumerate(kata_tbl):
        out_str = out_str.replace(moji, hira_tbl[i:i+1])
        non_str = non_str.replace(moji, '')
    for i, moji in enumerate(hira_tbl):
        non_str = non_str.replace(moji, '')
    if non_str != '':
        out_str = ''
    return str(out_str)

def get_kana(in_str: str, title: str):
    in_str = in_str.replace('(', '（').replace(')', '）')
    if to_hirayomi(title) != '':
        return to_hirayomi(title)
    start_index = -1
    end_index = start_index + 1
    if '（' in in_str:
        start_index = in_str.index('（')
    if '）' in in_str:
        end_index = in_str.index('）', start_index + 1)
    if start_index == -1:
        return ''
    in_str = in_str[start_index:end_index]
    out_str :str = ''
    bracket_count = 0
    brace_count = 0
    in_str = change_tag(in_str)
    in_str = in_str.replace('・', '').replace('〜', 'ー').replace('～', 'ー')
    in_str = in_str.replace('☆', '').replace('！', '').replace('!', '')
    in_str = in_str.replace('♡', '').replace('♥', '').replace('×', '')
    in_str = in_str.replace('：', '').replace(':', '')
    for moji in in_str:
        if moji == '[':
            bracket_count += 1
            continue
        if moji == '{':
            brace_count += 1
            continue
        if moji == ']':
            bracket_count -= 1
            continue
        if moji == '}':
            brace_count -= 1
            continue
        if bracket_count > 0:
            continue
        if brace_count > 0:
            continue
        if moji == ' ' and out_str != '':
            continue
        if moji == '　' and out_str != '':
            continue
        index = -1
        try:
            index = kana_tbl.index(moji)
        except ValueError:
            pass
        if index == -1 and out_str == '':
            continue
        if index == -1 and out_str != '':
            break
        out_str += moji
    return str(to_hira(out_str))

def change_tag(in_str: str):
    in_str = in_str.replace('&lt;', '<').replace('&gt;', '>')
    in_str = in_str.replace('&quot;', '"').replace('&amp;', '&')
    in_str = in_str.replace('<br />', '').replace('<br/>', '').replace('<nowiki/>', '')
    out_str = in_str
    while '<ref' in in_str:
        start_index = in_str.index('<ref')
        pre_end_index1 = len(in_str)
        pre_end_index2 = len(in_str)
        try:
            if '/>' in in_str:
                pre_end_index1 = in_str.index('/>', start_index + 1) + len('/>')
            if '</ref>' in in_str:
                pre_end_index2 = in_str.index('</ref>', start_index + 1) + len('</ref>')
            end_index = min(pre_end_index1, pre_end_index2)
            out_str = in_str[0:start_index]
            out_str += in_str[end_index:]
            in_str = out_str
        except ValueError:
            break
    if '{{efn|' in in_str and '}}' in in_str:
        try:
            start_index = in_str.index('{{efn|')
            end_index = in_str.index('}}', start_index + 1)
            out_str = in_str[0:start_index]
            out_str += in_str[end_index+len('}}'):]
        except ValueError:
            pass
    if '{{Refn|' in in_str and '}}' in in_str:
        try:
            start_index = in_str.index('{{Refn|')
            end_index = in_str.index('}}', start_index + 1)
            out_str = in_str[0:start_index]
            out_str += in_str[end_index+len('}}'):]
        except ValueError:
            pass
    if '{{Sfn|' in in_str and '}}' in in_str:
        try:
            start_index = in_str.index('{{Sfn|')
            end_index = in_str.index('}}', start_index + 1)
            out_str = in_str[0:start_index]
            out_str += in_str[end_index+len('}}'):]
        except ValueError:
            pass
    if '<!--' in in_str and '-->' in in_str:
        try:
            start_index = in_str.index('<!--')
            end_index = in_str.index('-->', start_index + 1)
            out_str = in_str[0:start_index]
            out_str += in_str[end_index+len('-->'):]
        except ValueError:
            pass
    in_str = out_str
    if '{{JIS2004フォント|' in in_str:
        try:
            start_index = in_str.index('{{JIS2004フォント|')
            end_index = in_str.index('}}')
            ucode_str = in_str[start_index+len('{{JIS2004フォント|'):end_index]
            ucode_bytes = ucode_str.replace(';', '').replace('&#x', '0x').replace('&#', '')
            out_str = in_str[0:start_index]
            if '0x' in ucode_bytes:
                out_str += chr(int(ucode_bytes, 16))
            else:
                out_str += chr(int(ucode_bytes, 10))
            out_str += in_str[end_index+len('}}'):]
        except ValueError:
            pass
    if '{{JIS90フォント|' in in_str:
        try:
            out_str = in_str.replace('{{JIS90フォント|', '').replace('}}', '', 1)
        except ValueError:
            pass
    if '{{lang|ja-Latn|' in in_str:
        try:
            out_str = in_str.replace('{{lang|ja-Latn|', '').replace('}}', '', 1)
        except ValueError:
            pass
    if '{{lang|ko|' in in_str:
        try:
            out_str = in_str.replace('{{lang|ko|', '').replace('}}', '', 1)
        except ValueError:
            pass
    if '{{Color|red|' in in_str:
        try:
            out_str = in_str.replace('{{Color|red|', '').replace('}}', '', 1)
        except ValueError:
            pass
    if '{{Color|pink|' in in_str:
        try:
            out_str = in_str.replace('{{Color|pink|', '').replace('}}', '', 1)
        except ValueError:
            pass
    if '{{拡張漢字|' in in_str:
        try:
            out_str = in_str.replace('{{拡張漢字|', '').replace('}}', '', 1)
        except ValueError:
            pass
    return str(out_str)

def get_title(in_str: str):
    out_str :str = ''
    in_str = change_tag(in_str)
    try:
        start_index = in_str.index("'''") + 3
        end_index = in_str.index("'''", 3)
        out_str = in_str[start_index:end_index]
    except ValueError:
        pass
    if '&#' in out_str and ';' in out_str:
        try:
            in_str = out_str
            start_index = in_str.index('&#')
            end_index = in_str.index(';')
            ucode_str = in_str[start_index+len('&#'):end_index]
            ucode_bytes = ucode_str.replace(';', '').replace('x', '0x')
            out_str = in_str[0:start_index]
            if '0x' in ucode_bytes:
                out_str += chr(int(ucode_bytes, 16))
            else:
                out_str += chr(int(ucode_bytes, 10))
            out_str += in_str[end_index+len(';'):]
        except ValueError:
            pass
    while '[[' in out_str and ']]' in out_str:
        try:
            in_str = out_str
            start_index = in_str.index('[[')
            end_index = in_str.index(']]')
            out_str = in_str[0:start_index]
            out_str += in_str[end_index+len(']]'):]
        except ValueError:
            pass
    if out_str.isascii():
        return str(out_str)
    return str(out_str.replace(' ', '').replace('　', ''))

def convert_title_yomigana(in_str: str):
    # なぜか作品名でもないものにタイトルにカッコを入れたがる人が多い。
    in_str = in_str.replace('『', '').replace('』', '').replace('「', '').replace('」', '')
    out_str :str = in_str
    if not '{{読み仮名|' in in_str:
        return out_str
    if not '}}' in in_str:
        return out_str
    if in_str.index('{{読み仮名|') != 0:
        return out_str
    try:
        start_index = in_str.index('{{')
        end_index = in_str.index('}}', start_index)
        start_index1 = start_index
        while '{{' in  in_str[start_index1 + len('{{'):end_index]:
            end_index = in_str.index('}}', end_index+len('}}'))
            start_index1 = end_index
        yomi_str = in_str[start_index + len('{{'):end_index].replace('読み仮名|', '')
        pre_str = in_str[0:start_index]
        sur_str = in_str[end_index+ len('}}'):]
        yomi_array = yomi_str.split('|')
        out_str = pre_str + yomi_array[0] + '（' + yomi_array[1] + '）' + sur_str
    except ValueError:
        return out_str
    return out_str

def cut_period(in_str: str):
    #2回の「。」まで文書を取り込む
    if not "'''" in in_str:
        return in_str
    end_index = len(in_str)
    try:
        end_index = in_str.index("'''", 1)
    except ValueError:
        pass
    try:
        end_index = in_str.index("。", end_index)
    except ValueError:
        return in_str
    try:
        end_index = in_str.index("。", end_index + 1)
    except ValueError:
        pass
    return in_str[:end_index+len('。')]

def cut_parenthesis(in_str: str):
    out_str = in_str
    out_str = out_str.replace('(', '（').replace(')', '）')
    start_index = -1
    end_index = -1
    if '（' in out_str:
        start_index = out_str.index('（')
    if '）' in out_str:
        end_index = out_str.index('）', start_index + 1)
    if start_index == -1:
        return out_str
    if end_index == -1:
        return out_str
    out_str = in_str[:start_index]
    out_str += in_str[end_index+1:]
    return out_str

def get_jinmei(in_str: str):
    part_os_speeech = '人名'
    title = get_title(in_str)
    if  '芸名' in title:
        return None
    if  '一覧' in title:
        return None
    if  '問題' in title:
        return None
    if  '事件' in title:
        return None
    if  '吹奏楽' in title:
        return None
    data = '"' + title + '","' + get_kana(in_str, title) + '","' + part_os_speeech + '",""'
    print(data)
    return data

def get_play_by_play(in_str: str):
    # 実況者のニックネームやVTuberを人名とするべきなのか
    part_os_speeech = '人名'
    title = get_title(in_str)
    if  '芸名' in title:
        return None
    if  '一覧' in title:
        return None
    if  '問題' in title:
        return None
    if  '事件' in title:
        return None
    data = '"' + title + '","' + get_kana(in_str, title) + '","' + part_os_speeech + '",""'
    print(data)
    return data

def get_lol(in_str: str):
    # 各人の書き方の揺れが。。。
    part_os_speeech = '人名'
    hint_word = ''
    title = get_title(in_str)
    if 'コンビ' in in_str and not '担当' in in_str and (not '芸人' in in_str or '(お笑い芸人)' in in_str) \
        and not 'リーダー' in in_str and not 'メンバー' in in_str:
        part_os_speeech = '固有名詞'
        hint_word = 'お笑いグループ'
    if 'トリオ' in in_str and not '担当' in in_str and (not '芸人' in in_str or '(お笑い芸人)' in in_str) \
        and not 'リーダー' in in_str and not 'メンバー' in in_str:
        part_os_speeech = '固有名詞'
        hint_word = 'お笑いグループ'
    if 'カルテット' in in_str and not '担当' in in_str and (not '芸人' in in_str or '(お笑い芸人)' in in_str) \
        and not 'リーダー' in in_str and not 'メンバー' in in_str:
        part_os_speeech = '固有名詞'
        hint_word = 'お笑いグループ'
    if 'グループ' in in_str and not '担当' in in_str and (not '芸人' in in_str or '(お笑い芸人)' in in_str) \
        and not 'リーダー' in in_str and not 'メンバー' in in_str:
        part_os_speeech = '固有名詞'
        hint_word = 'お笑いグループ'
    if 'ユニット' in in_str and not '担当' in in_str and (not '芸人' in in_str or '(お笑い芸人)' in in_str) \
        and not 'リーダー' in in_str and not 'メンバー' in in_str:
        part_os_speeech = '固有名詞'
        hint_word = 'お笑いグループ'
    if title != '吉本坂46' and '吉本坂46' in in_str:
        part_os_speeech = '人名'
        hint_word = ''
    if '寄席' in in_str:
        return None
    if '賞。' in in_str:
        return None
    if '芸' in title:
        return None
    if '事件' in title:
        return None
    if 'イロモネア' in title:
        return None
    if '漫才' in title:
        return None
    if 'コント' == title:
        return None
    if '一覧' in title:
        return None
    if '吹奏楽' in title:
        return None
    if 'ハリセン' == title:
        return None
    if '萬歳' == title:
        return None
    if '自虐ネタ' == title:
        return None
    if 'お笑い' in title:
        return None
    if  '天才ピアニスト' == title:
        # ピア「ニ」ストの「ニ」がカタカナではなく漢字の「に」
        in_str = in_str.replace('ピア二スト', 'ピアニスト')
    data = '"' + title + '","' + get_kana(in_str, title) + '","' + part_os_speeech + '","' + hint_word + '"'
    print(data)
    return data

def get_shukujitsu(in_str: str):
    # 元旦と昭和の日が抽出できないので付加する
    part_os_speeech = '固有名詞'
    title = get_title(in_str)
    if title[-1] != '日':
        return None
    if title == '平日':
        return None
    if title == '休日':
        return None
    if '住民の祝祭日' in in_str:
        #琉球政府
        return None
    data = '"' + title + '","' + get_kana(in_str, title) + '","' + part_os_speeech + '","国民の祝日"'
    print(data)
    if title == '成人の日':
        # データ補足
        data = '"元日","がんじつ","' + part_os_speeech + '","国民の祝日"'
        print(data)
        data = '"昭和の日","しょうわのひ","' + part_os_speeech + '","国民の祝日"'
        print(data)
        
    return data

def get_ryoseikoku(in_str: str):
    part_os_speeech = '地名'
    hint_word = "令制国"
    title = get_title(in_str)
    if title[-1] != '国':
        return None
    if title in ["多禰国"]:
        hint_word = "平安時代の令制国"
    if title in ["石城国", "石背国", "諏方国"]:
        hint_word = "奈良時代の令制国"
    kana = get_kana(in_str, title)
    data = '"' + title + '","' + kana + '","' + part_os_speeech + '","' + hint_word + '"'
    print(data)
    kana = kana.replace('のくに', 'こく')
    data = '"' + title + '","' + kana + '","' + part_os_speeech + '","' + hint_word + '"'
    print(data)
    if  kana == 'むつこく':
        kana = 'りくおうのくに'
        data = '"' + title + '","' + kana + '","' + part_os_speeech + '","' + hint_word + '"'
        print(data)
    return data

def get_hotkeyword(in_str: str):
    part_os_speeech = '固有名詞'
    title = get_title(in_str)
    data = '"' + title + '","' + get_kana(in_str, title) + '","' + part_os_speeech + '","ネットスラング"'
    print(data)
    return data

def get_onomatopee(in_str: str):
    part_os_speeech = '固有名詞'
    title = get_title(in_str)
    data = '"' + title + '","' + get_kana(in_str, title) + '","' + part_os_speeech + '","オノマトペ"'
    print(data)
    return data

def get_monster(in_str: str):
    part_os_speeech = '固有名詞'
    title = get_title(in_str)
    if  '怪獣' in title:
        return None
    if  '変身' in title:
        return None
    if  'モデル' in title:
        return None
    if  '恐竜' in in_str:
        return None
    if  'メーカー' in in_str:
        return None
    if  '画家' in in_str:
        return None
    if  '造形' in in_str:
        return None
    if  'アーティスト' in in_str:
        return None
    if  'イラストレーター' in in_str:
        return None
    if  'ぬいぐるみ' in in_str:
        return None
    data = '"' + title + '","' + get_kana(in_str, title) + '","' + part_os_speeech + '","怪獣"'
    print(data)
    return data

def get_dinosaurus(in_str: str):
    part_os_speeech = '固有名詞'
    hint_word = '恐竜'
    title = get_title(in_str)
    if "{{Lang|la|{{Snamei||Panguraptor}}}}" == title:
        # どうやら作成中
        title = 'パングラプトル'
    if  '血道弓' == title:
        return None
    if  '恐竜' in title:
        return None
    if  'ダイナソー' in title:
        return None
    if  '進化' in title:
        return None
    if  '鎖骨' in title:
        return None
    if  '叉骨' in title:
        return None
    if  '気嚢' in title:
        return None
    if  '羽毛' in title:
        return None
    if  '血道弓' in title:
        return None
    if  'デスポーズ' in title:
        return None
    if  'デンタルバッテリー' in title:
        return None
    if  'サワンナケート県' in title:
        return None
    if  '代' in title:
        return None
    if  '紀' in title:
        return None
    if  '属' in title:
        return None
    if  '目' in title:
        return None
    if  '類' in title:
        return None
    if  '科' in title:
        return None
    if  '層' in title:
        return None
    if  '所' in title:
        return None
    if  '館' in title:
        return None
    if  'ジョン' == title:
        title = 'ジャック・ホーナー'
    if  '学者]]' in in_str:
        part_os_speeech = '人名'
        hint_word = '恐竜学者'
    if  '学]]者' in in_str:
        part_os_speeech = '人名'
        hint_word = '恐竜学者'
    if 'アンタルクトサウルス' == title:
        # キーワードに学者が記載されているので例外で戻す
        hint_word = '恐竜'
    if 'PLEO' == title:
        hint_word = '恐竜玩具'
    if 'Juratic' == title:
        hint_word = '恐竜玩具'
    if  '漫画家' in in_str:
        return None
    if  'アーティスト' in in_str:
        return None
    if  'ゲーム' in in_str:
        return None
    if  'イラストレーター' in in_str:
        return None
    if  '撮影' in in_str:
        return None
    if  'ジオパーク' in in_str:
        return None
    if  'の[[化石' in in_str:
        return None
    if  'タレント' in in_str:
        return None
    if  'モデル' in in_str:
        return None
    if  '女優' in in_str:
        return None
    if  '俳優' in in_str:
        return None
    if  '造形家' in in_str:
        return None
    if  '小説' in in_str:
        return None
    if  '架空' in in_str:
        return None
    if  '仮想' in in_str:
        return None
    if  'バンド' in in_str:
        return None
    title = cut_parenthesis(title.replace("''", ''))
    kana = get_kana(in_str, title)
    data = '"' + title + '","' + kana + '","' + part_os_speeech + '","' + hint_word + '"'
    print(data)
    if 'ゔ' in kana:
        # 言葉のゆらぎ
        kana = kana.replace('ゔぁ', 'ば').replace('ゔぃ', 'び').replace('ゔぇ', 'べ')
        kana = kana.replace('ゔぉ', 'ぼ').replace('ゔ', 'ぶ')
        data = '"' + title + '","' + kana + '","' + part_os_speeech + '","' + hint_word + '"'
        print(data)
    return data

# test
## '''[https://ameblo.jp/egao79/entry-12722415683.html や]しろ 優'''（やしろ ゆう、[[1987年]][[7月9日]] - ）は、[[日本]]の[[お笑いタレント]]、[[ものまねタレント]]。
## '''ロンドンブーツ1号2号'''（ロンドンブーツいちごうにごう）は、'''[[田村淳]]'''と'''[[田村亮 (お笑い芸人)|田村亮]]'''からなる[[吉本興業]]所属の男性[[お笑いタレント|お笑いコンビ]]、[[司会|司会者]]。略称は「'''ロンブー'''」、「'''ロンドンブーツ'''」。
## '''中川家'''（なかがわけ）は、'''[[中川剛 (お笑い芸人)|剛]]'''（つよし）と'''[[中川礼二|礼二]]'''（れいじ）による兄弟[[漫才]]コンビである。
## '''富澤 たけし'''（とみざわ たけし、[[1974年]]〈[[昭和]]49年〉[[4月30日]] - ）は[[日本]]のお笑いタレント。俳優。
## '''木村 吉清'''(きむら よしきよ、生年不詳 - [[慶長]]3年（[[1598年]]））は、
#item="'''ジョン'''（通称ジャック）'''R.ホーナー'''（John（\"Jack\"）  R. Horner　[[1946年]][[6月15日]] - ）は[[アメリカ合衆国]]の[[古生物学]]者であり、[[恐竜]]が子育てをしたという初めての明確な証拠となった[[マイアサウラ]]の発見、記載者である。"
#print(get_kana("'''天才ピアニスト'''（てんさいピア二スト）は、[[吉本興業]]大阪本社に所属する日本の女性[[お笑いタレント|お笑いコンビ]]。", "dummy"))
#print(convert_title_yomigana("{{読み仮名|'''文化の日'''|ぶんかのひ}}は、[[日本]]の[[国民の祝日]]の一つである。日付は[[11月3日]]。"))
#print(get_title("'''石川 {{拡張漢字|啄}}木'''（いしかわ たくぼく、[[1886年]]（[[明治]]19年）[[2月20日]] - [[1912年]]（明治45年）[[4月13日]]）は、[[岩手県]]出身の[[日本]]の[[歌人]]、[[詩人]]。「{{拡張漢字|啄}}木」は[[雅号]]で、本名は「'''一'''（はじめ）」。"))
#print(get_title("'''&#29881;子内親王'''（じゅしないしんのう、[[弘安]]10年（[[1287年]]） - [[延慶 (日本)|延慶]]3年[[10月8日 (旧暦)|10月8日]]（[[1310年]][[10月30日]]））は、[[鎌倉時代]]後期の[[皇族]]、[[女院]]、[[歌人]]。女院号は'''朔平門院'''（さくへいもんいん）。"))
#print(convert_title_yomigana("{{読み仮名|'''天開 司'''|てんかい つかさ|}}は、[[日本]]の男性[[バーチャルYouTuber]]（以下「VTuber」）。")) 
#print(get_title("'''{{JIS90フォント|辻 希美}}'''（つじ のぞみ、[[1987年]][[6月17日]] - ）は、[[日本]]の[[タレント]]、[[歌手]]、[[YouTuber]]、[[コメンテーター]]、元[[アイドル]]。"))
#print(get_title("'''{{lang|ja-Latn|かしこまり}}'''（''{{lang|en|Kashiko Mari}}''）は、[[日本]]の[[バーチャルYouTuber]]、[[シンガーソングライター|バーチャルシンガー]]。"))
#print(get_kana("'''櫻井 ゆりの'''（さくらい ゆりの) は[[日本]]の女性[[タレント]]、ゲームタレント、[[ゲーム実況者]]。元[[王様のブランチ]]リポーター、[[京都府]]出身。", "dummy"))
#print(get_kana("'''甲賀流忍者!ぽんぽこ'''（こうがりゅうにんじゃ!ぽんぽこ、以下ぽんぽこ）は、[[日本]]の[[女性]][[バーチャルYouTuber]]（VTuber）<ref name=\"niconico\">{{Cite web|url=https://news.nicovideo.jp/watch/nw3928591|title=滋賀県に生息するご当地系VTuber「甲賀流忍者ぽんぽこ」|work=右も左も個性派ぞろい！ 注目の“動物系”VTuber紹介|website=[[ニコニコニュース]]|publisher=[[ドワンゴ]]|date=2018-09-24|accessdate=2021-09-04}}</ref>、[[ゆるキャラ]]<ref name=\"yurugp\" />。VTuberの[[ピーナッツくん]]と共に活動することが多く<ref name=\"niconico\" />、ピーナッツくんとのコンビ名は「'''ぽこピー'''」<ref name=\"vsc\">{{Cite web|url=https://kai-you.net/article/68117|title=ぽこピー、おめシス、名取さな──VTuber「個人勢の星」渋谷に集結|website=KAI-YOU.net|date=2019-10-04|accessdate=2022-02-13}}</ref>。事務所に所属していない個人のVTuberである<ref name=\"vsc\" />。","dummy"))

web_stop = False

key = 'USERPROFILE'
downloadfolder = 'Downloads'
if 'darwin' == sys.platform:
    key = 'HOME'
if 'linux' == sys.platform:
    key = 'HOME'
    downloadfolder = 'ダウンロード'
folder = os.path.join(os.getenv(key), downloadfolder)

def thread_web():
    app = Flask(__name__,
                static_url_path='', 
                static_folder=folder)
    app.run(host='127.0.0.1', port=8080)
    while True:
        if True == web_stop:
            break
        time.sleep(0.5) 

url = ""
try:
    if os.path.isfile(os.path.join(folder, 'jawiki-latest-pages-articles.xml.bz2')):
        thread1 = threading.Thread(target=thread_web)
        thread1.setDaemon(True)
        thread1.start()
        # ダウンロードファイルからデータ取得
        url = 'http://localhost:8080/jawiki-latest-pages-articles.xml.bz2'
    else:
        # wikipediaの倉庫から直接データ取得
        url = 'https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles.xml.bz2'
    r = requests.get(url, stream=True,  headers={'User-agent': 'Mozilla/5.0'})
    chunk_size = 32 * 1024
    decom = bz2.BZ2Decompressor()
    backarray: bytes = b''
    headerflag = False
    for data in r.iter_content(chunk_size):
        text_bufx = decom.decompress(data)
        text_buf =  bytes(backarray + text_bufx)
        if text_buf == b'':
            continue
        idxlist = []
        previdx = 0
        for idx, val in enumerate(text_buf):
            if val == 0x0a:
                if str.strip(text_buf[previdx:idx].decode('utf-8')) == '':
                    previdx = idx + 1
                    continue
                idxlist.append(str.strip(text_buf[previdx:idx].decode('utf-8')))
                previdx = idx + 1
        headerflag = True
        for item in idxlist:
            #↓---- 変換 ----
            item = convert_title_yomigana(item)
            if item[0:2] == "{{":
                headerflag = True
                continue
            if item[0:2] == "==":
                headerflag = False
                continue
            if item[0:3] != "'''":
                continue
            if headerflag == False:
                continue
            if item[0:5] == "'''[[":
                continue
            #↓---- 変換 ----
            # まりなす対策
            item = item.replace("バーチャルダンス&ボーカルユニット", "[[バーチャルYouTuber]]")
            # にじさんじ対策
            item = item.replace("[[バーチャルライバー]]", "バーチャルライバー")
            item = item.replace("バーチャルライバー", "[[バーチャルYouTuber]]")
            #↓---- 除外リスト ----
            item = change_tag(item)
            item = cut_period(item)
            headerflag = False
            if "一覧'''" in item:
                continue
            if 'テレビ番組' in item:
                continue
            if 'ラジオ番組' in item:
                continue
            if '情報番組' in item:
                continue
            if '動画番組' in item:
                continue
            if '情報誌' in item:
                continue
            if '専門チャンネル' in item:
                continue
            if '専門学校' in item:
                continue
            if "'''株式会社" in item:
                continue
            if "株式会社'''" in item:
                continue
            if "'''有限会社" in item:
                continue
            if "有限会社'''" in item:
                continue
            if 'シングル]]' in item:
                continue
            if 'アルバム]]' in item:
                continue
            if 'ライブ・ツアー' in item:
                continue
            if '[[インターネットラジオ]]' in item:
                continue
            if '[[部署]]' in item:
                continue
            if '[[劇団]]' in item:
                continue
            if '芸能事務所' in item:
                continue
            if '声優事務所' in item:
                continue
            if '個人事務所' in item:
                continue
            #↑---- 除外リスト ----
            #↓---- 抽出リスト ----
            '''
            if '声優]]' in item and not '架空' in item and not '登場人物' in item:
                get_jinmei(item)
                continue
            if '[[ナレーター]]' in item:
                get_jinmei(item)
                continue
            if '俳優]]' in item and not '架空' in item and not '登場人物' in item:
                get_jinmei(item)
                continue
            if '女優]]' in item and not '架空' in item and not '登場人物' in item:
                get_jinmei(item)
                continue
            if 'モデル]]' in item and not '架空' in item and not '登場人物' in item:
                get_jinmei(item)
                continue
            if 'タレント]]' in item and not '架空' in item and not '登場人物' in item:
                get_jinmei(item)
                continue
            if '[[歌舞伎役者]]' in item:
                get_jinmei(item)
                continue
            if '[[お笑い' in item or 'お笑いタレント' in item:
                # 思った以上に拾いすぎる
                get_lol(item)
                continue
            if '漫才]]' in item:
                get_lol(item)
                continue
            if '[[歌手]]' in item and not '架空' in item and not '登場人物' in item:
                get_jinmei(item)
                continue
            if '[[シンガーソングライター]]' in item:
                get_jinmei(item)
                continue
            if '[[ミュージシャン]]' in item:
                get_jinmei(item)
                continue
            if 'バンド]]' in item:
                get_jinmei(item)
                continue
            if '[[歌い手]]' in item:
                get_jinmei(item)
                continue
            if '[[ピアニスト]]' in item:
                get_jinmei(item)
                continue
            if '[[アナウンサー]]' in item:
                get_jinmei(item)
                continue
            if '[[フリーアナウンサー]]' in item:
                get_jinmei(item)
                continue
            if '[[プロ野球選手]]' in item:
                get_jinmei(item)
                continue
            if '[[卓球選手]]' in item:
                get_jinmei(item)
                continue
            if '[[卓球]]選手' in item:
                get_jinmei(item)
                continue
            if '[[水泳選手]]' in item:
                get_jinmei(item)
                continue
            if '競泳]]選手' in item:
                get_jinmei(item)
                continue
            if 'アーティスティックスイミング]]選手' in item:
                get_jinmei(item)
                continue
            if '[[レーシングドライバー]]' in item:
                get_jinmei(item)
                continue
            if 'サッカー選手]]' in item or 'サッカー]]選手' in item:
                get_jinmei(item)
                continue
            if 'テニス選手]]' in item or 'テニス]]選手' in item:
                get_jinmei(item)
                continue
            if 'バスケット選手]]' in item or 'バスケット]]選手' in item:
                get_jinmei(item)
                continue
            if 'バレーボール選手]]' in item or 'バレーボール]]選手' in item:
                get_jinmei(item)
                continue
            if '[[騎手]]' in item:
                get_jinmei(item)
                continue
            if '[[プロゴルファー]]' in item:
                get_jinmei(item)
                continue
            if '[[プロレスラー]]' in item:
                get_jinmei(item)
                continue
            if 'スケート]]選手' in item:
                get_jinmei(item)
                continue
            if '[[柔道家]]' in item:
                get_jinmei(item)
                continue
            if '力士]]' in item:
                get_jinmei(item)
                continue
            if '[[プロボクサー]]' in item:
                get_jinmei(item)
                continue
            if '[[プロボウラー]]' in item:
                get_jinmei(item)
                continue
            if '雀士]]' in item:
                get_jinmei(item)
                continue
            if '[[小説家]]' in item and '日本' in item:
                get_jinmei(item)
                continue
            if '[[作家]]' in item and '日本' in item:
                get_jinmei(item)
                continue
            if '[[詩人]]' in item and '日本' in item:
                get_jinmei(item)
                continue
            if '[[歌人]]' in item and '日本' in item:
                get_jinmei(item)
                continue
            if '大名' in item:
                get_jinmei(item)
                continue
            if '将軍]]' in item and '日本' in item:
                get_jinmei(item)
                continue
            if ('[[武将]]' in item or '武者' in item or '武士' in item) and '日本' in item:
                get_jinmei(item)
                continue
            if ('僧]]' in item or '僧兵' in item) and '日本' in item and not '小僧]]' in item:
                get_jinmei(item)
                continue
            if '皇族]]' in item and '日本' in item:
                get_jinmei(item)
                continue
            if '貴族]]' in item and '日本' in item:
                get_jinmei(item)
                continue
            if '[[漫画家]]' in item:
                get_jinmei(item)
                continue
            if '画家]]' in item and not '漫画家]]' in item:
                get_jinmei(item)
                continue
            if '[[アニメーター]]' in item:
                get_jinmei(item)
                continue
            if '[[イラストレーター]]' in item:
                get_jinmei(item)
                continue
            if 'アニメーション監督]]' in item:
                get_jinmei(item)
                continue
            if '映画監督]]' in item:
                get_jinmei(item)
                continue
            if 'ゲーム実況者]]' in item or 'ゲーム配信者]]' in item:
                get_play_by_play(item)
                continue
            if '[[YouTuber]]' in item:
                get_play_by_play(item)
                continue
            if 'バーチャルYouTuber' in item:
                get_play_by_play(item)
                continue
            if '[[令制国]]' in item and not '[[令制国]]以前' in item:
                get_ryoseikoku(item)
                continue
            if '[[国民の祝日]]' in item:
                # 元旦と昭和の日が抽出できない対策入り
                get_shukujitsu(item)
                continue
            if 'ネットスラング' in item:
                get_hotkeyword(item)
                continue
            if '擬態語' in item:
                get_onomatopee(item)
                continue
            #if 'コンピュータゲーム' in item:
            #    # 残念だが精度が悪い
            #    get_onomatopee(item)
            #    continue
            #if 'ライトノベル' in item:
            #    # 残念だが精度が悪い
            #    get_onomatopee(item)
            #    continue
            #if 'テレビゲーム' in item:
            #    # 思ったより範囲が広すぎる
            #    get_onomatopee(item)
            #    continue
            #if ('特撮映画]]' in item or '特撮怪獣映画]]' in item) and not '怪獣]]' in item:
            #    # 残念だが精度が悪い
            #    get_onomatopee(item)
            #    continue
            if '怪獣]]' in item:
                # ちなみに怪人をキーワードにすると拾いにくい
                get_monster(item)
                continue
            #if 'モンスター]]' in item:
            #    # そんなに拾わないしポケモンもそんなに拾わない
            #    get_monster(item)
            #    continue
            if '恐竜' in item:
                get_dinosaurus(item)
                continue
            '''
        backarray = text_buf[previdx:]
    True == web_stop
    sys.exit()

except KeyboardInterrupt:
    True == web_stop
    print("***Keyboard Interrupt***")
    sys.exit()
