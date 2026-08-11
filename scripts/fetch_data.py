import akshare as ak
import pandas as pd
import requests
import os, sys, json
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
output_dir = f"docs/{today}"
os.makedirs(output_dir, exist_ok=True)

print(f"AKshare 版本: {ak.__version__}")

# ========== 交易日判断 ==========
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

# ================= 行业板块资金流 =================
print("\n--- 行业板块资金流 ---")
df_ind = None

# 1) 优先尝试东方财富细分接口
try:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fid": "f62",
        "fs": "m:90+t2",                # 行业板块
        "fields": "f12,f14,f62,f66,f69,f70,f72,f184,f3"
    }
    resp = requests.get(url, params=params, timeout=15)
    print("东方财富行业响应长度:", len(resp.text))
    # 如果返回空字符串，直接跳过
    if not resp.text.strip():
        raise ValueError("东方财富行业接口返回空文本")
    data_json = resp.json()
    items = data_json.get("data", {}).get("diff")
    if not items:
        raise ValueError("东方财富行业数据为空列表")
    df_ind = pd.DataFrame(items)
    # 列名映射
    df_ind = df_ind.rename(columns={
        "f14": "板块", "f62": "主力净流入", "f66": "超大单净流入",
        "f69": "大单净流入", "f70": "中单净流入", "f72": "小单净流入",
        "f184": "成交额", "f3": "涨跌幅"
    })
    # 保留关键列
    df_ind = df_ind[["板块", "主力净流入", "超大单净流入", "大单净流入", "中单净流入", "小单净流入", "涨跌幅"]]
    df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
    print("✅ 东方财富行业细分数据已保存")
except Exception as e:
    print(f"东方财富行业接口失败: {e}")

# 2) 降级：尝试 ak.stock_sector_fund_flow_rank 多种参数
if df_ind is None:
    print("尝试 stock_sector_fund_flow_rank ...")
    for sector_type in [None, "行业", "行业板块"]:
        try:
            if sector_type:
                df_ind = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type=sector_type)
            else:
                df_ind = ak.stock_sector_fund_flow_rank(indicator="今日")
            print(f"✅ stock_sector_fund_flow_rank (sector_type={sector_type}) 成功，列名:", df_ind.columns.tolist())
            df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
            break
        except Exception as e:
            print(f"sector_type={sector_type} 失败: {e}")
            df_ind = None

# 3) 最终降级：AKshare 总净额接口
if df_ind is None:
    print("降级到 stock_fund_flow_industry ...")
    try:
        df_ind = ak.stock_fund_flow_industry()
        df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
        print("✅ 已降级为行业总净额数据")
    except Exception as e:
        print(f"❌ 行业板块数据完全获取失败: {e}")

# ================= 概念板块资金流 =================
print("\n--- 概念板块资金流 ---")
df_con = None

# 1) 东方财富概念接口
try:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fid": "f62",
        "fs": "m:90+t3",                # 概念板块
        "fields": "f12,f14,f62,f66,f69,f70,f72,f184,f3"
    }
    resp = requests.get(url, params=params, timeout=15)
    print("东方财富概念响应长度:", len(resp.text))
    if not resp.text.strip():
        raise ValueError("东方财富概念接口返回空文本")
    data_json = resp.json()
    items = data_json.get("data", {}).get("diff")
    if not items:
        raise ValueError("东方财富概念数据为空列表")
    df_con = pd.DataFrame(items)
    df_con = df_con.rename(columns={
        "f14": "板块", "f62": "主力净流入", "f66": "超大单净流入",
        "f69": "大单净流入", "f70": "中单净流入", "f72": "小单净流入",
        "f184": "成交额", "f3": "涨跌幅"
    })
    df_con = df_con[["板块", "主力净流入", "超大单净流入", "大单净流入", "中单净流入", "小单净流入", "涨跌幅"]]
    df_con.to_csv(f"{output_dir}/concept.csv", index=False)
    print("✅ 东方财富概念细分数据已保存")
except Exception as e:
    print(f"东方财富概念接口失败: {e}")

# 2) 降级：stock_sector_fund_flow_rank 尝试
if df_con is None:
    print("尝试 stock_sector_fund_flow_rank 获取概念 ...")
    for sector_type in [None, "概念", "概念板块"]:
        try:
            if sector_type:
                df_con = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type=sector_type)
            else:
                df_con = ak.stock_sector_fund_flow_rank(indicator="今日")
            print(f"✅ stock_sector_fund_flow_rank (sector_type={sector_type}) 成功，列名:", df_con.columns.tolist())
            df_con.to_csv(f"{output_dir}/concept.csv", index=False)
            break
        except Exception as e:
            print(f"sector_type={sector_type} 失败: {e}")
            df_con = None

# 3) 最终降级：总净额接口
if df_con is None:
    print("降级到 stock_fund_flow_concept ...")
    try:
        df_con = ak.stock_fund_flow_concept()
        df_con.to_csv(f"{output_dir}/concept.csv", index=False)
        print("✅ 已降级为概念总净额数据")
    except Exception as e:
        print(f"❌ 概念板块数据完全获取失败: {e}")

# ================= 北向资金 ==================
print("\n--- 北向资金 ---")
try:
    df_north = ak.stock_hsgt_fund_flow_summary_em()
    # 筛选今天的数据（列名可能是 '交易日' 或 '日期'）
    if '交易日' in df_north.columns:
        north_today = df_north[df_north['交易日'] == today]
    elif '日期' in df_north.columns:
        north_today = df_north[df_north['日期'] == today]
    else:
        north_today = df_north.iloc[-1:]  # 取最新一条
    north_today.to_csv(f"{output_dir}/north.csv", index=False)
    print("✅ 北向资金已保存")
except Exception as e:
    print(f"❌ 北向资金获取失败: {e}")

# ================= 大宗交易（暗盘）=================
print("\n--- 大宗交易 ---")
try:
    df_block = ak.stock_dzjy_mrmx(start_date=today, end_date=today)
    if df_block is not None and not df_block.empty:
        df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
        print("✅ 大宗交易已保存")
    else:
        print("⚠️ 当日无大宗交易数据")
except Exception as e:
    print(f"⚠️ 大宗交易获取失败（可能当日无数据）: {e}")

print("\n===== 数据获取阶段全部完成 =====")
