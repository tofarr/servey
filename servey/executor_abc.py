from abc import abstractmethod, ABC


class ExecutorABC(ABC):

    @abstractmethod
    def execute(self, **kwargs):
        """
        Execute this action and return the result. Local actions may not strictly enforce
        timeouts, but instead issue a warning to the logs. Environments like lambda
        are not so forgiving, and may leave data in an invalid state!
        """

    @abstractmethod
    def execute_async(self, **kwargs):
        """
        Execute this action asynchronously and return flow before it finishes
        """
