#include <vector>

double sorted_total(std::vector<double> x) {
  std::sort(x.begin(), x.end());
  std::vector<double> out;
  std::copy(x.begin(), x.end(), std::back_inserter(out));
  return std::accumulate(out.begin(), out.end(), 0.0);
}
