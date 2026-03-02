#include <vector>

class BinarySearch {
 public:
  int search(const std::vector<int>& nums, int target) const noexcept {
    if (nums.empty())
      return -1;

    int left = 0, right = nums.size() - 1;
    while (left <= right) {
      const int middle = left + (right - left) / 2;
      const int mid_val = nums[middle];

      if (mid_val == target)
        return middle;
      if (mid_val < target)
        left = middle + 1;
      else
        right = middle - 1;
    }

    return -1;
  }
};
