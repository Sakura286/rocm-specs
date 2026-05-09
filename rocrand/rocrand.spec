%global upstreamname rocRAND
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%bcond compat 0
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}/
%global pkg_suffix -%{rocm_release}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%endif
%global rocrand_name rocrand%{pkg_suffix}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//' )

%bcond debug 0
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

# relevant HW is required to run %check
%bcond test 0
# enable building of tests if test is enabled
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

# For docs
%bcond doc 0

# Use ninja if it is available
%bcond ninja 1

%if %{with ninja}
%global cmake_generator -G Ninja
%else
%global cmake_generator %{nil}
%endif

# The common parts of the cmake configuration
%global cmake_config \\\
  -DBUILD_TEST=%build_test \\\
  -DCMAKE_AR=%rocmllvm_bindir/llvm-ar \\\
  -DCMAKE_BUILD_TYPE=%build_type \\\
  -DCMAKE_EXPORT_COMPILE_COMMANDS=%{build_compile_db} \\\
  -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \\\
  -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \\\
  -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \\\
  -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \\\
  -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/.. \\\
  -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld \\\
  -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib \\\
  -DCMAKE_SKIP_RPATH=ON \\\
  -DROCM_SYMLINK_LIBS=OFF

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

%global gpu_list %{rocm_gpu_list_default}
%global _gpu_list gfx1100

# export an llvm compilation database
# Useful for input for other llvm tools
%bcond export 0
%if %{with export}
%global build_compile_db ON
%else
%global build_compile_db OFF
%endif

Name:           rocrand%{pkg_suffix}
Version:        %{rocm_version}
Release:        7%{?dist}
Summary:        ROCm random number generator

Url:            https://github.com/ROCm/rocRAND
License:        MIT AND BSD-3-Clause
Source0:        %{url}/archive/rocm-%{version}.tar.gz#/%{upstreamname}-%{version}.tar.gz

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

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-hip%{pkg_suffix}-devel
BuildRequires:  rocr-runtime%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}-modules

%if %{with test} || %{with check}
BuildRequires:  gtest-devel
%endif

%if %{with doc}
BuildRequires:  doxygen
%endif

%if %{with ninja}
BuildRequires:  ninja
%endif

Provides:       rocrand%{pkg_suffix} = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

%description
The rocRAND project provides functions that generate pseudo-random and
quasi-random numbers.

The rocRAND library is implemented in the HIP programming language and
optimized for AMD's latest discrete GPUs. It is designed to run on top of AMD's
Radeon Open Compute ROCm runtime, but it also works on CUDA enabled GPUs.

%package devel
Summary:        The rocRAND development package
Requires:       %{rocrand_name}%{?_isa} = %{version}-%{release}

%description devel
The rocRAND development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{rocrand_name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%if %{with gitcommit}
%setup -q -n rocm-libraries-%{commit0}
cd projects/rocrand
%else
%autosetup -p1 -n %{upstreamname}-rocm-%{version}
%endif


# On Tumbleweed Q3,2025
# https://github.com/ROCm/rocm-libraries/issues/83
# /usr/include/gtest/internal/gtest-port.h:273:2: error: C++ versions less than C++17 are not supported.
# Convert the c++11's to c++17
#sed -i -e 's@set(CMAKE_CXX_STANDARD 11)@set(CMAKE_CXX_STANDARD 17)@' {,test/{cpp_wrapper,package}/}CMakeLists.txt

%build

%cmake %{cmake_generator} %{cmake_config} \
       -DAMDGPU_TARGETS=%{gpu_list} \

%cmake_build

%install

%cmake_install

rm -f %{buildroot}%{pkg_prefix}/share/doc/rocrand/LICENSE.md

%files -n %{rocrand_name}
%doc README.md
%license LICENSE.md

%if %{with debug}
%{pkg_prefix}/%{pkg_libdir}/librocrand-d.so.1{,.*}
%else
%{pkg_prefix}/%{pkg_libdir}/librocrand.so.1{,.*}
%endif

%files devel 
%{pkg_prefix}/include/rocrand/
%{pkg_prefix}/%{pkg_libdir}/cmake/rocrand/
%if %{with debug}
%{pkg_prefix}/%{pkg_libdir}/librocrand-d.so
%else
%{pkg_prefix}/%{pkg_libdir}/librocrand.so
%endif

%if %{with test}
%files test
%{pkg_prefix}/bin/test_*
%{pkg_prefix}/bin/rocRAND/
%endif

%changelog
* Mon Jan 26 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
