# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# rocThrust needs a GPU to run tests, but we could still
# keep the test cases for packagers who have a GPU, so make it optional.
%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%global rocm_release 7.2
%global rocm_patch   4
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm builds with clang
%global toolchain clang

Name:           rocthrust
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm Thrust library

Url:            https://github.com/ROCm/rocThrust
VCS:            git:https://github.com/ROCm/rocThrust.git
License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT
# All files are Apache 2.0 with some exceptions:
# ./cmake contains only files under MIT
# ./internal/benchmark/*.py are dual licensed Apache 2.0 and Boost 1.0
# ./thrust/ contain some header files that are Boost 1.0 licensed
# ./thrust/ contain some headers that are dual Apache 2.0 and Boost 1.0
# ./thrust/cmake/FindTBB.cmake is public domain
# ./thrust/detail/allocator/allocator_traits.h is dual Apache 2.0 and MIT
# ./thrust/detail/complex contains BSD 2 clause licensed headers
#!RemoteAsset:  sha256:b49bac5243d33092b242823cdf1d33fe7f05556bbbd2ca9ac4d5394e49f68b1c
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_TEST=%{build_test}

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  cmake(hip)
BuildRequires:  cmake(rocprim)
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%description
Thrust is a parallel algorithm library. This library has been
ported to HIP/ROCm platform, which uses the rocPRIM library.

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{summary}

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%prep -a
# ROCMExportTargetsHeaderOnly.cmake hardcodes 'lib' as the library directory.
# Change it to the correct platform-specific library directory.
sed -i -e 's/ROCM_INSTALL_LIBDIR lib/ROCM_INSTALL_LIBDIR %{_lib}/' cmake/ROCMExportTargetsHeaderOnly.cmake

%install -a
rm -f %{buildroot}%{_docdir}/rocthrust/LICENSE

%files
%doc README.md
%license LICENSE
%license NOTICES.txt

%files devel
%{_includedir}/thrust/
%{_libdir}/cmake/rocthrust/

%if %{with test}
%files test
%{_bindir}/test_*
%{_bindir}/rocthrust/
%endif

%changelog
%autochangelog
