class WorkerAssigner:
    def __init__(self, workers, tasks):
        self.workers = workers
        self.tasks = tasks
        self.assignments = {}

    def assign_tasks(self):
        for worker in self.workers:
            best_task = None
            best_score = float('inf')
            for task in self.tasks:
                score = self.evaluate_task(worker, task)
                if score < best_score:
                    best_score = score
                    best_task = task
            if best_task is not None:
                self.assignments[worker] = best_task
                self.tasks.remove(best_task)

    def evaluate_task(self, worker, task):
        # Placeholder for actual evaluation logic
        return abs(worker - task)  # Example: absolute difference

    def get_assignments(self):
        return self.assignments