import graphviz

# 紧凑型折叠布局 (Compact Matrix Layout)
dot = graphviz.Digraph('visual_servoing', comment='Compact Flow')
dot.attr(rankdir='TB', size='10,10', fontname='SimSun', compound='true')

# Default node style
dot.attr('node', shape='box', style='filled', fillcolor='#ffffff', fontname='SimSun')

# Row 1: 初始阶段
with dot.subgraph(name='cluster_0') as c:
    c.attr(style='invis')
    c.node('Start', '开始', shape='ellipse', fillcolor='#e1f5fe')
    c.node('Capture', '1.图像采集')
    c.node('Detect', '2.表盘识别?', shape='diamond', fillcolor='#fff9c4')
    c.node('Search', '局部搜索')
    c.node('GetCoords', '3.提取坐标', fillcolor='#c8e6c9')
    c.attr(rank='same') # 强制在同一行

# Row 2: 核心计算与执行
with dot.subgraph(name='cluster_1') as c:
    c.attr(style='invis')
    c.node('CalcDiff', '4.计算偏差')
    c.node('Normalize', '5.归一化')
    c.node('MapPTZ', '6.映射指令')
    c.node('MovePTZ', '7.执行运动')
    c.node('Wait', '8.等待稳定')
    c.attr(rank='same') # 强制在同一行

# Row 3: 验证与结束
with dot.subgraph(name='cluster_2') as c:
    c.attr(style='invis')
    c.node('ReCapture', '9.再次采集')
    c.node('CheckCenter', '10.居中?', shape='diamond', fillcolor='#fff9c4')
    c.node('Zoom', '11.变焦聚焦')
    c.node('Read', '12.拍照读数')
    c.node('End', '结束', shape='ellipse', fillcolor='#e1f5fe')
    c.attr(rank='same') # 强制在同一行

# --- 连接关系 ---

# 第一行内部
dot.edge('Start', 'Capture')
dot.edge('Capture', 'Detect')
dot.edge('Detect', 'Search', label='否')
dot.edge('Search', 'Capture') # 局部回环
dot.edge('Detect', 'GetCoords', label='是')

# 换行连接 (Row 1 -> Row 2)
dot.edge('GetCoords', 'CalcDiff')

# 第二行内部
dot.edge('CalcDiff', 'Normalize')
dot.edge('Normalize', 'MapPTZ')
dot.edge('MapPTZ', 'MovePTZ')
dot.edge('MovePTZ', 'Wait')

# 换行连接 (Row 2 -> Row 3)
dot.edge('Wait', 'ReCapture')

# 第三行内部
dot.edge('ReCapture', 'CheckCenter')
dot.edge('CheckCenter', 'Zoom', label='是')
dot.edge('Zoom', 'Read')
dot.edge('Read', 'End')

# 跨行大回环 (Row 3 -> Row 2)
# 使用 dashed 虚线表示反馈路径，constraint=false 避免破坏布局
dot.edge('CheckCenter', 'CalcDiff', label='否(微调)', constraint='false', style='dashed', color='blue')

# 生成
output_path = '/workspace/docs/visual_servoing_flow_compact'
dot.render(output_path, format='svg', cleanup=True)
print(f"Graph generated at {output_path}.svg")