from .api import *
from .coordinates import Point
from pprint import pprint
import json

api = API()

# area = Area(Point(43.3739, 1.1688), Point(43.8476, 1.7217))
# data_raw = api.get_area(area)
# data = json.loads(data_raw)

# for k, v in data.items():
#     # print(v)
#     print(api.get_flight(k))

f = api.get_flight('2973b74b')
print(f)