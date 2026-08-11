import pandas as pd
import json
import os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
data_dir = f"docs/{today}"

if not os.path.exists(f"{data_dir}/industry.csv"):
    empty_result = {
        "date": today,
        "industry_top10": [], "industry_bottom10": [],
        "concept_top10": [], "concept_bottom10": [],
        "north_net_flow": "N/A",
        "big_discount_count": 0, "big_discount_list": []
    }
    with open(f"{data_dir}/analysis.json", "w", encoding="utf-8") as f:
        json.dump(empty_result, f, ensure_ascii=False, indent=2)
    exit(0)

def process_board(df, name_col='行业', prefix=''):
    """处理板块数据，自动识别细分资金还是净额"""
    df = df.copy()
    # 判断是否包含细分列
    has_detail = all(c in df.columns for c in ['超大单净流入', '大单净流入', '中单净流入', '小单净流入'])
    
    if has_detail:
        # 计算主力和散户
        df['主力净流入'] = df['超大单净流入'] + df['大单净流入']
        df['散户净流入'] = df['中单净流入'] + df['小单净流入']
        df['涨跌幅'] = df.get('涨跌幅', df.get(f'{prefix}涨跌幅', None))
    else:
        # 只有总净额
        df['资金净流入'] = df['净额']
        df['散户净流入'] = "N/A"
        df['涨跌幅'] = df.get('涨跌幅', df.get(f'{prefix}涨跌幅', df.get('行业-涨跌幅', None)))
    
    # 统一名称列
    if name_col in df.columns:
        df['板块名称'] = df[name_col]
    elif '名称' in df.columns:
        df['板块名称'] = df['名称']
    else:
        df['板块名称'] = '未知'
    
    # 选取需要的列
    if has_detail:
        cols = ['板块名称', '主力净流入', '散户净流入', '涨跌幅']
    else:
        cols = ['板块名称', '资金净流入', '散户净流入', '涨跌幅']
    
    df = df[cols].copy()
    # 数值列转浮点
    value_col = '主力净流入' if has_detail else '资金净流入'
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    if has_detail:
        df['散户净流入'] = pd.to_numeric(df['散户净流入'], errors='coerce')
    df = df.dropna(subset=[value_col])
    return df, has_detail, value_col

# ---------- 行业板块 ----------
ind = pd.read_csv(f"{data_dir}/industry.csv")
print("行业 CSV 列名:", ind.columns.tolist())

# 尝试寻找名称列
name_col_ind = '板块' if '板块' in ind.columns else ('行业' if '行业' in ind.columns else None)
ind_processed, ind_detail, ind_val_col = process_board(ind, name_col=name_col_ind, prefix='行业-')

ind_top10 = ind_processed.nlargest(10, ind_val_col).to_dict(orient='records')
ind_bottom10 = ind_processed.nsmallest(10, ind_val_col).to_dict(orient='records')

# ---------- 概念板块 ----------
con = pd.read_csv(f"{data_dir}/concept.csv")
print("概念 CSV 列名:", con.columns.tolist())

name_col_con = '概念' if '概念' in con.columns else ('概念名称' if '概念名称' in con.columns else '行业')
con_processed, con_detail, con_val_col = process_board(con, name_col=name_col_con, prefix='概念-')

con_top10 = con_processed.nlargest(10, con_val_col).to_dict(orient='records')
con_bottom10 = con_processed.nsmallest(10, con_val_col).to_dict(orient='records')

# ---------- 北向资金 ----------
north_value = "N/A"
try:
    north = pd.read_csv(f"{data_dir}/north.csv")
    if not north.empty:
        for col in ['净买入', '当日净流入', '资金净流入', '成交净买额']:
            if col in north.columns:
                north_value = north.iloc[0][col]
                break
    else:
        north_value = "N/A"
except Exception as e:
    print(f"北向处理失败: {e}")
    north_value = "N/A"

# ---------- 大宗交易 ----------
big_discount_count = 0
big_discount_list = []
try:
    block = pd.read_csv(f"{data_dir}/block_trade.csv")
    if not block.empty and '成交价' in block.columns and '收盘价' in block.columns:
        block['折价率'] = (block['成交价'] / block['收盘价'] - 1) * 100
        big = block[block['折价率'] < -8]
        big_discount_count = len(big)
        big_discount_list = big[['证券简称','成交价','收盘价','折价率']].to_dict(orient='records') if not big.empty else []
except FileNotFoundError:
    print("大宗交易文件不存在，跳过")
    big_discount_count = 0
    big_discount_list = []
# ---------- 最终 JSON ----------
result = {
    "date": today,
    "industry_top10": ind_top10,
    "industry_bottom10": ind_bottom10,
    "concept_top10": con_top10,
    "concept_bottom10": con_bottom10,
    "north_net_flow": north_value,
    "big_discount_count": big_discount_count,
    "big_discount_list": big_discount_list,
    "industry_has_detail": ind_detail,
    "concept_has_detail": con_detail
}

with open(f"{data_dir}/analysis.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ 分析完成，已生成 analysis.json")
