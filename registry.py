# MeshWeaver

class TaskRegistry:
    """Registry for tasks in MeshWeaver."""

    def __init__(self):
        self.tasks = {}

    def register(self, name, func):
        if not callable(func):
            raise ValueError("Task must be callable")
        
        self.tasks[name] = func

    def unregister(self, name):
        self.tasks.pop(name, None)

    def exists(self, name):
        return name in self.tasks

    def execute(self, name, args=None, kwargs=None):
        if name not in self.tasks:
            raise ValueError(
                f"Unknown task: {name}"
            )
        
        func = self.tasks[name]
        args = args or []
        kwargs = kwargs or {}
        
        return func(*args, **kwargs)
    
    def list_tasks(self):
        return list(self.tasks.keys())

# Example predefined tasks

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def square(number):
    return number * number

def greet(name):
    return f"Hello, {name}!"

def create_default_registry():
    """Create a default task registry with predefined tasks."""
    registry = TaskRegistry()
    registry.register("add", add)
    registry.register("multiply", multiply)
    registry.register("square", square)
    registry.register("greet", greet)
    return registry