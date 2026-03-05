#include <algorithm>
#include <vector>

class Solution {
 public:
  constexpr std::vector<int> searchRange(const std::vector<int>& nums, const int target) const noexcept {
    const auto [first, last] = std::ranges::equal_range(nums, target);
    const auto offset = nums.cbegin();
    if (first == last)
      return {-1, -1};
    return {static_cast<int>(first - offset), static_cast<int>(std::prev(last) - offset)};
  }
};
