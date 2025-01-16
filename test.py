import tushare as ts
# 初始化pro接口
pro = ts.pro_api('bcfab7bccd8e066c2290c423bdb2d399b34690884be7b1ae05db1011')

# 拉取数据
df = pro.index_basic(**{
    "ts_code": 600371,
    "market": "",
    "publisher": "",
    "category": "",
    "name": "",
    "limit": "",
    "offset": ""
}, fields=[
    "ts_code",
    "name",
    "market",
    "publisher",
    "category",
    "base_date",
    "base_point",
    "list_date"
])
print(df)