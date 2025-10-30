import random
import json
from math import sin, cos, pi, log

CANVAS_WIDTH = 840  # 画布的宽
CANVAS_HEIGHT = 680  # 画布的高
CANVAS_CENTER_X = CANVAS_WIDTH / 2  # 画布中心的X轴坐标
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2  # 画布中心的Y轴坐标
IMAGE_ENLARGE = 12  # 放大比例

HEART_COLOR = "#BE0014"  # 引号内修改颜色！颜色代码放在文章末尾


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    """
    "爱心函数生成器"
    :param shrink_ratio: 放大比例
    :param t: 参数
    :return: 坐标
    """
    # 基础函数
    x = 17 * (sin(t) ** 3)
    y = -(16 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(3 * t))

    # 放大
    x *= IMAGE_ENLARGE
    y *= IMAGE_ENLARGE
    # 移到画布中央
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    """
    随机内部扩散
    :param x: 原x
    :param y: 原y
    :param beta: 强度
    :return: 新坐标
    """
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy


def shrink(x, y, ratio):
    """
    抖动
    :param x: 原x
    :param y: 原y
    :param ratio: 比例
    :return: 新坐标
    """
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)  # 这个参数...
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    """
    自定义曲线函数，调整跳动周期
    :param p: 参数
    :return: 正弦
    """
    # 可以尝试换其他的动态函数，达到更有力量的效果（贝塞尔？）
    return 2 * (2 * sin(4 * p)) / (2 * pi)


class Heart:
    """
    爱心类
    """

    def __init__(self, generate_frame=60):  # 增加帧数以便更流畅的动画
        self._points = set()  # 原始爱心坐标集合
        self._edge_diffusion_points = set()  # 边缘扩散效果点坐标集合
        self._center_diffusion_points = set()  # 中心扩散效果点坐标集合
        self.all_points = {}  # 每帧动态点坐标
        self.export_data = []  # 用于导出的数据
        
        self.build(2000)

        self.random_halo = 1000

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # 爱心
        for _ in range(number):
            t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
            x, y = heart_function(t)
            self._points.add((x, y))

        # 爱心内扩散
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # 爱心内再次扩散
        point_list = list(self._points)
        for _ in range(10000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.27)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        # 调整缩放比例
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.420)  # 魔法参数

        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 15 * curve(generate_frame / 10 * pi)  # 圆滑的周期的缩放比例

        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

        all_points = []
        frame_data = []  # 用于导出的数据

        # 光环
        heart_halo_point = set()  # 光环的点坐标集合
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # 随机不到的地方造成爱心有缺口
            x, y = heart_function(t, shrink_ratio=-15)  # 魔法参数
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # 处理新的点
                heart_halo_point.add((x, y))
                x += random.randint(-60, 60)
                y += random.randint(-60, 60)
                size = random.choice((1, 1, 2))
                all_points.append((x, y, size))
                frame_data.append([x, y, size])
                
                # 添加周围点
                offsets = [(20, 20), (-20, -20), (20, -20), (-20, 20)]
                for dx, dy in offsets:
                    all_points.append((x + dx, y + dy, size))
                    frame_data.append([x + dx, y + dy, size])

        # 轮廓
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))
            frame_data.append([x, y, size])

        # 内容
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
            frame_data.append([x, y, size])

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))
            frame_data.append([x, y, size])

        self.all_points[generate_frame] = all_points
        self.export_data.append(frame_data)  # 保存帧数据

    def export_to_json(self, filename="heart_data.json"):
        """导出动画数据到JSON文件"""
        export_dict = {
            "frames": self.export_data,
            "width": CANVAS_WIDTH,
            "height": CANVAS_HEIGHT,
            "color": HEART_COLOR
        }
        
        with open(filename, 'w') as f:
            json.dump(export_dict, f)
        print(f"数据已导出到 {filename}")


if __name__ == '__main__':
    # 生成数据但不显示窗口
    heart = Heart(60)  # 生成60帧
    
    # 导出数据
    heart.export_to_json("heart_data.json")
    print("动画数据生成完成！")