#!/usr/bin/python3
import json

from collections import defaultdict
from functools import total_ordering
from pprint import pprint


@total_ordering
class Station:
    def __init__(self, lat, lng, name):
        self.lat = lat
        self.lng = lng
        self.name = name

    def  __mul__(self, other):
        return self.lat * other.lng - self.lng * other.lat

    def __lt__(self, other):
        return self * other > 0

    def __eq__(self, other):
        return self.lat / other.lat == self.lng / other.lng

    def __sub__(self, other):
        return Station(self.lat - other.lat, self.lng - other.lng, self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Station({}, {}, {})'.format(repr(self.lat), repr(self.lng), repr(self.name))

    def __hash__(self):
        return hash((self.lat, self.lng, self.name))


def read_data(data_file_name):              # считываем файл
    with open(data_file_name) as data_file:
        data = json.load(data_file)

    lines = defaultdict(set)
    for line in data["lines"]:
        for station in line["stations"]:
            lines[line['name']].add(Station(lat=station['lat'], lng=station['lng'], name=station['name']))

    return lines


def find_all_cross_lines_pairs(lines):          # фукция, которая находит пересекающиеся линии метро

   pairs = list()
   for name_1, line_1 in lines.items():
       for name_2, line_2 in lines.items():
           if name_1 > name_2:
                for station_1 in line_1:
                    for station_2 in line_2:
                        if abs(station_1.lat - station_2.lat) < 0.01 and abs(station_1.lng - station_2.lng) < 0.01 and name_1>name_2:     # хотим узнать, в одной ли окресности две станции метро разных веток (полагаем, что длина перехода меньше отпределенного значения)
                            yield (name_1, line_1, name_2, line_2 )



def get_two_lines_stations(stations_1, stations_2):      # объединяем станции из двух данных веток
    return lines[name_1] | lines[name_2]


def find_mbo(stations):          # алгоритм Грэхэма для нахождения выпуклой оболочки
    left_station = min(stations, key=lambda station: station.lat)

    right_stations = sorted([station - left_station for station in stations if station != left_station])

    left_station = left_station - left_station

    stack = [left_station, right_stations[0]]
    for station in right_stations[1:]:
        while stack[-1] > station:
            stack.remove()
        stack.append(station)

    return stack

def area_triangle(a1, a2):    # площадь треугольника, когда одна из координат (0,0)
    return abs(a1 * a2)


def find_area(mbo):       # находим площадь выпуклой оболочки, как сумму площадей треугольников
    S = 0
    for station in range(1, len(mbo) - 1):
        S += area_triangle(mbo[station], mbo[station + 1])
    return S

if __name__ == '__main__':
    lines = read_data('metro.json')

    '''
    names = list()
    for name_1, line_1, name_2, line_2 in find_all_cross_lines_pairs(lines):
        names.append((name_1, name_2))

    pprint(set(names))
    pprint(len(set(names)))
    '''

    
    #Выше можно посмотреть, какие ветки пересекаются по мнению моей программы. Так как из-за того, что переходы между ветками имеют свою длину, координаты "соседних" станций разных веток различаются.
    #Я взял достаточно большую окресность, чтобы покрыть длины всех переходов. Возможно попадание лишних пар, но их немного.
    #Всего 57 пересечений, что очень близко оценивает сверху количество реальных пересечений. Но если вдуг такое "псевдопересечение" появилось бы в ответе, то мы бы всегда смогли его убрать вручную

    areas = list()
    for name_1, line_1, name_2, line_2 in find_all_cross_lines_pairs(lines):
        two_line_stations = get_two_lines_stations(line_1, line_2)
        mbo = find_mbo(two_line_stations)
        area = find_area(mbo)
        areas.append((area, (name_1, name_2)))

    areas = set(areas)
    pprint(sorted(areas, reverse=True)[:3])


