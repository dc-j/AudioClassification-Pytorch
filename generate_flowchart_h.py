import graphviz

# 核心修改：将布局方向改为 LR (Left-to-Right)
dot = graphviz.Digraph('visual_servoing', comment='Visual Servoing Flow')
dot.attr(rankdir='LR', size='15,8', fontname='SimSun')

# 节点定义
dot.attr('node', shape='ellipse', style='filled', fillcolor='#e1f5fe', fontname='SimSun')
dot.node('Start', '开始\n(到达点位)')
dot.node('End', '结束\n(上传数据)')

dot.attr('node', shape='box', style='filled', fillcolor='#ffffff', fontname='SimSun')
dot.node('Capture', '采集图像')
dot.node('Search', '局部搜索')
dot.node('MovePTZ', '执行\n云台运动')
dot.node('Wait', '等待\n稳定')
dot.node('ReCapture', '再次\n采集')

dot.attr('node', shape='diamond', style='filled', fillcolor='#fff9c4', fontname='SimSun')
dot.node('Detect', '识别\n成功?')
dot.node('CheckCenter', '居中?')

dot.attr('node', shape='box', style='filled', fillcolor='#c8e6c9', fontname='SimSun')
dot.node('GetCoords', '提取坐标')
dot.node('CalcDiff', '计算偏差')
dot.node('Normalize', '归一化')
dot.node('MapPTZ', '映射指令')
dot.node('Zoom', '变焦\n聚焦')
dot.node('Read', '拍照\n读数')

# 核心算法子图（为了让这些紧凑在一起）
with dot.subgraph(name='cluster_algo') as c:
    c.attr(label='纠偏算法', style='dashed', bgcolor='#f5f5f5')
    c.edge('CalcDiff', 'Normalize')
    c.edge('Normalize', 'MapPTZ')

# 连接关系
dot.edge('Start', 'Capture')
dot.edge('Capture', 'Detect')

# 识别分支
dot.edge('Detect', 'Search', label='否')
dot.edge('Search', 'Capture')
dot.edge('Detect', 'GetCoords', label='是')

# 主流程
dot.edge('GetCoords', 'CalcDiff')
dot.edge('MapPTZ', 'MovePTZ')
dot.edge('MovePTZ', 'Wait')
dot.edge('Wait', 'ReCapture')
dot.edge('ReCapture', 'CheckCenter')

# 回环（调整）
# 使用 constraint=false 避免回环线影响整体从左到右的布局
dot.edge('CheckCenter', 'CalcDiff', label='否', constraint='false', style='dashed')

# 成功出口
dot.edge('CheckCenter', 'Zoom', label='是')
dot.edge('Zoom', 'Read')
dot.edge('Read', 'End')

# 渲染
output_path = '/workspace/docs/visual_servoing_flow_horizontal'
dot.render(output_path, format='svg', cleanup=True)
print(f"Graph generated at {output_path}.svg")