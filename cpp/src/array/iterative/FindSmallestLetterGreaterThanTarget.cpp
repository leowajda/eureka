#include <algorithm>
#include <vector>

class Solution {
 public:
  constexpr char nextGreatestLetter(const std::vector<char>& letters, const char target) const noexcept {
    const auto it = std::ranges::upper_bound(letters, target);
    return it != letters.cend() ? *it : letters.front();
  }
};
