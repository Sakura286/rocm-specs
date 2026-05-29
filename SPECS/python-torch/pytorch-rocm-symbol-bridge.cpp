// === openRuyi ROCm symbol bridge for pytorch 2.11 / clang 21 ===
//
// Appended to aten/src/ATen/core/Tensor.cpp by python-torch.spec.
//
// Background:
//   libtorch_hip.so references the TensorBase data-pointer template family
//   (const_data_ptr / mutable_data_ptr / data_ptr) using a NON-SFINAE
//   mangling form (...Li0EEE... — only the non-type template parameter
//   value is encoded). But the explicit specialisations emitted from
//   TensorMethods.cpp into libtorch_cpu.so are mangled WITH the SFINAE
//   template-template-parameter encoded (...Tn NSt9enable_if... Li0EEE...).
//   Same C++ source, two clang mangling conventions, no link-time error
//   thanks to lld's --allow-shlib-undefined → runtime dlopen reports
//   "undefined symbol: _ZNK2at10TensorBase14const_data_ptrI*Li0EEEPK*v"
//   when libtorch_hip.so is loaded.
//
// Reference: https://github.com/pytorch/pytorch/issues/173707
//   (closed as not planned; pytorch treats this as a clang/ROCm gap)
//
// Bridge strategy:
//   Provide the missing Li0E-only manglings as free functions linked into
//   libtorch_cpu.so, with default visibility so the dynamic linker can
//   resolve libtorch_hip.so against them. Each bridge body delegates to
//   the non-templated public accessor on TensorBase, which returns the
//   raw underlying data pointer.
//
// Semantics note:
//   The non-templated TensorBase::const_data_ptr() / mutable_data_ptr() /
//   data_ptr() skip the scalar-type runtime check that the templated
//   specialisations perform. In practice this only matters for HIP code
//   paths that already dispatched on dtype before reaching this call —
//   which is the common case in ATen kernels.
//
// gemm stubs from the upstream issue are intentionally NOT included:
//   `nm -DC --undefined-only libtorch_hip.so` on this build shows no
//   undefined at::cuda::blas::gemm symbols, and the upstream stubs have
//   empty bodies (silent functional failure if ever called).

#include <ATen/core/TensorBase.h>
#include <c10/util/BFloat16.h>
#include <c10/util/Float8_e4m3fn.h>
#include <c10/util/Float8_e4m3fnuz.h>
#include <c10/util/Float8_e5m2.h>
#include <c10/util/Float8_e5m2fnuz.h>
#include <c10/util/Float8_e8m0fnu.h>
#include <c10/util/Half.h>
#include <c10/util/complex.h>
#include <c10/util/qint8.h>
#include <c10/util/qint32.h>
#include <c10/util/quint8.h>

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmissing-prototypes"
#pragma GCC visibility push(default)

extern "C" {

#define BRIDGE_READ(MangledName) \
  __attribute__((visibility("default"))) \
  const void* MangledName(const at::TensorBase* t) { return t->const_data_ptr(); }

#define BRIDGE_WRITE(MangledName) \
  __attribute__((visibility("default"))) \
  void* MangledName(const at::TensorBase* t) { return t->mutable_data_ptr(); }

// ---- const_data_ptr<T, 0>  (non-const T, plain Li0E form) ----
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIaLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIbLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIdLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIfLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIhLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIiLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIjLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIlLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrImLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIsLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrItLi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c104HalfELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c108BFloat16ELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c107complexIdEELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c107complexINS2_4HalfEEELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c1011Float8_e5m2ELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c1013Float8_e4m3fnELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c1014Float8_e8m0fnuELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c1015Float8_e4m3fnuzELi0EEEPKT_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c1015Float8_e5m2fnuzELi0EEEPKT_v)

// ---- const_data_ptr<KT, 0>  (const-qualified T, plain Li0E form) ----
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKaLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKbLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKdLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKfLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKhLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKiLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKjLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKlLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKmLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKsLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKtLi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c104HalfELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c108BFloat16ELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c107complexIdEELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c107complexIfEELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c107complexINS2_4HalfEEELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c105qint8ELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c106qint32ELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c106quint8ELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c1011Float8_e5m2ELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c1013Float8_e4m3fnELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c1014Float8_e8m0fnuELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c1015Float8_e4m3fnuzELi0EEEPKNSt12remove_constIT_E4typeEv)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIKN3c1015Float8_e5m2fnuzELi0EEEPKNSt12remove_constIT_E4typeEv)

// ---- const_data_ptr<T, Tn enable_if<!is_const_v<T>>... 0>  (SFINAE form, non-const T) ----
// libtorch_hip.so emits these for a few primitives even when most TUs use the Li0E form.
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIdTnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS3_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIfTnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS3_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIiTnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS3_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIlTnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS3_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c104HalfETnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS5_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c108BFloat16ETnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS5_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c107complexIdEETnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS6_v)
BRIDGE_READ(_ZNK2at10TensorBase14const_data_ptrIN3c107complexIfEETnNSt9enable_ifIXntsr3stdE10is_const_vIT_EEiE4typeELi0EEEPKS6_v)

// ---- mutable_data_ptr<T> ----
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIaEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIbEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIdEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIfEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIhEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIiEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIjEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIlEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrImEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIsEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrItEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c104HalfEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c108BFloat16EEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c107complexIdEEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c107complexIfEEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c107complexINS2_4HalfEEEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c1011Float8_e5m2EEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c1013Float8_e4m3fnEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c1014Float8_e8m0fnuEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c1015Float8_e4m3fnuzEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c1015Float8_e5m2fnuzEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c105qint8EEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c106qint32EEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase16mutable_data_ptrIN3c106quint8EEEPT_v)

// ---- data_ptr<T>  (legacy mutable accessor) ----
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIaEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIbEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIdEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIfEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIhEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIiEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIlEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIsEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIN3c104HalfEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIN3c108BFloat16EEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIN3c107complexIdEEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIN3c107complexIfEEEEPT_v)
BRIDGE_WRITE(_ZNK2at10TensorBase8data_ptrIN3c107complexINS2_4HalfEEEEEPT_v)

#undef BRIDGE_READ
#undef BRIDGE_WRITE

} // extern "C"

#pragma GCC visibility pop
#pragma GCC diagnostic pop
// === openRuyi ROCm symbol bridge end ===
