#include <Rcpp.h>
// std::unique_ptr is not used here; "std::find" in a string is not a use either
const char* msg = "std::find";

// [[Rcpp::export]]
Rcpp::NumericVector sorted(Rcpp::NumericVector x) {
  Rcpp::NumericVector y = Rcpp::clone(x);
  std::sort(y.begin(), y.end());
  return y;
}
