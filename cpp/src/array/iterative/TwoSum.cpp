#include <unordered_map>
#include <vector>

class Solution {
 public:
  std::vector<int> twoSum(const std::vector<int>& nums, const int target) const {
    std::unordered_map<int, int> indices;
    indices.reserve(nums.size());

    for (int index = 0; index < static_cast<int>(nums.size()); ++index) {
      const int complement = target - nums[index];
      if (const auto it = indices.find(complement); it != indices.cend())
        return {it->second, index};

      indices.emplace(nums[index], index);
    }

    return {};
  }
};
