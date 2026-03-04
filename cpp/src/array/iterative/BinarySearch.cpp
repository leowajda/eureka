#include <algorithm>
#include <vector>

class BinarySearch {
 public:
  constexpr int search(const std::vector<int>& nums, const int target) const noexcept {
    const auto it = std::ranges::lower_bound(nums, target);
    return it != nums.cend() && *it == target ? static_cast<int>(it - nums.cbegin()) : -1;
  }
};
