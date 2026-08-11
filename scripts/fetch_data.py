import akshare as ak
import pandas as pd
from datetime import datetime

today_str = datetime.now().strftime("%Y-%m-%d")

# 1. 行业板块资金流排名（今日）
df_industry = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业板块")
df_industry.to_csv(f"report/{today_str}/industry_raw.csv", index=False)

# 2. 概念板块资金流排名
df_concept = ak.stock_concept_fund_flow_rank(indicator="今日")
df_concept.to_csv(f"report/{today_str}/concept_raw.csv", index=False)

# 3. 北向资金净流入
df_north = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")
# 取最新一行当日净流入
north_today = df_north[df_north['日期'] == today_str]
north_today.to_csv(f"report/{today_str}/north_flow.csv", index=False)

# 4. 大宗交易（暗盘）当日明细
df_block = ak.stock_dzjy_mrmx(symbol="沪深", start_date=today_str, end_date=today_str)
df_block.to_csv(f"report/{today_str}/block_trade.csv", index=False)
