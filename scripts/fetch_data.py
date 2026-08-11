import akshare as ak
import pandas as pd
import os, sys
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
output_dir = f"docs/{today}"
os.makedirs(output_dir, exist_ok=True)

print(f"AKshare 版本: {ak.__version__}")

# 交易日判断
try:
    trade_date_df = ak.tool_trade_date_hist_sina()
    trade_dates = trade_date_df['trade_date'].astype(str).tolist()
    if today not in trade_dates:
        print(f"今天 {today} 不是交易日，退出")
        with open(f"{output_dir}/holiday.flag", "w") as f:
            f.write("holiday")
        sys.exit(0)
    print("是交易日，继续...")
except Exception as e:
    print(f"交易日判断失败，继续: {e}")

# 行业板块
try:
    df_ind = ak.stock_fund_flow_industry()
    print("行业列名:", df_ind.columns.tolist())
    df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
    print("✅ 行业板块数据 OK")
except Exception as e:
    print(f"行业板块失败: {e}")

# 概念板块
try:
    df_con = ak.stock_fund_flow_concept()
    print("概念列名:", df_con.columns.tolist())
    df_con.to_csv(f"{output_dir}/concept.csv", index=False)
    print("✅ 概念板块数据 OK")
except Exception as e:
    print(f"概念板块失败: {e}")

# 北向资金
try:
    df_north = ak.stock_hsgt_fund_flow_summary_em()
    print("北向列名:", df_north.columns.tolist())
    # 筛选今日数据
    if '日期' in df_north.columns:
        north_today = df_north[df_north['日期'] == today]
    elif 'date' in df_north.columns:
        north_today = df_north[df_north['date'] == today]
    else:
        north_today = df_north.iloc[-1:]
    north_today.to_csv(f"{output_dir}/north.csv", index=False)
    print("✅ 北向资金数据 OK")
except Exception as e:
    print(f"北向资金失败: {e}")

# 大宗交易
try:
    # 尝试直接调，不加 symbol 参数
    df_block = ak.stock_dzjy_mrmx(start_date=today, end_date=today)
    print("大宗列名:", df_block.columns.tolist() if not df_block.empty else "空")
    df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
    print("✅ 大宗交易数据 OK")
except Exception as e:
    print(f"大宗交易失败: {e}")

print("数据获取阶段完成")
