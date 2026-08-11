import json
import os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
data_dir = f"docs/{today}"
json_path = f"{data_dir}/analysis.json"

if not os.path.exists(json_path):
    print("无分析数据")
    exit(0)

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

def gen_table(headers, rows, col_keys):
    html = '<table border="1" cellpadding="5" style="border-collapse:collapse; width:100%;">'
    html += '<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>'
    for row in rows:
        html += '<tr>' + ''.join(f'<td>{row.get(k, "")}</td>' for k in col_keys) + '</tr>'
    html += '</table>'
    return html

# 判断使用哪个资金字段
ind_key = '主力净流入' if data.get('industry_has_detail') else '资金净流入'
con_key = '主力净流入' if data.get('concept_has_detail') else '资金净流入'

html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>A股资金分析 - {today}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 960px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1, h2 {{ color: #2c3e50; }}
        .red {{ color: #e74c3c; }}
        .green {{ color: #27ae60; }}
        table {{ margin: 15px 0; }}
        th {{ background: #34495e; color: white; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
    </style>
</head>
<body>
<div class="container">
    <h1>📊 A股主力资金分析报告</h1>
    <p><strong>日期：{today}</strong>  |  北向资金净流入：
    <span class="{ 
        'red' if isinstance(data['north_net_flow'], (int, float)) and data['north_net_flow'] < 0 
        else 'green' if isinstance(data['north_net_flow'], (int, float)) 
        else '' 
    }">
    {data['north_net_flow']}{' 亿' if isinstance(data['north_net_flow'], (int, float)) else ''}
    </span></p>

    <h2>🏭 行业板块{'主力' if data.get('industry_has_detail') else '资金'}净流入 TOP10</h2>
    {gen_table(['板块', f'{ind_key}(亿)', '散户净流入', '涨跌幅(%)'], 
               data['industry_top10'], 
               ['板块名称', ind_key, '散户净流入', '涨跌幅'])}

    <h2>📉 行业板块{'主力' if data.get('industry_has_detail') else '资金'}净流出 TOP10</h2>
    {gen_table(['板块', f'{ind_key}(亿)', '散户净流入', '涨跌幅(%)'], 
               data['industry_bottom10'], 
               ['板块名称', ind_key, '散户净流入', '涨跌幅'])}

    <h2>💡 概念板块{'主力' if data.get('concept_has_detail') else '资金'}净流入 TOP10</h2>
    {gen_table(['概念', f'{con_key}(亿)', '散户净流入', '涨跌幅(%)'], 
               data['concept_top10'], 
               ['板块名称', con_key, '散户净流入', '涨跌幅'])}

    <h2>⚠️ 概念板块{'主力' if data.get('concept_has_detail') else '资金'}净流出 TOP10</h2>
    {gen_table(['概念', f'{con_key}(亿)', '散户净流入', '涨跌幅(%)'], 
               data['concept_bottom10'], 
               ['板块名称', con_key, '散户净流入', '涨跌幅'])}

    <h2>🕵️ 大宗交易异动（折价>8%）</h2>
    {"<p>今日无非正常折价大宗交易</p>" if data['big_discount_count'] == 0 else gen_table(['股票', '成交价', '收盘价', '折价率(%)'], data['big_discount_list'], ['证券简称', '成交价', '收盘价', '折价率'])}
    
    <p style="color:#666; font-size:14px;">数据来源：AKshare | 自动更新于 GitHub Actions</p>
</div>
</body>
</html>"""

with open(f"{data_dir}/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"当天报告已生成: {data_dir}/index.html")

# ---- 首页更新 ----
dates = []
for d in os.listdir("docs"):
    if os.path.isdir(f"docs/{d}") and len(d) == 10 and d[4] == '-':
        dates.append(d)
dates.sort(reverse=True)

links_html = "".join(f'<li><a href="{d}/">{d}</a></li>' for d in dates)

index_html = f"""<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8"><title>A股资金流日报</title></head>
<body>
<h1>A股资金流日报列表</h1>
<ul>{links_html}</ul>
<p>点击日期查看当日详细报告</p>
</body>
</html>"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

print("首页已更新")
