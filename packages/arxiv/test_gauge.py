from prometheus_client import Gauge
try:
    g = Gauge('my_gauge', 'my description')
    g.set_function(lambda: 5)
    print("set_function works")
except AttributeError as e:
    print(f"AttributeError: {e}")
