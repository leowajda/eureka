#include <algorithm>
#include <vector>

class Solution {
 public:
  constexpr char nextGreatestLetter(const std::vector<char>& letters, const char target) const noexcept {
    const auto it = std::upper_bound(letters.cbegin(), letters.cend(), target);
    return it != letters.cend() ? *it : letters.front();
  }
};
