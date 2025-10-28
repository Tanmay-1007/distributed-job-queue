"""
Task Registry - Where we define all available tasks
Workers will look up tasks here to execute them
"""

class TaskRegistry:
    def __init__(self):
        self.tasks = {}
    
    def register(self, task_name):
        """Decorator to register a task"""
        def decorator(func):
            self.tasks[task_name] = func
            print(f"📝 Registered task: {task_name}")
            return func
        return decorator
    
    def get_task(self, task_name):
        """Get a task function by name"""
        return self.tasks.get(task_name)
    
    def list_tasks(self):
        """List all registered tasks"""
        return list(self.tasks.keys())

# Global task registry instance
task_registry = TaskRegistry()