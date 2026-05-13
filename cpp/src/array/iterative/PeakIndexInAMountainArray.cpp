#include <vector>

class Solution {
 public:
  constexpr int peakIndexInMountainArray(std::vector<int>& arr) const noexcept {
    const int n = static_cast<int>(arr.size() - 1);
    int left = 0, right = n - 1;

    while (left < right) {
      const int mid = left + (right - left) / 2;

      if (arr[mid] > arr[mid + 1])
        right = mid;
      else
        left = mid + 1;
    }

    return right;
  }
};
