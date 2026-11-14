#!/usr/bin/python3

from pyecharts.charts import Line,Page
from pyecharts import options as opts  # 导入 options 模块以使用图表的配置选项
import platform
import sqlite3


def gen():
    cn = sqlite3.connect('RPiStatus.db')
    cu = cn.cursor()

    textsize = 32
    date_st = []
    time_st = []
    cpu_t = []


    sql = "SELECT *  FROM pistatus order by id desc limit 10 "
    rec = cu.execute(sql)
    # print(type(list(rec)))
    lst = list(rec)
    lst.reverse()

    for line in lst:
        #提取日期和时间
        tm_st = line[1][5:].replace("/","-") +" "+line[2]
        time_st.append(tm_st)
        #提取温度
        cpu_t.append(line[3])

    page = Page(page_title="My RPi Center")
    x_data = time_st
    y_data = cpu_t
   
    line = Line()  # 创建折线图实例
    line.set_global_opts(
        tooltip_opts=opts.TooltipOpts(is_show=False),  # 配置工具提示，不显示
        xaxis_opts=opts.AxisOpts(type_="category"),  # 配置 x 轴类型为类别型
        yaxis_opts=opts.AxisOpts(
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),  # 配置 y 轴类型为数值型，显示轴标记和分割线
    )

    line.add_xaxis(xaxis_data=x_data)  # 添加 x 轴数据
    line.add_yaxis(
        series_name="温度",  # 设置系列的名称
        y_axis=y_data,  # 添加 y 轴数据
        symbol="emptyCircle",  # 设置数据点的样式为空心圆
        is_symbol_show=True,  # 显示数据点的样式
        label_opts=opts.LabelOpts(is_show=False),  # 配置标签，不显示
    )
    line.set_global_opts(title_opts=opts.TitleOpts(title="主标题", subtitle="副标题"))  # 设置图表的标题和副标题
    page.add(line)
    page.render('index.html')


if __name__ == "__main__":
    gen()


