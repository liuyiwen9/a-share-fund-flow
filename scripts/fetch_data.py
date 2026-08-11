import akshare as ak
import pandas as pd
import requests
import os, sys, json
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
output_dir = f"docs/{today}"
os.makedirs(output_dir, exist_ok=True)

print(f"AKshare 版本: {ak.__version__}")

# 交易日判断（仍用 AKshare）
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

# ================= 东方财富行业板块资金流（细分）=================
print("\n--- 行业板块资金流（东方财富）---")
try:
    # 东方财富行业板块资金流接口
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fid": "f62",
        "fs": "m:90+t2",
        "fields": "f12,f14,f62,f66,f69,f70,f72,f184,f3"
    }
    resp = requests.get(url, params=params, timeout=10)
    data_json = resp.json()
    items = data_json["data"]["diff"]
    df_ind = pd.DataFrame(items)
    # 列名映射：f14=板块名称, f62=主力净流入, f66=超大单净流入, f69=大单净流入, f70=中单净流入, f72=小单净流入, f184=成交额, f3=涨跌幅
    df_ind = df_ind.rename(columns={
        "f14": "板块", "f62": "主力净流入", "f66": "超大单净流入",
        "f69": "大单净流入", "f70": "中单净流入", "f72": "小单净流入",
        "f184": "成交额", "f3": "涨跌幅"
    })
    # 保留必要列
    df_ind = df_ind[["板块", "主力净流入", "超大单净流入", "大单净流入", "中单净流入", "小单净流入", "涨跌幅"]]
    df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
    print("✅ 行业细分数据已保存，列名:", df_ind.columns.tolist())
except Exception as e:
    print(f"❌ 行业细分失败: {e}，降级使用 AKshare 总净额接口")
    try:
        df_ind = ak.stock_fund_flow_industry()
        df_ind.to_csv(f"{output_dir}/industry.csv", index=False)
        print("✅ 已降级为总净额数据")
    except Exception as e2:
        print(f"行业板块完全失败: {e2}")

# ================= 东方财富概念板块资金流（细分）=================
print("\n--- 概念板块资金流（东方财富）---")
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
        "fs": "m:90+t3",   # 概念板块用 t3
        "fields": "f12,f14,f62,f66,f69,f70,f72,f184,f3"
    }
    resp = requests.get(url, params=params, timeout=10)
    data_json = resp.json()
    items = data_json["data"]["diff"]
    df_con = pd.DataFrame(items)
    df_con = df_con.rename(columns={
        "f14": "板块", "f62": "主力净流入", "f66": "超大单净流入",
        "f69": "大单净流入", "f70": "中单净流入", "f72": "小单净流入",
        "f184": "成交额", "f3": "涨跌幅"
    })
    df_con = df_con[["板块", "主力净流入", "超大单净流入", "大单净流入", "中单净流入", "小单净流入", "涨跌幅"]]
    df_con.to_csv(f"{output_dir}/concept.csv", index=False)
    print("✅ 概念细分数据已保存")
except Exception as e:
    print(f"❌ 概念细分失败: {e}，降级")
    try:
        df_con = ak.stock_fund_flow_concept()
        df_con.to_csv(f"{output_dir}/concept.csv", index=False)
        print("✅ 已降级为总净额数据")
    except Exception as e2:
        print(f"概念板块完全失败: {e2}")

# ================= 北向资金 ==================
print("\n--- 北向资金 ---")
try:
    df_north = ak.stock_hsgt_fund_flow_summary_em()
    # 筛选今日
    if '交易日' in df_north.columns:
        north_today = df_north[df_north['交易日'] == today]
    elif '日期' in df_north.columns:
        north_today = df_north[df_north['日期'] == today]
    else:
        north_today = df_north.iloc[-1:]
    north_today.to_csv(f"{output_dir}/north.csv", index=False)
    print("✅ 北向资金已保存")
except Exception as e:
    print(f"❌ 北向失败: {e}")

# ================= 大宗交易（容错处理）=================
print("\n--- 大宗交易 ---")
try:
    # 使用 AKshare 获取大宗交易，捕获可能的 None 数据
    df_block = ak.stock_dzjy_mrmx(start_date=today, end_date=today)
    if df_block is not None and not df_block.empty:
        df_block.to_csv(f"{output_dir}/block_trade.csv", index=False)
        print("✅ 大宗交易已保存")
    else:
        print("⚠️ 当日无大宗交易数据")
except Exception as e:
    print(f"⚠️ 大宗交易获取失败（可能当日无数据）: {e}")

print("\n所有数据获取完毕")
