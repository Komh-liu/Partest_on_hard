// single_thread_impl.h
#include "array_sum.h"
#include <numeric> // 对于 std::accumulate

int array_sum(const std::vector<int>& arr) {
    return std::accumulate(arr.begin(), arr.end(), 0);
}