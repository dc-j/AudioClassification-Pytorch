import graphviz

dot = graphviz.Digraph('visual_servoing', comment='Visual Servoing Flow')
dot.attr(rankdir='TB', size='10,10', fontname='SimSun')

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
dot.node('GetCoords', '提取表盘检测框中心坐标 P_target')

# Core Logic Subgraph
with dot.subgraph(name='cluster_core') as c:
    c.attr(style='dashed', label='核心纠偏算法', fontname='SimSun', bgcolor='#f5f5f5')
    c.node('CalcDiff', '计算中心偏差量\nΔx, Δy')
    c.node('Normalize', '坐标归一化处理\nNx = 2*Δx/W\nNy = 2*Δy/H')
    c.node('MapPTZ', '映射云台XYZ/角度控制量\nPan = Nx * Kp\nTilt = Ny * Kp')
    c.edge('CalcDiff', 'Normalize')
    c.edge('Normalize', 'MapPTZ')

dot.attr('node', shape='box', style='filled', fillcolor='#ffffff', fontname='SimSun')
dot.node('MovePTZ', '调用云台驱动执行运动')
dot.node('Wait', '等待云台稳定')
dot.node('ReCapture', '再次采集图像验证')

dot.attr('node', shape='diamond', style='filled', fillcolor='#fff9c4', fontname='SimSun')
dot.node('CheckCenter', '判断是否位于画面中心?\n偏差 < 阈值')

dot.attr('node', shape='box', style='filled', fillcolor='#c8e6c9', fontname='SimSun')
dot.node('Zoom', '变焦拉近 & 自动对焦')
dot.node('Read', '高清拍照 & 算法读数')

dot.attr('node', shape='ellipse', style='filled', fillcolor='#e1f5fe', fontname='SimSun')
dot.node('End', '结束: 上传数据')

# Define edges
dot.edge('Start', 'Capture')
dot.edge('Capture', 'Detect')
dot.edge('Detect', 'Search', label='未识别')
dot.edge('Search', 'Capture')
dot.edge('Detect', 'GetCoords', label='识别成功')
dot.edge('GetCoords', 'CalcDiff')
dot.edge('MapPTZ', 'MovePTZ')
dot.edge('MovePTZ', 'Wait')
dot.edge('Wait', 'ReCapture')
dot.edge('ReCapture', 'CheckCenter')
dot.edge('CheckCenter', 'CalcDiff', label='否/仍有偏差')
dot.edge('CheckCenter', 'Zoom', label='是/已居中')
dot.edge('Zoom', 'Read')
dot.edge('Read', 'End')

# Render the graph
output_path = '/workspace/docs/visual_servoing_flow'
dot.render(output_path, format='png', cleanup=True)

print(f"Graph generated at {output_path}.png")
