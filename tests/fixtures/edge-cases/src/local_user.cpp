#include "local_hdr.h"
#include <vector>
#include <stdlib.h>

/* std::accumulate in a block comment is ignored */
long span(const std::vector<int>& v) {
  int* scratch = (int*) malloc(sizeof(int));
  free(scratch);
  return std::distance(v.begin(), std::max_element(v.begin(), v.end())) + (long) std::sqrt(4.0);
}
