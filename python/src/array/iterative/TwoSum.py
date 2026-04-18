class TwoSum:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        first_index_by_value: dict[int, int] = {}

        for index, value in enumerate(nums):
            if (match_index := first_index_by_value.get(target - value)) is not None:
                return [match_index, index]

            first_index_by_value.setdefault(value, index)

        return [-1, -1]
