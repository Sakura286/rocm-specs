# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%global toolchain clang

%global rocm_release 7.2
%global rocm_patch   4
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           hipcub
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm port of CUDA CUB (header-only)
License:        BSD-3-Clause AND MIT
Url:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:2b08b0e7fc8d97717bc9656a0cc0e502dd221770f34deb8721ced2239939d779
Source:         %{url}/releases/download/rocm-%{version}/hipcub.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_TEST=%{build_test}

BuildRequires:  clang22
BuildRequires:  clang22-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocprim)
BuildRequires:  compiler-rt22
BuildRequires:  lld22
BuildRequires:  llvm22
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros

%description
hipCUB is a thin header-only wrapper library on top of rocPRIM which enables
developers to render portable HIP code. Existing CUDA CUB source code can
be recompiled in HIP using hipCUB.

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%prep -a
# Fix cmake install lib directory
sed -i -e 's/ROCM_INSTALL_LIBDIR lib/ROCM_INSTALL_LIBDIR %{_lib}/' \
    cmake/ROCMExportTargetsHeaderOnly.cmake

%install -a
rm -f %{buildroot}/%{_datadir}/doc/hipcub/LICENSE.txt

%files
%doc README.md
%license LICENSE.txt
%{_includedir}/hipcub/
%{_libdir}/cmake/hipcub/

%if %{with test}
%files test
%{_bindir}/test_*
%{_bindir}/hipcub/
%endif

%changelog
%autochangelog
