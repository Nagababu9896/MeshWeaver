# MeshWeaver

from serializer import TaskSerializer

def complex_calculation(x, y, multiplier=2):

    result = (x ** 2 + y ** 2)

    return result * multiplier

def main():

    print("=" * 50)
    print("MeshWeaver Task searialization Test")
    print("=" * 50)

    serialized = TaskSerializer.serialize(
        complex_calculation,
        10,
        20,
        multiplier=3
    )

    print("Task serialized successfully")

    result = TaskSerializer.execute(
        serialized
    )

    print(
        f"Execution result: {result}"
    )

    excepted = (
        (10 ** 2 + 20 ** 2) * 3
    )

    assert result == excepted

    print("serialization test: PASS")

if __name__ == "__main__":
    main()