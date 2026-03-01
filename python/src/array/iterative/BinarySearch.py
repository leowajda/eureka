from bisect import bisect_left
from typing import List


class BinarySearch:
    def search(self, nums: List[int], target: int) -> int:
        idx = bisect_left(nums, target)
        return idx if idx < len(nums) and nums[idx] == target else -1
