import pandas as pd
import json
import os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
data_dir = f"docs/{today}"

if not os.path.exists(f"{data_dir}/industry.csv"):
    empty_result = {
        "date": today,
        "industry_top10": [],
        "industry_bottom10": [],
        "concept_top10": [],
        "concept_bottom10": [],
        "north_net_flow": "N/A",
        "big_discount_count": 0,
        "big_discount_list": [],
        "note": "⚠️ 今日无数据或非交易日"
    }
    with open(f"{data_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(empty_result, f, ensure_ascii=False, indent=2)
    print("无数据，生成空报告")
    exit(0)

# ---------- 行业板块 ----------
ind = pd.read_csv(f"{data_dir}/industry.csv")
print("行业列名:", ind.columns.tolist())

if '行业' in ind.columns and '净额' in ind.columns:
    ind = ind.rename(columns={'行业': '板块', '净额': '资金净流入', '行业-涨跌幅': '涨跌幅'})
    ind['散户净流入'] = "N/A"
    ind = ind[['板块', '资金净流入', '散户净流入', '涨跌幅']]
    ind['资金净流入'] = pd.to_numeric(ind['资金净流入'], errors='coerce')
    ind = ind.dropna(subset=['资金净流入'])
    ind_top10 = ind.nlargest(10, '资金净流入').to_dict(orient='records')
    ind_bottom10 = ind.nsmallest(10, '资金净流入').to_dict(orient='records')
else:
    ind_top10, ind_bottom10 = [], []

# ---------- 概念板块 ----------
con = pd.read_csv(f"{data_dir}/concept.csv")
print("概念列名:", con.columns.tolist())

if '净额' in con.columns:
    # 确定名称列（概念数据中列名也是'行业'，我们当做概念名称）
    name_col = '概念' if '概念' in con.columns else ('概念名称' if '概念名称' in con.columns else '行业')
    # 确定涨跌幅列
    change_col = '涨跌幅' if '涨跌幅' in con.columns else ('行业-涨跌幅' if '行业-涨跌幅' in con.columns else None)
    
    rename_map = {name_col: '概念名称', '净额': '资金净流入'}
    if change_col:
        rename_map[change_col] = '涨跌幅'
    con = con.rename(columns=rename_map)
    
    con['散户净流入'] = "N/A"
    keep_cols = ['概念名称', '资金净流入', '散户净流入']
    if change_col:
        keep_cols.append('涨跌幅')
    con = con[keep_cols]
    
    con['资金净流入'] = pd.to_numeric(con['资金净流入'], errors='coerce')
    con = con.dropna(subset=['资金净流入'])
    con_top10 = con.nlargest(10, '资金净流入').to_dict(orient='records')
    con_bottom10 = con.nsmallest(10, '资金净流入').to_dict(orient='records')
else:
    con_top10, con_bottom10 = [], []

# ---------- 北向资金 ----------
north_value = "N/A"
try:
    north = pd.read_csv(f"{data_dir}/north.csv")
    print("北向列名:", north.columns.tolist())
    for col in ['净买入', '当日净流入', 'net', '资金净流入', '净额']:
        if col in north.columns:
            north_value = north.iloc[0][col]
            break
except Exception as e:
    print(f"北向资金处理失败: {e}")

# ---------- 大宗交易 ----------
big_discount_count = 0
big_discount_list = []
try:
    block = pd.read_csv(f"{data_dir}/block_trade.csv")
    print("大宗列名:", block.columns.tolist())
    if not block.empty:
        if '成交价' in block.columns and '收盘价' in block.columns:
            block['折价率'] = (block['成交价'] / block['收盘价'] - 1) * 100
            big = block[block['折价率'] < -8]
            big_discount_count = len(big)
            big_discount_list = big[['证券简称', '成交价', '收盘价', '折价率']].to_dict(orient='records') if not big.empty else []
except Exception as e:
    print(f"大宗交易处理失败: {e}")

# ---------- 输出 ----------
result = {
    "date": today,
    "industry_top10": ind_top10,
    "industry_bottom10": ind_bottom10,
    "concept_top10": con_top10,
    "concept_bottom10": con_bottom10,
    "north_net_flow": north_value,
    "big_discount_count": big_discount_count,
    "big_discount_list": big_discount_list
}

with open(f"{data_dir}/analysis.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("分析完成，已生成 analysis.json")
