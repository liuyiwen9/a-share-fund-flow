import pandas as pd
import json

today_str = "2026-08-11"  # 由参数传入

# 读取行业
ind = pd.read_csv(f"report/{today_str}/industry_raw.csv")
ind['主力净流入'] = ind['超大单净流入'] + ind['大单净流入']
ind['散户净流入'] = ind['中单净流入'] + ind['小单净流入']
ind['主力净占比'] = (ind['主力净流入'] / ind['成交额']) * 100
ind_top10 = ind.nlargest(10, '主力净流入')
ind_bottom10 = ind.nsmallest(10, '主力净流入')

# 概念同样处理
con = pd.read_csv(f"report/{today_str}/concept_raw.csv")
con['主力净流入'] = con['超大单净流入'] + con['大单净流入']
con['散户净流入'] = con['中单净流入'] + con['小单净流入']
con['主力净占比'] = (con['主力净流入'] / con['成交额']) * 100
con_top10 = con.nlargest(10, '主力净流入')
con_bottom10 = con.nsmallest(10, '主力净流入')

# 北向资金
north = pd.read_csv(f"report/{today_str}/north_flow.csv")
north_value = north['当日净流入'].values[0] if not north.empty else 0

# 暗盘（大宗交易）分析：找出折价率 > 8% 的股票
block = pd.read_csv(f"report/{today_str}/block_trade.csv")
if not block.empty:
    block['折价率'] = (block['成交价'] / block['收盘价'] - 1) * 100
    big_discount = block[block['折价率'] < -8]   # 折价超过8%
else:
    big_discount = pd.DataFrame()

# 打包成 JSON 供网页使用
result = {
    "date": today_str,
    "industry_top10": ind_top10.to_dict(orient='records'),
    "industry_bottom10": ind_bottom10.to_dict(orient='records'),
    "concept_top10": con_top10.to_dict(orient='records'),
    "concept_bottom10": con_bottom10.to_dict(orient='records'),
    "north_net_flow": north_value,
    "big_discount_trades": big_discount.to_dict(orient='records')
}

with open(f"report/{today_str}/analysis_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
