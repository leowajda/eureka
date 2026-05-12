#include <vector>

class FindMinimumInRotatedSortedArray {
 public:
  [[nodiscard]] constexpr int findMin(const std::vector<int>& nums) const noexcept {
    int left = 0, right = static_cast<int>(nums.size()) - 1;
    while (left < right) {
      const int mid = left + (right - left) / 2;
      if (nums[mid] > nums[right])
        left = mid + 1;
      else
        right = mid;
    }

    return nums[left];
  }
};
