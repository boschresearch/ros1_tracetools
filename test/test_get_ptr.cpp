// just a compile timestamp

#include <tracetools/tracetools.h>

namespace {
  class foo {

  };
  void test_fn(const foo&) {
    // does nothing
  }
}

int main(int, char**)
{
  const boost::function<void (const foo&)> f(&test_fn);
  const void* d = ros::trace::get_ptr(f);

  return d == 0;
}
