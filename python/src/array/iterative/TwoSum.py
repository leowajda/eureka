from typing import List


class TwoSum:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        indices: dict[int, int] = {}

        for index, value in enumerate(nums):
            complement = target - value
            if complement in indices:
                return [indices[complement], index]

            indices[value] = index

        return []
