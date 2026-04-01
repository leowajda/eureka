#include <algorithm>
#include <ranges>

class Sqrtx {
 public:
  constexpr int mySqrt(const int x) const noexcept {
    const auto range = std::views::iota(0LL, static_cast<long long>(x) + 1);
    const auto it = std::ranges::partition_point(range, [x](long long val) { return val * val <= x; });
    return static_cast<int>(*it - 1);
  }
};
