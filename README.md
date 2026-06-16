# MacroAssetTracker

多资产行情与风险分析仪表板（Streamlit）。跟踪中国与海外股票、债券、商品、REITs 等大类资产，提供价格趋势、相关性与风险指标的交互式可视化。

> ⚠️ 数据来自 Wind（万得），仅供学习/演示，非投资建议，且不在代码 MIT 许可范围内——详见 [DATA_NOTICE.md](DATA_NOTICE.md)。

## 在线访问

部署于 Streamlit Community Cloud：https://macroassettracker-public-6gmtj9uqqwkm8c26rguodo.streamlit.app

## 功能

- 📊 **行情总览** — 价格趋势与标准化比较，支持时间范围与资产筛选
- 🔗 **相关性与风险** — 相关性热力图、VaR/CVaR/Sortino/最大回撤等风险指标
- ⚙️ **系统管理** — 数据状态与覆盖范围

## 本地运行

需要 Python ≥ 3.10（代码使用了 `X | None` 类型注解）。推荐 3.12。

```bash
pip install -r requirements.txt
streamlit run src/main.py
```
浏览器打开 http://localhost:8501

## 数据

`data/prices.csv` / `data/returns.csv` 为历史快照。本公开版不含数据获取代码，更新需手动替换 CSV 后重新部署。

## 许可

代码以 MIT 许可发布（见 [LICENSE](LICENSE)）；数据文件不在此范围内（见 [DATA_NOTICE.md](DATA_NOTICE.md)）。
