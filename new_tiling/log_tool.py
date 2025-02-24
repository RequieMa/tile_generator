import time
from functools import wraps
import inspect
import pandas as pd

def decorate_all_functions(module):
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            setattr(module, name, time_logger(obj))

def print_summary(module):
    summary = {
        "Name": [],
        "Average Time": [],
        "Total Time": [],
        "Call Count": [],
    }
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            try:
                summary["Call Count"].append(obj.call_count)
                summary["Name"].append(name)
                summary["Average Time"].append(obj.average_time())
                summary["Total Time"].append(obj.total_time)
            except:
                pass
    summary = pd.DataFrame.from_dict(summary)
    summary.sort_values(by='Call Count', ascending=False, inplace=True)
    print(summary)

def time_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(wrapper, 'call_count'):
            wrapper.call_count = 0
            wrapper.total_time = 0
        
        start_time = time.perf_counter_ns()
        result = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        
        wrapper.call_count += 1
        wrapper.total_time += (end_time - start_time)
        
        print(f"{func.__name__} call {wrapper.call_count} took {end_time - start_time} ns")
        return result
    
    def average_time():
        try:
            return wrapper.total_time / wrapper.call_count
        except:
            return -1
    
    wrapper.average_time = average_time
    return wrapper