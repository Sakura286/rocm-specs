%bcond gitcommit 0
%if %{with gitcommit}
%global commit0 2584e35062ad9c2edb68d93c464cf157bc57e3b0
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global date0 20250926
%endif

%global upstreamname MIOpen
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%bcond compat 0
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}
%global pkg_suffix -%{rocm_release}
%global pkg_module rocm%{pkg_suffix}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%global pkg_module default
%endif

%global miopen_name miopen%{pkg_suffix}

%global toolchain rocm

# hipcc does not support some clang flags
# build_cxxflags does not honor CMAKE_BUILD_TYPE, strip out -g
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-g / /' -e 's/-mtls-dialect=gnu2//')

%bcond debug 0
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

# For testing
# hardcoded use of gtest and dirs is not suitable for mock building
# Testsuite is not in great shape, fails instead of skips ck tests
%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

# Change this to the gpu family you are testing on
%bcond check 0
%global gpu_test default
%if %{with test}
%if %{with check}
# Do not build everything to do the test on one thing
%global rocm_gpu_list %{gpu_test}
%endif
%endif

# Needs to match rocblas
%bcond tensile 1

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

%global gpu_list %{rocm_gpu_list_default}
%global _gpu_list gfx1100

# Use ninja if it is available
%bcond ninja 1

%if %{with ninja}
%global cmake_generator -G Ninja
%else
%global cmake_generator %{nil}
%endif

Name:           %{miopen_name}
%if %{with gitcommit}
Version:        git%{date0}.%{shortcommit0}
Release:        1%{?dist}
%else
Version:        %{rocm_version}
Release:        1%{?dist}
%endif
Summary:        AMD's Machine Intelligence Library
License:        MIT AND BSD-2-Clause AND Apache-2.0 AND %{?fedora:LicenseRef-Fedora-Public-Domain}%{?suse_version:SUSE-Public-Domain}
# The base license is MIT with a couple of exceptions
# BSD-2-Clause
#   driver/mloSoftmaxHost.hpp
#   src/include/miopen/mlo_internal.hpp
# Apache-2.0
#   src/include/miopen/kernel_cache.hpp
#   src/kernel_cache.cpp
# Public Domain
#   src/md5.cpp

%if %{with gitcommit}
Url:            https://github.com/ROCm/rocm-libraries
Source0:        %{url}/archive/%{commit0}/rocm-libraries-%{shortcommit0}.tar.gz
%else
Url:            https://github.com/ROCm/%{upstreamname}
Source0:        %{url}/archive/rocm-%{version}.tar.gz#/%{upstreamname}-%{version}.tar.gz
%endif

# So we do not thrash memory
Patch1:         0001-miopen-add-link-and-compile-pools.patch

BuildRequires:  cmake
BuildRequires:  pkgconfig(eigen3)
BuildRequires:  gcc-c++
BuildRequires:  fdupes

BuildRequires:  llvm
BuildRequires:  llvm-devel
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra
BuildRequires:  clang-tools-extra-devel
BuildRequires:  lld
BuildRequires:  lld-devel
BuildRequires:  hipcc
BuildRequires:  compiler-rt
BuildRequires:  rocm-device-libs

BuildRequires:  fplus-devel
BuildRequires:  frugally-deep-devel
BuildRequires:  half-devel
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  hipblas%{pkg_suffix}-devel
BuildRequires:  rocblas%{pkg_suffix}-devel
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-hip%{pkg_suffix}-devel
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}
BuildRequires:  rocrand%{pkg_suffix}-devel
BuildRequires:  roctracer%{pkg_suffix}-devel
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  zlib-devel

BuildRequires:  boost-devel
BuildRequires:  pkgconfig(bzip2)

%if %{with test}
BuildRequires:  gmock-devel
BuildRequires:  gtest-devel
%endif

%if %{with ninja}
BuildRequires:  ninja
%define __builder ninja
%endif

Provides:       miopen%{pkg_suffix} = %{version}-%{release}

# Use ROCm devel at runtime
Requires:       rocm-hip%{pkg_suffix}-devel
Requires:       rocrand%{pkg_suffix}-devel
# Also needs c++ to work
# From pytorch-examples/word_language_model
# MIOpen(HIP): Error [BuildHip] HIPRTC status = HIPRTC_ERROR_COMPILATION (6), source file: MIOpenDropoutHIP.cpp
# MIOpen(HIP): Warning [BuildHip] In file included from /tmp/comgr-78a343/input/MIOpenDropoutHIP.cpp:32:
# In file included from /tmp/comgr-78a343/include/miopen_rocrand.hpp:45:
# In file included from /usr/include/rocrand/rocrand_xorwow.h:24:
# /usr/include/rocrand/rocrand_common.h:39:10: fatal error: 'utility' file not found
#   39 | #include <utility>
#      |          ^~~~~~~~~
Requires:       gcc-c++


ExclusiveArch:  x86_64 riscv64

%description
AMD's library for high performance machine learning primitives.

%package devel
Summary: Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       miopen%{pkg_suffix}-devel = %{version}-%{release}

%description devel
%{summary}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%if %{with gitcommit}
%setup -q -n rocm-libraries-%{commit0}
cd projects/miopen
%patch -P1 -p1
%else
%autosetup -p1 -n %{upstreamname}-rocm-%{version}
%endif

# Readme has executable bit
chmod 644 README.md

# clang-tidy is brittle and not needed for rebuilding from a tarball
sed -i -e 's@clang-tidy@true@' cmake/ClangTidy.cmake

# workaround error on finding lbunzip2
sed -i -e 's@lbunzip2 bunzip2@bunzip2@' CMakeLists.txt

# https://github.com/ROCm/MIOpen/issues/2672
sed -i -e 's@find_path(HALF_INCLUDE_DIR half/half.hpp)@#find_path(HALF_INCLUDE_DIR half/half.hpp)@' CMakeLists.txt
# #include <half/half.hpp> -> <half.hpp>
for f in `find . -type f -name '*.hpp' -o -name '*.cpp' `; do
    sed -i -e 's@#include <half/half.hpp>@#include <half.hpp>@' $f
done
# On 6.4.0
# ../test/verify.hpp:198:56: error: no member named 'expr' in namespace 'half_float::detail'
#  198 |     if constexpr(std::is_same_v<T, half_float::detail::expr>)
# This is not our float, hack it out
sed -i -e 's@std::is_same_v<T, half_float::detail::expr>@0@' test/verify.hpp

# Tries to download its own googletest
# No good knob to turn it off so hack the cmake
%if %{without test}
sed -i -e 's@add_subdirectory(test)@#add_subdirectory(test)@' CMakeLists.txt
sed -i -e 's@add_subdirectory(speedtests)@#add_subdirectory(speedtests)@' CMakeLists.txt
%endif

%if %{without tensile}
sed -i -e 's@#define ROCBLAS_BETA_FEATURES_API 1@#define ROCBLAS_BETA_FEATURES_API 0@' src/include/miopen/handle.hpp
sed -i -e 's@#define ROCBLAS_BETA_FEATURES_API 1@#define ROCBLAS_BETA_FEATURES_API 0@' src/solver/mha/mha_common.hpp
sed -i -e 's@#define ROCBLAS_BETA_FEATURES_API 1@#define ROCBLAS_BETA_FEATURES_API 0@' src/gemm_v2.cpp
%endif

# Our use of modules confuse install locations
# The db is not installed relative to the lib dir.
# Hardcode its location
sed -i -e 's@GetLibPath().parent_path() / "share/miopen/db"@"/usr/share/miopen/db"@' src/db_path.cpp.in

# Unsupported compiler flags
sed -i -e 's@opts.push_back("-fno-offload-uniform-block");@//opts.push_back("-fno-offload-uniform-block");@' src/comgr.cpp

# Paths to clang
sed -i -e 's@llvm/bin/clang@bin/clang@' src/hip/hip_build_utils.cpp

%build
%if %{with gitcommit}
cd projects/miopen
%endif


# Real cores, No hyperthreading
COMPILE_JOBS=`cat /proc/cpuinfo | grep -m 1 'cpu cores' | awk '{ print $4 }'`
if [ ${COMPILE_JOBS}x = x ]; then
    COMPILE_JOBS=1
fi
# Take into account memmory usage per core, do not thrash real memory
BUILD_MEM=4
MEM_KB=0
MEM_KB=`cat /proc/meminfo | grep MemTotal | awk '{ print $2 }'`
MEM_MB=`eval "expr ${MEM_KB} / 1024"`
MEM_GB=`eval "expr ${MEM_MB} / 1024"`
COMPILE_JOBS_MEM=`eval "expr 1 + ${MEM_GB} / ${BUILD_MEM}"`
if [ "$COMPILE_JOBS_MEM" -lt "$COMPILE_JOBS" ]; then
    COMPILE_JOBS=$COMPILE_JOBS_MEM
fi
LINK_MEM=32
LINK_JOBS=`eval "expr 1 + ${MEM_GB} / ${LINK_MEM}"`

#%{?suse_version:%{?build_cxxflags:CXXFLAGS="%{build_cxxflags}"}}

%cmake %{cmake_generator} \
       -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \
       -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \
       -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \
       -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \
       -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \
       -DROCM_SYMLINK_LIBS=OFF \
       -DHIP_PLATFORM=amd \
       -DGPU_TARGETS=%{gpu_list} \
       -DBUILD_TESTING=%{build_test} \
       %{?build_type:-DCMAKE_BUILD_TYPE=%{build_type}} \
       -DCMAKE_SKIP_RPATH=ON \
       -DBoost_USE_STATIC_LIBS=OFF \
       -DMIOPEN_PARALLEL_COMPILE_JOBS=$COMPILE_JOBS \
       -DMIOPEN_PARALLEL_LINK_JOBS=$LINK_JOBS \
       -DMIOPEN_BACKEND=HIP \
       -DMIOPEN_BUILD_DRIVER=OFF \
       -DMIOPEN_ENABLE_AI_IMMED_MODE_FALLBACK=OFF \
       -DMIOPEN_ENABLE_AI_KERNEL_TUNING=OFF \
       -DMIOPEN_TEST_ALL=%{build_test} \
       -DMIOPEN_USE_HIPBLASLT=OFF \
       -DMIOPEN_USE_MLIR=OFF \
       -DMIOPEN_USE_COMPOSABLEKERNEL=OFF

%cmake_build

%if %{with test}
%cmake_build -t tests
%endif

%if %{with test}
%if %{with check}
%check
find . -name 'libMIOpen.so.1'
export LD_LIBRARY_PATH=${PWD}/%{_vpath_builddir}/lib:$LD_LIBRARY_PATH
%ctest
%endif
%endif

%install
%if %{with gitcommit}
cd projects/miopen
%endif
%cmake_install

# Extra license
rm -f %{buildroot}%{pkg_prefix}/share/doc/miopen-hip/LICENSE.md

%fdupes %{buildroot}%{pkg_prefix}

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%if %{with gitcommit}
%doc projects/miopen/README.md
%license projects/miopen/LICENSE.md
%else
%doc README.md
%license LICENSE.md
%endif

%{pkg_prefix}/%{pkg_libdir}/libMIOpen.so.1{,.*}
%{pkg_prefix}/libexec/miopen/

%files devel
%{pkg_prefix}/share/miopen/
%{pkg_prefix}/include/miopen/
%{pkg_prefix}/%{pkg_libdir}/libMIOpen.so
%{pkg_prefix}/%{pkg_libdir}/cmake/miopen/

%if %{with test}
%files test
%{pkg_prefix}/bin/test*
%endif

%changelog
* Mon Feb 2 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
