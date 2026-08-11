import akshare as ak
import pandas as pd
import os, sys, traceback
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
        print(f"今天 {today} 不是交易日，创建标记文件退出")
        with open(f"{output_dir}/holiday.flag", "w") as f:
            f.write("holiday")
        sys.exit(0)
    else:
        print(f"今天 {today} 是交易日，继续获取数据")
except Exception as e:
    print(f"交易日历获取失败，默认继续: {e}")

# ---------- 1. 行业板块资金流 ----------
try:
    # 新版推荐用 stock_board_industry_fund_flow_rank
    df_ind = ak.stock_board_industry_fund_flow_rank(indicator="今日")
    df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
    print("✅ 行业板块数据已保存")
except Exception as e:
    print(f"❌ 行业板块数据失败: {e}")
    # 备用接口
    try:
        df_ind = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业板块")
        df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
        print("✅ 通过备用接口获取行业板块数据")
    except Exception as e2:
        print(f"备用行业接口也失败: {e2}")

# ---------- 2. 概念板块资金流 ----------
try:
    # 新版推荐 stock_board_concept_fund_flow_rank
    df_con = ak.stock_board_concept_fund_flow_rank(indicator="今日")
    df_con.to_csv(f"{output_dir}/concept.csv", index=False)
    print("✅ 概念板块数据已保存")
except Exception as e:
    print(f"❌ 概念板块数据失败: {e}")
    try:
        # 尝试旧的 stock_concept_fund_flow_rank（部分版本保留）
        df_con = ak.stock_concept_fund_flow_rank(indicator="今日")
        df_con.to_csv(f"{output_dir}/concept.csv", index=False)
        print("✅ 通过备用接口获取概念板块数据")
    except Exception as e2:
        print(f"备用概念接口也失败: {e2}")

# ---------- 3. 北向资金 ----------
try:
    # 新版本北向资金推荐 stock_hsgt_north_net_flow_in_em（但错误显示没有这个属性）
    # 实际可用 stock_hsgt_hist_em(symbol="北上") 获取历史，然后筛选今天
    df_north = ak.stock_hsgt_hist_em(symbol="北上")
    df_north['日期'] = pd.to_datetime(df_north['日期']).dt.strftime("%Y-%m-%d")
    north_today = df_north[df_north['日期'] == today]
    if north_today.empty:
        north_today = df_north.iloc[-1:]  # 取最新一条
    north_today.to_csv(f"{output_dir}/north.csv", index=False)
    print("✅ 北向资金数据已保存")
except Exception as e:
    print(f"❌ 北向资金数据失败: {e}")
    # 备用：直接用当日净流入数据（实时）
    try:
        df_north = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")  # 部分版本仍有
        df_north.to_csv(f"{output_dir}/north.csv", index=False)
        print("✅ 通过备用接口获取北向资金")
    except Exception as e2:
        print(f"备用北向接口也失败: {e2}")

# ---------- 4. 大宗交易（暗盘）----------
try:
    # 大宗交易需要分别获取沪市和深市，然后合并
    df_sh = ak.stock_dzjy_mrmx(symbol="沪市", start_date=today, end_date=today)
    df_sz = ak.stock_dzjy_mrmx(symbol="深市", start_date=today, end_date=today)
    df_block = pd.concat([df_sh, df_sz], ignore_index=True)
    df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
    print("✅ 大宗交易数据已保存")
except Exception as e:
    print(f"❌ 大宗交易数据失败: {e}")
    try:
        # 有些版本支持 symbol="全部"
        df_block = ak.stock_dzjy_mrmx(symbol="全部", start_date=today, end_date=today)
        df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
        print("✅ 通过备用接口获取大宗交易")
    except Exception as e2:
        print(f"备用大宗接口也失败: {e2}")

print("数据获取阶段完成")
