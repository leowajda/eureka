class TwoSum:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        index_by_value: dict[int, int] = {}

        for index, value in enumerate(nums):
            complement = target - value
            match_index = index_by_value.get(complement)
            if match_index is not None:
                return [match_index, index]

            index_by_value[value] = index

        return [-1, -1]
