#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""资治通鉴 wikitext 解析器 v2 — 按换行数字分隔条目"""
import re, json

TRAN = {
'資':'资','治':'治','通':'通','鑑':'鉴','晉':'晋','趙':'赵','韓':'韩',
'侯':'侯','司':'司','馬':'马','光':'光','溫':'温','公':'公','書':'书',
'討':'讨','伐':'伐','寵':'宠','秩':'秩','於':'于','區':'区','分':'分',
'復':'复','棄':'弃','禮':'礼','職':'职','歲':'岁','時':'时','亂':'乱',
'紀':'纪','經':'经','傳':'传','記':'记','說':'说','論':'论',
'讓':'让','豐':'丰','產':'产','異':'异','載':'载',
'協':'协','畢':'毕','與':'与','賢':'贤','號':'号','稱':'称',
'聖':'圣','義':'义','執':'执','秉':'秉','猶':'犹','雖':'虽',
'湯':'汤','紂':'纣','魯':'鲁','鄭':'郑','衛':'卫','陳':'陈',
'蔡':'蔡','吳':'吴','蜀':'蜀','楚':'楚','燕':'燕',
'秦':'秦','齊':'齐','智':'智','范':'范','孫':'孙',
'冊':'册','拜':'拜','相':'相','升':'升','任':'任',
'聽':'听','從':'从','服':'服','事':'事','順':'顺','逆':'逆',
'姦':'奸','邪':'邪','枉':'枉','濁':'浊','顯':'显','隱':'隐',
'著':'著','聞':'闻','見':'见','知':'知','愚':'愚',
'弟':'悌','孝':'孝','忠':'忠','信':'信','仁':'仁',
'良':'良','恭':'恭','儉':'俭','廉':'廉','恥':'耻',
'果':'果','毅':'毅','德':'德','功':'功','罪':'罪','過':'过',
'賞':'赏','罰':'罚','聽':'听','從':'从','勝':'胜','敗':'败','強':'强','國':'国',
'歲':'岁','統':'统','綱':'纲','體':'体','陵':'陵',
'替':'替','專':'专','擅':'擅','篡':'篡','弒':'弑',
'亂':'乱','叛':'叛','廢':'废','興':'兴','褒':'褒','貶':'贬','黜':'黜',
'喪':'丧','並':'并','楊':'扬','為':'为','無':'无',
'問':'问','學':'学','爭':'争','戰':'战','攻':'攻','守':'守',
'圍':'围','侵':'侵','殺':'杀','誅':'诛',
'賊':'贼','盜':'盗','納':'纳','貢':'贡','賦':'赋','稅':'税',
'車':'车','馬':'马','騎':'骑','將':'将','帥':'帅',
'卒':'卒','兵':'兵','甲':'甲','陳':'阵',
'宮':'宫','京':'京','都':'都','城':'城','邑':'邑',
'關':'关','塞':'塞','邊':'边','州':'州','郡':'郡','縣':'县',
'鄉':'乡','山':'山','川':'川','河':'河','江':'江','淮':'淮','漢':'汉',
'東':'东','西':'西','南':'南','北':'北','內':'内','外':'外',
'初':'初','元':'元','正':'正','春':'春','夏':'夏','秋':'秋','冬':'冬',
'年':'年','月':'月','日':'日','文':'文','武':'武','明':'明',
'幽':'幽','厲':'厉','王':'王','莊':'庄','僖':'僖',
'頃':'顷','定':'定','簡':'简','康':'康','悼':'悼','哲':'哲','貞':'贞',
'獻':'献','靈':'灵','景':'景','項':'项','黃':'黄',
'白':'白','黑':'黑','赤':'赤','青':'青','紫':'紫',
'金':'金','銀':'银','銅':'铜','鐵':'铁','錫':'锡',
'玉':'玉','珠':'珠','璧':'璧','田':'田',
'湯':'汤','堯':'尧','舜':'舜','禹':'禹',
}

def tc2s(text):
    return ''.join(TRAN.get(c, c) for c in text)

def clean(text):
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', '', text)
    text = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[([^\]|]+)\]\]', r'\1', text)
    text = re.sub(r"'''(.+?)'''", r'\1', text)
    text = re.sub(r"''(.+?)''", r'\1', text)
    text = re.sub(r'{{[^|{}]+}}', '', text)
    text = re.sub(r'{{[^|{}]*\|', '', text)
    return text

def parse_and_extract(raw):
    text = clean(raw)
    text = tc2s(text)
    # 去掉 header
    text = re.sub(r"^title=.*?\n", '', text)
    text = re.sub(r'\|section=.*?\n', '', text)
    text = re.sub(r'\|author=.*?\n', '', text)
    text = re.sub(r'\|previous=.*?\n', '', text)
    text = re.sub(r'\|next=.*?\n', '', text)
    # 去掉开篇时间句
    text = re.sub(r"^'''[^']+'''\n", '', text)

    entries = []

    # 按 == 王 == 分割
    king_parts = re.split(r'\n== (.+?) ==\n', text)
    i = 1
    while i < len(king_parts) - 1:
        king = king_parts[i].strip()
        body = king_parts[i+1] if i+1 < len(king_parts) else ''
        i += 2

        # 按 === 年份 === 分割
        year_parts = re.split(r'\n=== (.+?) ===', body)
        j = 1
        while j < len(year_parts) - 1:
            year = year_parts[j].strip()
            content = year_parts[j+1] if j+1 < len(year_parts) else ''
            j += 2

            # 按 \n数字　 分割条目
            segs = re.split(r'\n(\d)　', content)
            # segs[0]=空白, [1]=数字1, [2]=内容1, [3]=数字2, [4]=内容2...
            k = 1
            while k < len(segs) - 1:
                num = segs[k]
                block = segs[k+1] if k+1 < len(segs) else ''
                k += 2

                if '::' in block:
                    parts = block.split('::', 1)
                    main_text = parts[0].strip()
                    guangu = parts[1].strip()
                else:
                    main_text = block.strip()
                    guangu = ''

                if main_text or guangu:
                    entries.append({
                        'king': king,
                        'year': year,
                        'num': num,
                        'main_text': main_text,
                        'guangu': guangu,
                    })

    return entries

if __name__ == '__main__':
    with open('/tmp/zizhi_raw.txt', encoding='utf-8') as f:
        raw = f.read()
    text_cleaned = clean(raw)
    text_jian = tc2s(text_cleaned)
    with open('/tmp/zizhi_jian.txt', 'w', encoding='utf-8') as f:
        f.write(text_jian)
    entries = parse_and_extract(text_jian)
    print(f'提取 {len(entries)} 条')
    for e in entries[:6]:
        print(f"\n--- {e['king']} {e['year']} ---")
        print(f"主文: {e['main_text'][:60]}")
        if e['guangu']:
            print(f"臣光曰: {e['guangu'][:60]}")

    out = '/Users/shiwen/.openclaw-autoclaw/workspace/zizhi-kb/data/zhouji1.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f'\n已保存到 {out}')
