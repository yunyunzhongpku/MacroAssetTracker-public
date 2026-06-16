# MacroAssetTracker配置文件

# 资产配置
ASSETS = {
    "A股指数": ["000300.SH", "000905.SH", "399006.SZ", "000001.SH", "000016.SH", "000852.SH", "932000.CSI", "868008.WI", "518880.SH"],
    "债券指数": ["CBA00101.CS", "CBA02701.CS", "511260.SH", "511520.SH", "511090.SH"],
    "商品": ["AUFI.WI", "SCFI.WI", "CUFI.WI", "RBFI.WI", "IFI.WI", "SAFI.WI", "JMFI.WI", "AGFI.WI", "ECFI.WI", "LCFI.WI", "CFFI.WI", "LHFI.WI"],
    "海外": ["513500.SH", "513100.SH", "HSI.HI", "HSTECH.HI", "N225.GI", "SX5E.DF", "VN30.GI", "KS11.GI"],
    "海外现货参考": ["SPX.GI", "IXIC.GI"],
    "REITs": ["932006.CSI"]  # 中证REITs指数
}

# 资产名称映射（用于显示）
ASSET_NAMES = {
    # A股指数
    "000300.SH": "沪深300",
    "000905.SH": "中证500", 
    "399006.SZ": "创业板指",
    "000001.SH": "上证指数",
    "000016.SH": "上证50",
    "000852.SH": "中证1000",
    "932000.CSI": "中证2000",
    "868008.WI": "万得微盘股指数",
    "518880.SH": "黄金ETF",
    # 债券指数
    "CBA00101.CS": "中债总财富",
    "CBA02701.CS": "企业债",
    "511260.SH": "十年国债ETF",
    "511520.SH": "政金债ETF",
    "511090.SH": "30年国债ETF",
    # 商品
    "AUFI.WI": "黄金",
    "SCFI.WI": "原油",
    "CUFI.WI": "铜",
    "RBFI.WI": "螺纹钢",
    "IFI.WI": "铁矿",
    "SAFI.WI": "纯碱",
    "JMFI.WI": "焦煤",
    "AGFI.WI": "白银",
    "ECFI.WI": "欧线",
    "LCFI.WI": "碳酸锂",
    "CFFI.WI": "棉花",
    "LHFI.WI": "生猪",
    # 海外
    "513500.SH": "标普500ETF",
    "513100.SH": "纳指ETF",
    "SPX.GI": "标普500(现货)",
    "HSI.HI": "恒生指数",
    "HSTECH.HI": "恒生科技",
    "IXIC.GI": "纳斯达克(现货)",
    "N225.GI": "日经225",
    "SX5E.DF": "欧元区STOXX50",
    "VN30.GI": "越南V30",
    "KS11.GI": "韩国综合",
    # REITs
    "932006.CSI": "中证REITs指数"
}

# 债券收益率配置（单独处理，不包含在基础统计中）
BOND_YIELDS = {
    "美债收益率": ["UST2Y.GBM", "UST10Y.GBM", "UST30Y.GBM"],
    "中国国债收益率": ["TB1Y.WI", "TB2Y.WI", "TB10Y.WI", "TB30Y.WI"]
}

# 债券收益率名称映射
BOND_YIELD_NAMES = {
    "UST2Y.GBM": "2Y美债",
    "UST10Y.GBM": "10Y美债",
    "UST30Y.GBM": "30Y美债",
    "TB1Y.WI": "1Y中国国债",
    "TB2Y.WI": "2Y中国国债",
    "TB10Y.WI": "10Y中国国债",
    "TB30Y.WI": "30Y中国国债"
}

# 获取所有资产代码的扁平列表（用于基础统计分析）
ALL_SYMBOLS = []
for category_symbols in ASSETS.values():
    ALL_SYMBOLS.extend(category_symbols)

# 获取所有债券收益率代码的扁平列表
ALL_BOND_YIELDS = []
for category_yields in BOND_YIELDS.values():
    ALL_BOND_YIELDS.extend(category_yields)

# 数据日期范围（设置较广的范围以支持用户灵活选择）
START_DATE = "2020-01-01"
END_DATE = "2026-4-10"

# 界面配置
PAGE_TITLE = "MacroAssetTracker"
THEME_COLOR = "blue"

# 文件路径配置
import os
# 获取当前文件的目录，然后找到项目根目录的data文件夹
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 从src回到项目根目录
DATA_DIR = os.path.join(project_root, "data")
PRICES_FILE = os.path.join(DATA_DIR, "prices.csv")
RETURNS_FILE = os.path.join(DATA_DIR, "returns.csv")