import threading
from queue import Queue

class ParallelExecutor:
    def __init__(self):
        self.tasks = Queue()

    def add_task(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))

    def run(self, workers=4):
        def worker():
            while True:
                try:
                    func, args, kwargs = self.tasks.get(timeout=3)
                    func(*args, **kwargs)
                    self.tasks.task_done()
                except:
                    break
        threads = [threading.Thread(target=worker) for _ in range(workers)]
        for t in threads: t.start()
        for t in threads: t.join()

