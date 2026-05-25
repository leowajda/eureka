#include <algorithm>
#include <numeric>
#include <vector>

class FindMinimumTimeToFinishAllJobs {
 public:
  constexpr int minimumTimeRequired(std::vector<int>& jobs, const int k) const noexcept {
    int low = jobs.front();
    int high = std::reduce(jobs.begin(), jobs.end(), 0);
    std::vector<int> workers(k, 0);
    int minTime = high;

    std::ranges::sort(jobs, std::greater{});

    while (low <= high) {
      const int guess = low + (high - low) / 2;
      workers.assign(k, 0);

      if (isFeasible(jobs, workers, 0, guess)) {
        minTime = guess;
        high = guess - 1;
      } else
        low = guess + 1;
    }

    return minTime;
  }

  constexpr bool isFeasible(const std::vector<int>& jobs, std::vector<int>& workers, const int idx,
                            const int guess) const noexcept {
    if (idx == jobs.size())
      return true;

    for (size_t i = 0; i < workers.size(); i++) {
      if (workers[i] + jobs[idx] > guess)
        continue;

      workers[i] += jobs[idx];
      if (isFeasible(jobs, workers, idx + 1, guess))
        return true;
      workers[i] -= jobs[idx];

      if (workers[i] == 0)
        break;
    }

    return false;
  }
};
