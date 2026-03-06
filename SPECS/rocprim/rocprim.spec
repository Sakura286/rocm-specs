# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Test cost too much time
%bcond test 0

%global rocm_version 7.1.1

# Compiler is hipcc, which is clang based:
%global toolchain clang
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')

Name:           rocprim
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm parallel primatives
License:        MIT AND BSD-3-Clause
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset
Source0:        %{url}/releases/download/rocm-%{version}/rocPRIM.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF
BuildOption(conf):  -DBUILD_TEST=%{?with_test:ON}%{!?with_test:OFF}
BuildOption(conf):  -DCMAKE_AR=%rocmllvm_bindir/llvm-ar
BuildOption(conf):  -DCMAKE_BUILD_TYPE=%build_type
BuildOption(conf):  -DCMAKE_C_COMPILER=%rocmllvm_bindir/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%rocmllvm_bindir/clang++
BuildOption(conf):  -DCMAKE_LINKER=%rocmllvm_bindir/ld.lld
BuildOption(conf):  -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/..
BuildOption(conf):  -DCMAKE_RANLIB=%rocmllvm_bindir/llvm-ranlib
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DROCM_SYMLINK_LIBS=OFF

BuildRequires:  clang-devel
BuildRequires:  clang-tools-extra-devel
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  gcc-c++
BuildRequires:  lld-devel
BuildRequires:  llvm-devel
%if %{with test}
BuildRequires:  pkgconfig(gtest)
%endif
BuildRequires:  python3
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocminfo

%description
The rocPRIM is a header-only library providing HIP parallel primitives
for developing performant GPU-accelerated code on AMD ROCm platform.

%package        devel
Summary:        ROCm parallel primatives
Provides:       %{name}-static = %{version}-%{release}
# the devel subpackage is only headers and cmake infra
BuildArch:      noarch

%description    devel
The rocPRIM is a header-only library providing HIP parallel primitives
for developing performant GPU-accelerated code on AMD ROCm platform.

%if %{with test}
%package        test
Summary:        upstream tests for ROCm parallel primatives
Provides:       %{name}-test = %{version}-%{release}
Requires:       %{name}-devel
Requires:       gtest

%description    test
tests for the rocPRIM package
%endif

%prep -a
# In file included from rocPRIM-rocm-6.4.2/test/rocprim/test_texture_cache_iterator.cpp:26: 
# ../rocprim/include/rocprim/iterator/texture_cache_iterator.hpp:231:13: error:
#   'tex1Dfetch<int, nullptr>' is unavailable: The image/texture API not supported on the device
# Remove fail to build test
sed -i -e 's@add_rocprim_test("rocprim.texture_cache_iterator"@#add_rocprim_test("rocprim.texture_cache_iterator"@' test/rocprim/CMakeLists.txt
grep texture_cach test/rocprim/CMakeLists.txt

%install -a
rm -f %{buildroot}%{_prefix}/share/doc/rocprim/LICENSE.md
%if %{with test}
# force the cmake test file to use absolute paths for its referenced binaries
sed -i -e 's@\.\.@\/usr\/bin@' %{buildroot}%{_bindir}/%{name}/CTestTestfile.cmake
%endif

%files devel
%doc README.md
%license LICENSE.md
%license NOTICES.txt
%{_includedir}/%{name}
%{_datadir}/cmake/rocprim

%if %{with test}
%files test
%{_bindir}/test*
%{_datadir}/libtest*
%{_bindir}/%{name}/
%endif

%changelog
%{?autochangelog}
