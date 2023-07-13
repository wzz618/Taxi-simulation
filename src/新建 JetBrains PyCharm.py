from scipy.spatial import cKDTree
from shapely.geometry import Point, LineString

# 示例点集合
points = [
    Point(0, 0),
    Point(1, 1),
    Point(2, 2),
    Point(3, 3)
]

# 示例线集合
lines = [
    LineString([(0, 0), (1, 1)]),
    LineString([(1, 1), (2, 2)]),
    LineString([(2, 2), (3, 3)])
]

# 构建线集合的 KD 树
line_coords = [list(line.coords) for line in lines]
tree = cKDTree(line_coords)

# 针对每个点进行最邻近线的搜索
for point in points:
    # 在 KD 树中找到最邻近线的索引
    _, nearest_line_index = tree.query(point.coords[0])

    # 获取最邻近线对象
    nearest_line = lines[nearest_line_index]

    # 打印最邻近线的信息
    print(f"Point {point.coords[0]} nearest to Line {nearest_line.coords}")
