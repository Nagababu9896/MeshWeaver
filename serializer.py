# MeshWeaver


import cloudpickle
import hashlib


class TaskSerializer:
    """
    Serializes and deserializes Python tasks
    for transmission between MeshWeaver nodes.
    """

    @staticmethod
    def serialize(function, *args, **kwargs):
        """
        Serialize a function and its arguments.
        """

        payload = {
            "function": function,
            "args": args,
            "kwargs": kwargs,
        }

        data = cloudpickle.dumps(payload)

        checksum = hashlib.sha256(
            data
        ).hexdigest()

        return {
            "data": data,
            "checksum": checksum,
        }

    @staticmethod
    def deserialize(serialized_data):
        """
        Deserialize a serialized task.
        """

        if not isinstance(serialized_data, dict):
            raise ValueError(
                "Invalid serialized task"
            )

        data = serialized_data.get("data")
        checksum = serialized_data.get("checksum")

        if not data or not checksum:
            raise ValueError(
                "Missing task data or checksum"
            )

        calculated_checksum = hashlib.sha256(
            data
        ).hexdigest()

        if calculated_checksum != checksum:
            raise ValueError(
                "Task checksum verification failed"
            )

        return cloudpickle.loads(data)

    @staticmethod
    def execute(serialized_data):
        """
        Deserialize and execute a task.
        """

        payload = TaskSerializer.deserialize(
            serialized_data
        )

        function = payload["function"]
        args = payload["args"]
        kwargs = payload["kwargs"]

        return function(
            *args,
            **kwargs
        )
