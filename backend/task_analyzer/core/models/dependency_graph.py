"""
DependencyGraph
---------------

Responsible for detecting circular dependencies using DFS.

Input:
- tasks: Dict[id -> TaskEntity]

Output:
- has_cycle(): bool
- get_cycles(): list of lists of task IDs

"""

class DependencyGraph:

    def __init__(self, tasks_dict):
        self.tasks = tasks_dict
        self.visited = set()
        self.rec_stack = set()
        self.cycles = []

    def _dfs(self, task_id, path):
        if task_id in self.rec_stack:
            # cycle found
            cycle_start = path.index(task_id)
            self.cycles.append(path[cycle_start:])
            return True

        if task_id in self.visited:
            return False

        self.visited.add(task_id)
        self.rec_stack.add(task_id)

        task = self.tasks.get(task_id)
        if not task:
            return False

        for dep in task.dependencies:
            if self._dfs(dep, path + [dep]):
                return True

        self.rec_stack.remove(task_id)
        return False

    def has_cycle(self):
        for task_id in self.tasks:
            if self._dfs(task_id, [task_id]):
                return True
        return False

    def get_cycles(self):
        return self.cycles
