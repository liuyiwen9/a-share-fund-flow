import akshare as ak
import pandas as pd
import os, sys
from datetime import datetime, timedelta

# 判断今天是不是交易日，不是的话直接退出
today = datetime.now().strftime("%Y-%m-%d")
try:
    trade_date_df = ak.tool_trade_date_hist_sina()
    trade_dates = trade_date_df['trade_date'].astype(str).tolist()
    if today not in trade_dates:
        print("今天不是交易日，脚本自动退出")
        sys.exit(0)
except Exception as e:
    print(f"交易日历获取失败，继续运行: {e}")

# 创建当天输出目录 docs/2026-08-11/
output_dir = f"docs/{today}"
os.makedirs(output_dir, exist_ok=True)

# ---------- 1. 行业板块资金流 ----------
try:
    df_ind = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业板块")
    df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
    print("行业板块数据已获取")
except Exception as e:
    print(f"行业板块数据失败: {e}")

# ---------- 2. 概念板块资金流 ----------
try:
    df_con = ak.stock_concept_fund_flow_rank(indicator="今日")
    df_con.to_csv(f"{output_dir}/concept.csv", index=False)
    print("概念板块数据已获取")
except Exception as e:
    print(f"概念板块数据失败: {e}")

# ---------- 3. 北向资金 ----------
try:
    df_north = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")
    # 找今天的净流入（日期列可能是'date'或'日期'，这里用简单方法获取最后一行）
    north_today = df_north[df_north['日期'] == today]
    if north_today.empty:
        # 如果没找到当天数据，用最近一条
        north_today = df_north.iloc[-1:]
    north_today.to_csv(f"{output_dir}/north.csv", index=False)
    print("北向资金数据已获取")
except Exception as e:
    print(f"北向资金数据失败: {e}")

# ---------- 4. 大宗交易（暗盘）----------
try:
    df_block = ak.stock_dzjy_mrmx(symbol="沪深", start_date=today, end_date=today)
    df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
    print("大宗交易数据已获取")
except Exception as e:
    print(f"大宗交易数据失败: {e}")

print("数据获取阶段完成")
