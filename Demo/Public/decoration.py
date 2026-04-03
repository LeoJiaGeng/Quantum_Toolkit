import time
from functools import cache


class Decorator(object):
    def __init__(self):
        pass

    @staticmethod
    def exe_time(content):
        """print the elapsed time of specified function"""
        def recorder(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                ret = func(*args, **kwargs)
                print("%s函数耗时: %s\n" % (content, (time.time() - start)))
                return ret
            return wrapper
        return recorder

    @staticmethod
    def raise_err():
        """Raise an error for specified function"""
        def recorder(func):
            def wrapper(*args, **kwargs):
                ret = {"data": []}
                try:
                    ret = func(*args, **kwargs)
                except Exception as e:
                    ret["ret_val"] = False
                    ret["info"] = str(e)
                return ret
            return wrapper
        return recorder

    @staticmethod
    def exe_execute(func):
        def wrapper(*args, **kwargs):
            print("文件开始写入")
            ret = func(*args, **kwargs)
            print("文件写入完成\n")
            return ret
        return wrapper

    @staticmethod
    def write_log(name):
        def exe_execute(func):
            def wrapper(*args, **kwargs):
                print(name)
                print("文件开始写入")
                ret = func(*args, **kwargs)
                print("文件写入完成")
                return ret
            return wrapper
        return exe_execute

    @staticmethod
    def retry(times=3, timeout=0.1):
        """ attempting many times with time gap after fail operation """
        def recorder(func):
            def wrapper(*args, **kwargs):
                for i in range(times):
                    try:
                        ret = func(*args, **kwargs)
                        break
                    except Exception as e:
                        print(f"after {i+1} time try, there is a err: {e}")
                        time.sleep(timeout)
                return ret
            return wrapper
        return recorder


@Decorator.retry()
def test_fun(x):
    time.sleep(x)
    time.abc(1)
    print("cehsiyici")


@cache
def test_function(a):
    if not a:
        time.sleep(2)
    else:
        time.sleep(3)
    return a


def progress_bar():
    """progress bar"""
    for i in range(11):
        progress = "#" * i + "-" * (10 - i)
        print(f"\r\033[1;32m{progress}", end="")
        time.sleep(0.5)


if __name__ == "__main__":
    # print(test_function(0.1))
    # print(test_function(0.1))
    # print(test_function(0.1))
    # print(test_function(0.2))
    # print(test_function.cache_info())
    # print(test_function.cache_clear())
    progress_bar()
