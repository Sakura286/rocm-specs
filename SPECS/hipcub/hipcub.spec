# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipcub is a header-only ROCm library. No compiled runtime library is produced.
# All files go in the base package per SOP rule 6.
%global debug_package %{nil}

%bcond test 0
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm stack builds with clang
%global toolchain clang

Name:           hipcub
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm port of CUDA CUB (header-only)
Url:            https://github.com/ROCm/rocm-libraries
VCS:            git:https://github.com/ROCm/hipCUB.git
License:        BSD-3-Clause AND MIT
#!RemoteAsset:  sha256:6dadbb7689c7906493ec42f56792d9557f0293670a86059c9c188851f399647b
Source:         %{url}/releases/download/rocm-%{version}/hipcub.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DROCM_SYMLINK_LIBS=OFF
BuildOption(conf):  -DBUILD_FILE_REORG_BACKWARD_COMPATIBILITY=OFF
BuildOption(conf):  -DBUILD_TEST=%{build_test}

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocprim)
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
%if %{with test}
BuildRequires:  cmake(GTest)
BuildRequires:  rocminfo
%endif

# No compiled runtime: provide cmake() so dependents can use cmake(hipcub)
Provides:       cmake(hipcub) = %{version}

%description
hipCUB is a thin header-only wrapper library on top of rocPRIM which enables
developers to render portable HIP code. Existing CUDA CUB source code can
be recompiled in HIP using hipCUB.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep -a
# Fix cmake install lib directory
sed -i -e 's/ROCM_INSTALL_LIBDIR lib/ROCM_INSTALL_LIBDIR %{_lib}/' \
    cmake/ROCMExportTargetsHeaderOnly.cmake

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
