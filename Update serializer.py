# MeshWeaver

import hashlib
import cloudpickle

class TaskSerializer:

    @staticmethod
    def serialize(function, *args, **kwargs):
        payload = {
            "function": function,
            "args": args,
            "kwargs": kwargs,
        }

        data = cloudpickle.dumps(payload)

        checksum = hashlib.sha256(data).hexdigest()

        return {
            "data": data,
            "checksum": checksum,
        }

    @staticmethod
    def deserialize(payload):
        if not isinstance(payload, dict):
            raise ValueError("Invalid task payload")

        data = payload.get("data")
        checksum = payload.get("checksum")

        if data is None or checksum is None:
            raise ValueError(
                "Missing serialized data or checksum"
            )

        calculated = hashlib.sha256(data).hexdigest()

        if not hashlib.compare_digest(
            calculated,
            checksum
        ):
            raise ValueError(
                "Task checksum verification failed"
            )

        return cloudpickle.loads(data)

    @staticmethod
    def execute(payload):

        task = TaskSerializer.deserialize(
            payload
        )

        function = task["function"]
        args = task["args"]
        kwargs = task["kwargs"]

        return function(*args, **kwargs)