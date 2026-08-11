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
    else:
        print("是交易日，继续...")
except Exception as e:
    print(f"交易日判断失败，继续: {e}")

# ================= 行业板块资金流 =================
print("\n--- 行业板块资金流 ---")
try:
    # 主攻函数：stock_fund_flow_industry
    df_ind = ak.stock_fund_flow_industry()
    print("stock_fund_flow_industry 返回列名:", df_ind.columns.tolist())
    print("前2行:")
    print(df_ind.head(2))
    df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
    print("✅ 行业板块数据已保存")
except Exception as e:
    print(f"❌ stock_fund_flow_industry 失败: {e}")
    # 备用：stock_sector_fund_flow_rank 不带 sector_type 参数试试
    try:
        df_ind = ak.stock_sector_fund_flow_rank(indicator="今日")
        print("备用 stock_sector_fund_flow_rank 返回列名:", df_ind.columns.tolist())
        df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
        print("✅ 通过备用接口获取行业板块数据")
    except Exception as e2:
        print(f"备用行业接口也失败: {e2}")

# ================= 概念板块资金流 =================
print("\n--- 概念板块资金流 ---")
try:
    # 主攻函数：stock_fund_flow_concept
    df_con = ak.stock_fund_flow_concept()
    print("stock_fund_flow_concept 返回列名:", df_con.columns.tolist())
    print("前2行:")
    print(df_con.head(2))
    df_con.to_csv(f"{output_dir}/concept.csv", index=False)
    print("✅ 概念板块数据已保存")
except Exception as e:
    print(f"❌ stock_fund_flow_concept 失败: {e}")

# ================= 北向资金 =================
print("\n--- 北向资金 ---")
try:
    # 函数列表里有 stock_hsgt_fund_flow_summary_em，试试
    df_north = ak.stock_hsgt_fund_flow_summary_em()
    print("stock_hsgt_fund_flow_summary_em 返回列名:", df_north.columns.tolist())
    print("前2行:")
    print(df_north.head(2))
    # 筛选今天的数据
    if '日期' in df_north.columns:
        north_today = df_north[df_north['日期'] == today]
    elif 'date' in df_north.columns:
        north_today = df_north[df_north['date'] == today]
    else:
        north_today = df_north.iloc[-1:]  # 拿最后一行
    north_today.to_csv(f"{output_dir}/north.csv", index=False)
    print("✅ 北向资金数据已保存")
except Exception as e:
    print(f"❌ 北向资金失败: {e}")

# ================= 大宗交易（暗盘）=================
print("\n--- 大宗交易 ---")
try:
    # stock_dzjy_mrmx 存在，尝试不同的 symbol 参数
    # 先试 '沪市'
    try:
        df_sh = ak.stock_dzjy_mrmx(symbol="沪市", start_date=today, end_date=today)
    except:
        # 也许不需要 symbol 参数？或者用 symbol="全部"
        df_sh = ak.stock_dzjy_mrmx(start_date=today, end_date=today)
    try:
        df_sz = ak.stock_dzjy_mrmx(symbol="深市", start_date=today, end_date=today)
    except:
        df_sz = pd.DataFrame()
    df_block = pd.concat([df_sh, df_sz], ignore_index=True)
    if df_block.empty:
        # 如果分市不行，试试直接调一个
        df_block = ak.stock_dzjy_mrmx(start_date=today, end_date=today)
    print("stock_dzjy_mrmx 返回列名:", df_block.columns.tolist() if not df_block.empty else "空")
    df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
    print("✅ 大宗交易数据已保存")
except Exception as e:
    print(f"❌ 大宗交易失败: {e}")

print("\n数据获取阶段全部完成")
