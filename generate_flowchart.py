import graphviz

dot = graphviz.Digraph('visual_servoing', comment='Visual Servoing Flow')
# 关键修改：TB (Top-to-Bottom) 依然是主轴，但我们会利用 subgraph 和 rank 来强制横向排列
dot.attr(rankdir='TB', size='12,12', fontname='SimSun', compound='true')

# Define nodes with styling
dot.attr('node', shape='ellipse', style='filled', fillcolor='#e1f5fe', fontname='SimSun')
dot.node('Start', '开始: 机器人到达粗定位点')

dot.attr('node', shape='box', style='filled', fillcolor='#ffffff', fontname='SimSun')
dot.node('Capture', '采集当前帧图像')

dot.attr('node', shape='diamond', style='filled', fillcolor='#fff9c4', fontname='SimSun')
dot.node('Detect', 'AI模型识别目标表盘')

dot.attr('node', shape='box', style='filled', fillcolor='#ffffff', fontname='SimSun')
dot.node('Search', '执行局部搜索策略')

dot.attr('node', shape='box', style='filled', fillcolor='#c8e6c9', fontname='SimSun')
dot.node('GetCoords', '提取表盘中心坐标')

# Core Logic Subgraph - 使用 LR 让内部节点横向排列
with dot.subgraph(name='cluster_core') as c:
    c.attr(style='dashed', label='核心纠偏算法 (闭环)', fontname='SimSun', bgcolor='#f5f5f5', rankdir='LR')
    c.node('CalcDiff', '计算中心偏差量')
    c.node('Normalize', '坐标归一化')
    c.node('MapPTZ', '映射云台控制量')
    # 强制这些节点在同一层级
    c.attr(rank='same')
    c.edge('CalcDiff', 'Normalize')
    c.edge('Normalize', 'MapPTZ')

# 这里的循环控制部分也尽量紧凑
with dot.subgraph(name='cluster_control') as c:
    c.attr(label='执行与验证', fontname='SimSun', style='invis')
    dot.node('MovePTZ', '执行云台运动')
    dot.node('Wait', '等待稳定')
    dot.node('ReCapture', '再次采集')
    dot.node('CheckCenter', '是否居中?', shape='diamond', fillcolor='#fff9c4')
    
    # 将这几个步骤横向排列，节省纵向空间
    c.attr(rank='same') 
    # 注意：rank=same 对边连接有影响，我们通过隐式布局控制

dot.attr('node', shape='box', style='filled', fillcolor='#c8e6c9', fontname='SimSun')
# 最后的动作也横向放
with dot.subgraph(name='cluster_end_action') as c:
    c.attr(rank='same')
    c.node('Zoom', '变焦 & 聚焦')
    c.node('Read', '拍照 & 读数')
    c.node('End', '结束', shape='ellipse', fillcolor='#e1f5fe')

# Define edges
dot.edge('Start', 'Capture')
dot.edge('Capture', 'Detect')
dot.edge('Detect', 'Search', label='未识别')
dot.edge('Search', 'Capture')
dot.edge('Detect', 'GetCoords', label='识别成功')

dot.edge('GetCoords', 'CalcDiff')

# 核心算法块内部连接已定义
dot.edge('MapPTZ', 'MovePTZ')
dot.edge('MovePTZ', 'Wait')
dot.edge('Wait', 'ReCapture')
dot.edge('ReCapture', 'CheckCenter')

# 循环回路
dot.edge('CheckCenter', 'CalcDiff', label='否 (调整)', constraint='false') # constraint=false 防止回路拉长图形

# 成功出口
dot.edge('CheckCenter', 'Zoom', label='是')
dot.edge('Zoom', 'Read')
dot.edge('Read', 'End')

# Render the graph
output_path = '/workspace/docs/visual_servoing_flow'
dot.render(output_path, format='svg', cleanup=True)

print(f"Graph generated at {output_path}.svg")
