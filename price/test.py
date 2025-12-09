import re
import html

text = r"""&quot;htmlContentEncoded&quot;: &quot;\u003C!doctype html&gt;
&lt;div id=\&quot;ad\&quot; style=\&quot;width: 100%; height: 100%;\&quot;&gt;
&lt;div style=\&quot;overflow:hidden;width:100%;height:100%\&quot;&gt;
&lt;span aria-hidden=\&quot;true\&quot; id=\&quot;adLink-label\&quot; style=\&quot;...\&quot;&gt;
Annuncio sponsorizzato.
Logo del brand.
Immagine del prodotto.
TCL 50V6C TV 50&amp;quot; 4K UHD Smart LED TV, 4K HDR, Google TV con design senza bordi ...
299.9&lt;/span&gt;&lt;div style="""

# 1. HTML 解码
decoded_text = html.unescape(text)

# 2. 去掉反斜杠
decoded_text = decoded_text.replace('\\', '')

# 3. 匹配 <div id="ad"...> 到 </span><div style= 之间内容
pattern = r'<div id="ad" style="width: 100%; height: 100%;">(.*?)</span><div style='
match = re.search(pattern, decoded_text, re.S)  # re.S 让 . 匹配换行

if match:
    content = match.group(1).strip()
    print("匹配内容：\n", content)
    # 提取数字（整数或小数）
    price_match = re.search(r'(\d+(?:\.\d+)?)', content)
    if price_match:
        print("找到的价格：", price_match.group(1))
    else:
        print("未找到价格")
else:
    print("未找到指定内容")
