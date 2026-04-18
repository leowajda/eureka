#include <unordered_map>
#include <vector>

class TwoSum {
 public:
  std::vector<int> twoSum(const std::vector<int>& nums, const int target) const {
    std::unordered_map<int, int> index_by_value;
    index_by_value.reserve(nums.size());
    const auto size = static_cast<int>(nums.size());

    for (int index = 0; index < size; ++index) {
      const int value = nums[index];
      const int complement = target - value;
      const auto match = index_by_value.find(complement);

      if (match != index_by_value.end())
        return {match->second, index};

      index_by_value[value] = index;
    }

    return {-1, -1};
  }
};
