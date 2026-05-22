%global upstreamname rocFFT
%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%bcond compat 0
%if %{with compat}
%global pkg_libdir lib
%global pkg_prefix %{_prefix}/lib64/rocm/rocm-%{rocm_release}
%global pkg_suffix -%{rocm_release}
%else
%global pkg_libdir %{_lib}
%global pkg_prefix %{_prefix}
%global pkg_suffix %{nil}
%endif
%global rocfft_name rocfft%{pkg_suffix}

%global toolchain rocm

# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host-fcf-protection/')

%bcond debug 0
%if %{with debug}
%global build_type DEBUG
%else
%global build_type RelWithDebInfo
%endif

# kernel oops on gfx1201
# https://github.com/ROCm/rocFFT/issues/560
%bcond test 0
%if %{with test}
# Disable rpatch checks for a local build
%global __brp_check_rpaths %{nil}
%global build_test ON
%else
%global build_test OFF
%endif

# Option to test suite for testing on real HW:
# May have to set gpu under test with
# export HIP_VISIBLE_DEVICES=<num> - 0, 1 etc.
%bcond check 0

# For docs
%bcond doc 0

# Compression type and level for source/binary package payloads.
#  "w7T0.xzdio"	xz level 7 using %%{getncpus} threads
%global _source_payload w7T0.xzdio
%global _binary_payload w7T0.xzdio

# Use rocm-llvm strip
%global __strip %rocmllvm_bindir/llvm-strip

# Use ninja if it is available
%bcond ninja 1

%if %{with ninja}
%global cmake_generator -G Ninja
%else
%global cmake_generator %{nil}
%endif

%global cmake_config \\\
  -DBUILD_CLIENTS_TESTS_OPENMP=OFF \\\
  -DBUILD_CLIENTS_TESTS=%{build_test} \\\
  -DCMAKE_AR=%rocmllvm_bindir/llvm-ar \\\
  -DCMAKE_BUILD_TYPE=%{build_type} \\\
  -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang \\\
  -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++ \\\
  -DCMAKE_CXX_FLAGS="--rtlib=compiler-rt --unwindlib=libgcc -fPIC" \\\
  -DCMAKE_C_IMPLICIT_INCLUDE_DIRECTORIES=/usr/include \\\
  -DCMAKE_CXX_IMPLICIT_INCLUDE_DIRECTORIES=/usr/include \\\
  -DCMAKE_INSTALL_LIBDIR=%{pkg_libdir} \\\
  -DCMAKE_INSTALL_PREFIX=%{pkg_prefix} \\\
  -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld \\\
  -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib \\\
  -DHIPCC_BIN_DIR=%{_bindir} \\\
  -DHIP_COMPILER=%rocmllvm_bindir/clang++ \\\
  -DHIP_PLATFORM=amd \\\
  -DROCFFT_BUILD_OFFLINE_TUNER=OFF \\\
  -DROCFFT_KERNEL_CACHE_ENABLE=OFF \\\
  -DROCM_SYMLINK_LIBS=OFF \\\
  -DSQLITE_USE_SYSTEM_PACKAGE=ON \\\
  -Dhip_DIR=/usr/lib64/cmake/hip \\\
  -DCMAKE_PREFIX_PATH="%{rocmllvm_cmakedir}/..;%{_libdir}/cmake"
#   -DHIP_COMMON_DIR=$p/hip

%global gpu_list %{rocm_gpu_list_default}
%global _gpu_list gfx1100

Name:           rocfft%{pkg_suffix}
Version:        %{rocm_version}
Release:        1%{?dist}
Summary:        ROCm Fast Fourier Transforms (FFT) library
License:        MIT

Url:            https://github.com/ROCm/%{upstreamname}
Source0:        %{url}/archive/rocm-%{version}.tar.gz#/%{upstreamname}-rocm-%{version}.tar.gz

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

BuildRequires:  python3

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  rocm-cmake%{pkg_suffix}
BuildRequires:  rocm-comgr%{pkg_suffix}-devel
BuildRequires:  rocm-llvm%{pkg_suffix}-macros
BuildRequires:  rocm-hip%{pkg_suffix}-devel
#BuildRequires:  rocm-rpm-macros%{pkg_suffix}
BuildRequires:  rocr-runtime%{pkg_suffix}-devel >= %{rocm_release}

%if %{with test}
BuildRequires:  rocrand%{pkg_suffix}-devel
BuildRequires:  fftw-devel
BuildRequires:  boost-devel
BuildRequires:  hiprand%{pkg_suffix}-devel

BuildRequires:  gtest-devel

# rocfft-test compiles some things and requires rocm-hip-devel
Requires:  rocm-hip%{pkg_suffix}-devel >= %{rocm_release}

%endif

%if %{with doc}
BuildRequires:  python3dist(sphinx)
%endif

%if %{with ninja}
BuildRequires:  ninja
%define __builder ninja
%endif

Provides:       rocfft%{pkg_suffix} = %{version}-%{release}

ExclusiveArch:  x86_64 riscv64

Patch0: 0001-cmake-use-gnu-installdirs.patch

%description
A library for computing Fast Fourier Transforms (FFT), part of ROCm.

%package devel
Summary:        The rocFFT development package
Requires:       %{rocfft_name}%{?_isa} = %{version}-%{release}
Requires:       rocm-hip%{pkg_suffix}-devel

%description devel
The rocFFT development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -n %{upstreamname}-rocm-%{version} -p 1

# Do not care so much about the sqlite version
sed -i -e 's@SQLite3 3.50.2 @SQLite3 @' cmake/sqlite.cmake

%build
# ensuring executables are PIE enabled
export LDFLAGS="${LDFLAGS} -pie"

# OpenMP tests are disabled because upstream sets rpath in that case without
# a way to skip
#
# RHEL 9 has an issue with missing symbol __truncsfhf2 in libgcc.
# So switch from libgcc to rocm-llvm's libclang-rt.builtins with
# the rtlib=compiler-rt. Leave unwind unchange with unwindlib=libgcc
%cmake %{cmake_generator} %{cmake_config} \
    -DGPU_TARGETS=%{gpu_list}

%cmake_build

%install
%cmake_install

# we don't need the rocfft_rtc_helper binary, don't package it
find %{buildroot} -type f -name "rocfft_rtc_helper" -print0 | xargs -0 -I {} /usr/bin/rm -rf "{}"

# we don't need or want the client-info file installed by rocfft
rm -rf %{buildroot}/%{pkg_prefix}/.info

rm -f %{buildroot}%{pkg_prefix}/share/doc/rocfft/LICENSE.md


%check
%if %{with test}
%if %{with check}
%{_vpath_builddir}/clients/staging/rocfft-test
%endif
%endif

%files -n %{rocfft_name}
%doc README.md
%license LICENSE.md

%{pkg_prefix}/%{pkg_libdir}/librocfft.so.0{,.*}

%files devel
%{pkg_prefix}/include/rocfft/
%{pkg_prefix}/%{pkg_libdir}/librocfft.so
%{pkg_prefix}/%{pkg_libdir}/cmake/rocfft/

%if %{with test}
%files test
%{pkg_prefix}/bin/rocfft-test
%{pkg_prefix}/bin/rtc_helper_crash
%endif

%changelog
* Mon Jan 26 2026 Yifan Xu <xuyifan@iscas.ac.cn> - 7.1.1-1
- Import from upstream
