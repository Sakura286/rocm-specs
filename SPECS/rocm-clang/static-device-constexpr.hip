// SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#include <hip/hip_runtime.h>
#include <stddef.h>
template <size_t N, typename T>
__attribute__((device)) constexpr size_t count(T (&)[N]) { return N; }
template <unsigned... S> __attribute__((device)) unsigned size_probe() {
 static constexpr unsigned values[] = {S...};
 static constexpr unsigned n = count(values);
 return n;
}
__attribute__((global)) void kernel(unsigned* out) { *out = size_probe<1,2,4>(); }
