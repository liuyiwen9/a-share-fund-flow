import pandas as pd
import json
import os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
data_dir = f"docs/{today}"

# 检查数据文件是否存在
industry_file = f"{data_dir}/industry.csv"
if not os.path.exists(industry_file):
    # 无数据时生成一个“空报告”的 JSON，让 build_report 正常工作
    empty_result = {
        "date": today,
        "industry_top10": [],
        "industry_bottom10": [],
        "concept_top10": [],
        "concept_bottom10": [],
        "north_net_flow": "N/A",
        "big_discount_count": 0,
        "big_discount_list": [],
        "note": "⚠️ 数据获取失败，请检查 fetch_data.py 中的函数名是否匹配 AKshare 版本"
    }
    with open(f"{data_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(empty_result, f, ensure_ascii=False, indent=2)
    print("⚠️ 无数据文件，已生成空报告，网站不会报错。")
    exit(0)

# 如果有数据，从这里开始正常读取和分析...
ind = pd.read_csv(industry_file)
print("行业板块 CSV 列名：", ind.columns.tolist())

# AKshare 这个接口的列名通常是：'板块', '今日主力净流入-净额', '今日超大单净流入-净额', '今日大单净流入-净额', '今日中单净流入-净额', '今日小单净流入-净额', '今日主力净流入-净占比', '今日涨跌幅', ... 
# 我们优先用“主力净流入-净额”作为主力资金，如果列名不同，运行后可看列名调整
# 做简单适配：尝试匹配常见列名
col_map = {}
for col in ind.columns:
    if '主力净流入-净额' in col or '主力净流入' in col and '占比' not in col:
        col_map['主力净流入'] = col
    if '超大单净流入-净额' in col or '超大单净流入' in col:
        col_map['超大单'] = col
    if '大单净流入-净额' in col or '大单净流入' in col:
        col_map['大单'] = col
    if '中单净流入-净额' in col or '中单净流入' in col:
        col_map['中单'] = col
    if '小单净流入-净额' in col or '小单净流入' in col:
        col_map['小单'] = col
    if '主力净流入-净占比' in col or '主力净占比' in col:
        col_map['主力净占比'] = col
    if '涨跌幅' in col:
        col_map['涨跌幅'] = col
    if '板块' in col:
        col_map['板块'] = col

# 如果匹配不上，就打印列名让人检查
if '主力净流入' not in col_map:
    print("行业板块列名：", ind.columns.tolist())
    raise KeyError("请根据打印的列名修改代码")

ind['主力净流入'] = ind[col_map['主力净流入']]
ind['散户净流入'] = ind[col_map['中单']] + ind[col_map['小单']]
ind_top10 = ind.nlargest(10, '主力净流入')
ind_bottom10 = ind.nsmallest(10, '主力净流入')

# ---- 处理概念板块 ----
con = pd.read_csv(f"{data_dir}/concept.csv")
print("概念板块 CSV 列名：", con.columns.tolist())
# 概念板块列名类似，可以用同样的列名匹配逻辑（这里简化，假设列名一致）
# 可以复用上面匹配到的字段名，但概念可能没有'板块'而是'概念名称'，简单处理：
con_col_map = {}
for col in con.columns:
    if '主力净流入-净额' in col or ('主力净流入' in col and '占比' not in col):
        con_col_map['主力净流入'] = col
    if '中单净流入' in col:
        con_col_map['中单'] = col
    if '小单净流入' in col:
        con_col_map['小单'] = col
    if '概念' in col:
        con_col_map['概念'] = col
    if '涨跌幅' in col:
        con_col_map['涨跌幅'] = col

con['主力净流入'] = con[con_col_map['主力净流入']]
con['散户净流入'] = con[con_col_map['中单']] + con[con_col_map['小单']]
con_top10 = con.nlargest(10, '主力净流入')
con_bottom10 = con.nsmallest(10, '主力净流入')

# ---- 北向资金 ----
north = pd.read_csv(f"{data_dir}/north.csv")
north_value = north.iloc[0]['当日净流入'] if '当日净流入' in north.columns else "N/A"

# ---- 大宗交易异动 ----
block = pd.read_csv(f"{data_dir}/block_trade.csv")
if not block.empty:
    if '成交价' in block.columns and '收盘价' in block.columns:
        block['折价率'] = (block['成交价'] / block['收盘价'] - 1) * 100
        big_discount = block[block['折价率'] < -8]   # 折价超8%
    else:
        big_discount = pd.DataFrame()
else:
    big_discount = pd.DataFrame()

# 打包结果
result = {
    "date": today,
    "industry_top10": ind_top10[['板块', '主力净流入', '散户净流入', '涨跌幅']].to_dict(orient='records'),
    "industry_bottom10": ind_bottom10[['板块', '主力净流入', '散户净流入', '涨跌幅']].to_dict(orient='records'),
    "concept_top10": con_top10[['概念名称', '主力净流入', '散户净流入', '涨跌幅']].to_dict(orient='records'),
    "concept_bottom10": con_bottom10[['概念名称', '主力净流入', '散户净流入', '涨跌幅']].to_dict(orient='records'),
    "north_net_flow": north_value,
    "big_discount_count": len(big_discount),
    "big_discount_list": big_discount[['证券简称', '成交价', '收盘价', '折价率']].to_dict(orient='records') if not big_discount.empty else []
}

with open(f"{data_dir}/analysis.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("分析完成，已生成 analysis.json")
with open(f"report/{today_str}/analysis_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
