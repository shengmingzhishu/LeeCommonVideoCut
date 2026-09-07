# -*- coding: utf-8 -*-
import threading
import functools

def singleton(cls):
    instances = {}
    instance_lock = threading.Lock()

    @functools.wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            with instance_lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper

