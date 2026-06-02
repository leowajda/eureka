#include <algorithm>
#include <vector>

class RemoveDuplicatesFromSortedArray {
 public:
  [[nodiscard]] constexpr int removeDuplicates(std::vector<int>& nums) const noexcept {
    if (nums.empty()) [[unlikely]]
      return 0;
    auto result = std::ranges::unique(nums);
    return static_cast<int>(result.begin() - nums.begin());
  }
};
