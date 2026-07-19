# Unicode formatting

LinkedIn has no rich text. The bold and italic in José's posts are Unicode
Mathematical Alphanumeric Symbols substituted character by character. Markdown
`**bold**` renders as literal asterisks on LinkedIn and is always wrong for that
target.

Emit the real characters directly in the output so the post can be pasted
straight in.

## The four sets he uses

### 1. Bold — Mathematical Sans-Serif Bold (his default emphasis)

```
𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭
𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇
𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵
```

Base code points: `A`→U+1D5D4, `a`→U+1D5EE, `0`→U+1D7EC.

Used for: the thesis sentence, coined terms, list labels, single load-bearing
words. Example: `𝗧𝗵𝗲 𝗯𝗼𝘁𝘁𝗹𝗲𝗻𝗲𝗰𝗸 𝗶𝘀 𝘂𝘀.`

### 2. Italic — Mathematical Sans-Serif Italic

```
𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡
𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻
```

Base code points: `A`→U+1D608, `a`→U+1D622. No digits exist in this set; leave
digits as plain ASCII (as he does in `𝘤𝘮𝘥 + 1, 2, 3`).

Used for: code identifiers, key shortcuts, stage directions, parenthetical
asides. Example: `𝘭𝘰𝘥𝘢𝘴𝘩.𝘪𝘴𝘌𝘮𝘱𝘵𝘺()`, `~𝘴𝘢𝘳𝘤𝘢𝘴𝘵𝘪𝘤 𝘴𝘶𝘴𝘱𝘦𝘯𝘴𝘦 𝘮𝘶𝘴𝘪𝘤~`.

### 3. Bold italic — Mathematical Sans-Serif Bold Italic

```
𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕
𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯
```

Base code points: `A`→U+1D63C, `a`→U+1D656. No digits.

Used for: quoted authorities and the rare emphatic word. Example: the Kent Beck
quote, and `simplicity is 𝙠𝙞𝙡𝙡𝙚𝙧`.

### 4. Monospace — Mathematical Monospace (only as the strikethrough base)

```
𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉
𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣
𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿
```

Base code points: `A`→U+1D670, `a`→U+1D68A, `0`→U+1D7F6.

## Strikethrough

Append U+0336 (combining long stroke overlay) after every character. He applies
it over monospace characters:

```
me 𝚛̶𝚊̶𝚗̶𝚝̶𝚒̶𝚗̶𝚐̶ complaining about how MCP servers are stateless
```

## Converter

When formatting more than a few words, run this instead of hand-substituting.
Hand substitution is where mistakes happen, particularly mixing the two italic
sets, which look nearly identical but are different code points.

```python
OFFSETS = {
    "bold":        (0x1D5D4, 0x1D5EE, 0x1D7EC),
    "italic":      (0x1D608, 0x1D622, None),
    "bolditalic":  (0x1D63C, 0x1D656, None),
    "mono":        (0x1D670, 0x1D68A, 0x1D7F6),
}

def convert(text, style, strike=False):
    up, lo, dg = OFFSETS[style]
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            ch = chr(up + ord(ch) - 65)
        elif "a" <= ch <= "z":
            ch = chr(lo + ord(ch) - 97)
        elif "0" <= ch <= "9" and dg:
            ch = chr(dg + ord(ch) - 48)
        out.append(ch + "̶" if strike else ch)
    return "".join(out)

# convert("The bottleneck is us.", "bold")  ->  𝗧𝗵𝗲 𝗯𝗼𝘁𝘁𝗹𝗲𝗻𝗲𝗰𝗸 𝗶𝘀 𝘂𝘀.
# convert("ranting", "mono", strike=True)   ->  𝚛̶𝚊̶𝚗̶𝚝̶𝚒̶𝚗̶𝚐̶
```

Punctuation, spaces, and accented characters have no substitutes and pass
through unchanged. That is correct and matches his posts.

## Rules

- Bold appears **1 to 4 times per post**, never more.
- A bolded sentence stands as its own paragraph. Do not bold mid-flow inside a
  running paragraph, except for a single word carrying the sentence
  (`it is 𝘆𝗼𝘂𝗿 liability`).
- Numbers inside a bolded run get bolded too: `𝟴𝟬%`, `𝟯𝟬𝗽𝘅`, `𝟭𝗹𝗵 = 𝟯𝟬𝗽𝘅`.
- Never bold a whole paragraph, and never bold two consecutive paragraphs.
- Do not use these characters outside LinkedIn. In a blog post, article, README,
  or anywhere markdown renders, use real markdown. They also degrade badly in
  screen readers, so restraint is not just aesthetic.
