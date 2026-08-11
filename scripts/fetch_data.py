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

# ================= 1. 行业板块资金流（优先使用细分接口）=================
print("\n--- 行业板块资金流 ---")
try:
    # 尝试使用 stock_sector_fund_flow_rank 获取细分资金（主力、超大单、大单、中单、小单）
    df_ind = ak.stock_sector_fund_flow_rank(indicator="今日")
    print("✅ stock_sector_fund_flow_rank 成功，列名:", df_ind.columns.tolist())
    df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
except Exception as e:
    print(f"❌ 细分接口失败: {e}，降级到 stock_fund_flow_industry")
    try:
        df_ind = ak.stock_fund_flow_industry()
        print("✅ stock_fund_flow_industry 成功，列名:", df_ind.columns.tolist())
        df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
    except Exception as e2:
        print(f"❌ 行业板块数据完全获取失败: {e2}")
        traceback.print_exc()

# ================= 2. 概念板块资金流（同样优先细分接口）=================
print("\n--- 概念板块资金流 ---")
try:
    # 概念板块也可用 stock_sector_fund_flow_rank，部分版本需要 sector_type 参数，这里不加试试
    df_con = ak.stock_sector_fund_flow_rank(indicator="今日")
    print("✅ 概念(同接口)成功，列名:", df_con.columns.tolist())
    df_con.to_csv(f"{output_dir}/concept.csv", index=False)
except Exception as e:
    print(f"❌ 概念细分接口失败: {e}，降级到 stock_fund_flow_concept")
    try:
        df_con = ak.stock_fund_flow_concept()
        print("✅ stock_fund_flow_concept 成功，列名:", df_con.columns.tolist())
        df_con.to_csv(f"{output_dir}/concept.csv", index=False)
    except Exception as e2:
        print(f"❌ 概念板块数据完全获取失败: {e2}")
        traceback.print_exc()

# ================= 3. 北向资金 ==================
print("\n--- 北向资金 ---")
try:
    # 使用 stock_hsgt_fund_flow_summary_em 获取北向资金汇总
    df_north = ak.stock_hsgt_fund_flow_summary_em()
    print("北向资金接口返回列名:", df_north.columns.tolist())
    # 筛选今日数据
    if '日期' in df_north.columns:
        north_today = df_north[df_north['日期'] == today]
    elif 'date' in df_north.columns:
        north_today = df_north[df_north['date'] == today]
    else:
        north_today = df_north.iloc[-1:]  # 拿最新一行
    north_today.to_csv(f"{output_dir}/north.csv", index=False)
    print("✅ 北向资金数据已保存")
except Exception as e:
    print(f"❌ 北向资金失败: {e}")
    traceback.print_exc()

# ================= 4. 大宗交易（暗盘）=================
print("\n--- 大宗交易 ---")
try:
    # 直接调用 stock_dzjy_mrmx，尝试不加 symbol 参数获取全部
    df_block = ak.stock_dzjy_mrmx(start_date=today, end_date=today)
    print("大宗交易接口返回列名:", df_block.columns.tolist() if not df_block.empty else "空")
    df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
    print("✅ 大宗交易数据已保存")
except Exception as e:
    print(f"❌ 大宗交易失败: {e}")
    traceback.print_exc()

print("\n数据获取阶段全部完成")
