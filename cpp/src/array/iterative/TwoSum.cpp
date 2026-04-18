#include <unordered_map>
#include <vector>

class TwoSum {
 public:
  std::vector<int> twoSum(const std::vector<int>& nums, const int target) const {
    std::unordered_map<int, int> first_index_by_value;
    first_index_by_value.reserve(nums.size());

    for (int index = 0; index < static_cast<int>(nums.size()); ++index) {
      const int value = nums[index];
      if (const auto it = first_index_by_value.find(target - value);
          it != first_index_by_value.cend())
        return {it->second, index};

      first_index_by_value.try_emplace(value, index);
    }

    return {-1, -1};
  }
};
