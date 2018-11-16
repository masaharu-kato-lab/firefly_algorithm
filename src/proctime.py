import time

def proctime(function : callable):
    begin = time.time()
    function()
    finish = time.time()
    return finish - begin