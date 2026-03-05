%if 0%{?suse_version}
%global rocblas_name librocblas5
%else
%global rocblas_name rocblas
%endif

%bcond_with gitcommit
%if %{with gitcommit}
%global commit0 de5c1aebb641af098d9310a9fcca5591a7c066c8
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global date0 20251015
%endif

%global upstreamname rocblas
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

%bcond_with debug
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

%bcond_without compress
%if %{with compress}
%global build_compress ON
%else
%global build_compress OFF
%endif

%if 0%{?fedora}
%bcond_without test
%else
%bcond_with test
%endif
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

# Option to test suite for testing on real HW:
# May have to set gpu under test with
# export HIP_VISIBLE_DEVICES=<num> - 0, 1 etc.
%bcond_with check

# Tensile in 6.4 does not support generics
# https://github.com/ROCm/Tensile/issues/2124
%bcond_without tensile
%if %{with tensile}
%global build_tensile ON
%else
%global build_tensile OFF
%endif

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

# SUSE/OSB times out because -O is added to the make args
# This accumulates all the output from the long running tensile
# jobs.
%global _make_output_sync %{nil}

# OracleLinux 9 has a problem with it's strip not recognizing *.co's
%global __strip %rocmllvm_bindir/llvm-strip

# Use ninja if it is available
# Ninja is available on suse but obs times out with ninja build, make doesn't
%if 0%{?fedora}
%bcond_without ninja
%else
%bcond_with ninja
%endif

%if %{with ninja}
%global cmake_generator -G Ninja
%else
%global cmake_generator %{nil}
%endif

%global cmake_config \\\
  -DBLAS_INCLUDE_DIR=%{_includedir}/%{blaslib} \\\
  -DBLAS_LIBRARY=%{blaslib} \\\
  -DCMAKE_CXX_COMPILER=hipcc \\\
  -DCMAKE_C_COMPILER=clang \\\
  -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld \\\
  -DCMAKE_AR=%rocmllvm_bindir/llvm-ar \\\
  -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib \\\
  -DCMAKE_BUILD_TYPE=%{build_type} \\\
  -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/.. \\\
  -DCMAKE_SKIP_RPATH=ON \\\
  -DCMAKE_VERBOSE_MAKEFILE=ON \\\
  -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF \\\
  -DROCM_SYMLINK_LIBS=OFF \\\
  -DHIP_PLATFORM=amd \\\
  -DBUILD_CLIENTS_BENCHMARKS=%{build_test} \\\
  -DBUILD_CLIENTS_TESTS=%{build_test} \\\
  -DBUILD_CLIENTS_TESTS_OPENMP=OFF \\\
  -DBUILD_FORTRAN_CLIENTS=OFF \\\
  -DBUILD_OFFLOAD_COMPRESS=%{build_compress} \\\
  -DBUILD_WITH_HIPBLASLT=OFF \\\
  -DTensile_CPU_THREADS=${CORES} \\\
  -DTensile_LIBRARY_FORMAT=%{tensile_library_format} \\\
  -DTensile_VERBOSE=%{tensile_verbose} \\\
  -DTensile_DIR=${TP}/cmake \\\
  -DBUILD_WITH_PIP=OFF \\\
  -DTensile_LOGIC=asm_full \\\
  -DTensile_CODE_OBJECT_VERSION=default \\\
  -DTensile_SEPARATE_ARCHITECTURES=ON \\\
  -DTensile_LAZY_LIBRARY_LOADING=ON \\\
  -DTensile_ASSEMBLER=clang++\\\

%global rocm_gpu_list_default gfx1100
%bcond_with generic
%global rocm_gpu_list_generic "gfx9-generic;gfx9-4-generic;gfx10-1-generic;gfx10-3-generic;gfx11-generic;gfx12-generic"
%if %{with generic}
%global gpu_list %{rocm_gpu_list_generic}
%else
%global gpu_list %{rocm_gpu_list_default}
%endif

Name:           rocblas
Summary:        BLAS implementation for ROCm
License:        MIT AND BSD-3-Clause
URL:            https://github.com/ROCm/rocm-libraries

%if %{with gitcommit}
Version:        git%{date0}.%{shortcommit0}
Release:        1%{?dist}
Source0:        %{url}/archive/%{commit0}/rocm-libraries-%{shortcommit0}.tar.gz
%else
Version:        %{rocm_version}
Release:        1%{?dist}
Source0:        %{url}/releases/download/rocm-%{version}/%{upstreamname}.tar.gz#/%{upstreamname}-%{version}.tar.gz
%endif

Patch1:         0001-fixup-install-of-tensile-output.patch
# https://github.com/ROCm/rocm-libraries/commit/6221075881f3ea8e9dfa0d985f22005c74ae1f52
Patch2:         0002-fix-nodiscard-return-value-ignored.patch

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  rocm-cmake
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocm-hip-devel
BuildRequires:  rocr-runtime-devel
#BuildRequires:  rocm-rpm-macros

BuildRequires:  hipcc
BuildRequires:  rocm-device-libs
BuildRequires:  llvm
BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  compiler-rt
BuildRequires:  lld

%if %{with tensile}
#BuildRequires:  python3dist(tensile)
BuildRequires:  python3dist(Tensile)
Requires:       python3dist(msgpack)
BuildRequires:  msgpack-devel
%global tensile_verbose 1
%global tensile_library_format msgpack
%else
%global tensile_verbose %{nil}
%global tensile_library_format %{nil}
%endif # tensile

%if %{with compress}
BuildRequires:  pkgconfig(libzstd)
%endif

%if %{with test}

BuildRequires:  libomp-devel
BuildRequires:  rocminfo
BuildRequires:  rocm-smi-devel

BuildRequires:  gcc-gfortran
BuildRequires:  gtest-devel
BuildRequires:  python3dist(pyyaml)
BuildRequires:  blas-devel
%global blaslib cblas
%endif

BuildRequires:  ninja

Provides:       rocblas = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

%description
rocBLAS is the AMD library for Basic Linear Algebra Subprograms
(BLAS) on the ROCm platform. It is implemented in the HIP
programming language and optimized for AMD GPUs.

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{rocblas_name}%{?_isa} = %{version}-%{release}
Requires:       rocm-hip-devel

%description devel
%{summary}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       diffutils

%description test
%{summary}
%endif

%prep
%if %{with gitcommit}
%setup -q -n rocm-libraries-%{commit0}
cd projects/rocblas
%patch -P1 -p1 
%else
%autosetup -p1 -n %{upstreamname}
%endif
sed -i -e 's@pkg_search_module(PKGBLAS cblas)@pkg_search_module(PKGBLAS %blaslib)@' clients/CMakeLists.txt
    
sed -i -e 's@target_link_libraries( rocblas-test PRIVATE ${BLAS_LIBRARY} ${GTEST_BOTH_LIBRARIES} roc::rocblas )@target_link_libraries( rocblas-test PRIVATE %blaslib ${GTEST_BOTH_LIBRARIES} roc::rocblas )@' clients/gtest/CMakeLists.txt

# no git in this build
sed -i -e 's@find_package(Git REQUIRED)@find_package(Git)@' library/CMakeLists.txt

# On Tumbleweed Q2,2025
# /usr/include/gtest/internal/gtest-port.h:279:2: error: C++ versions less than C++14 are not supported.
#   279 | #error C++ versions less than C++14 are not supported.
# Convert the c++11's to c++14
sed -i -e 's@CXX_STANDARD 11@CXX_STANDARD 14@' clients/samples/CMakeLists.txt

%build

%if %{with gitcommit}
cd projects/rocblas
%endif

# With compat llvm the system clang is wrong
CLANG_PATH=`hipconfig --hipclangpath`
export TENSILE_ROCM_ASSEMBLER_PATH=${CLANG_PATH}/clang++
export TENSILE_ROCM_OFFLOAD_BUNDLER_PATH=${CLANG_PATH}/clang-offload-bundler
# Work around problem with koji's ld
export HIPCC_LINK_FLAGS_APPEND=-fuse-ld=lld

%if %{with tensile}
TP=`/usr/bin/TensileGetPath`
%endif

CORES=`lscpu | grep 'Core(s)' | awk '{ print $4 }'`
if [ ${CORES}x = x ]; then
    CORES=1
fi
# Try again..
if [ ${CORES} = 1 ]; then
    CORES=`lscpu | grep '^CPU(s)' | awk '{ print $2 }'`
    if [ ${CORES}x = x ]; then
        CORES=4
    fi
fi

%cmake %{cmake_generator} %{cmake_config} \
    -DGPU_TARGETS=%{gpu_list} \
    -DBUILD_WITH_TENSILE=%{build_tensile} \
    -DCMAKE_INSTALL_LIBDIR=%_libdir \
    -DDEVICE_LIB_PATH=/usr/lib/clang/21/amdgcn/bitcode \
    -DHIP_DEVICE_LIB_PATH=/usr/lib/clang/21/amdgcn/bitcode



%cmake_build

%install
%if %{with gitcommit}
cd projects/rocblas
%endif

%cmake_install

rm -f %{buildroot}%{_prefix}/share/doc/rocblas/LICENSE.md

%check
%if %{with test}
%if %{with check}
export LD_LIBRARY_PATH=%{_vpath_builddir}/library/src:$LD_LIBRARY_PATH
%{_vpath_builddir}/clients/staging/rocblas-test --gtest_brief=1
%endif
%endif

%files -n %{rocblas_name}
%if %{with gitcommit}
%license projects/rocblas/LICENSE.md
%else
%license LICENSE.md
%endif
%{_libdir}/librocblas.so.5{,.*}
%if %{with tensile}
%{_libdir}/rocblas/
%endif

%files devel
%if %{with gitcommit}
%doc projects/rocblas/README.md
%else
%doc README.md
%endif
%{_includedir}/rocblas/
%{_libdir}/cmake/rocblas/
%{_libdir}/librocblas.so

%if %{with test}
%files test
%{_bindir}/rocblas*
%endif

%changelog
* Mon Dec 15 2025 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
