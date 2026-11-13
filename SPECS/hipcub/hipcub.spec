# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# hipCUB need GPU to run test
%bcond test 0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 24

%ifarch x86_64 riscv64
# Compiling the full four-GPU test suite took 3445s with only four x86 jobs.
#!BuildConstraint: hardware:jobs 32
%endif

Name:           hipcub
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm port of CUDA CUB (header-only)
License:        BSD-3-Clause AND MIT
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:e6fedbf9d03c242be7a4d44cfb6016214f3b4120a1ff8d422f4a49add629efe4
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/hipcub.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n hipcub

BuildOption(conf):  -DROCPRIM_FETCH_METHOD=PACKAGE
BuildOption(conf):  -G Ninja
# Offload bundle IDs require an explicit host environment component.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT=--target=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_TEST=ON
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(GTest)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocprim-devel >= %{rocm_version}
BuildRequires:  cmake(rocprim)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros

%global _description %{expand:
hipCUB is a thin header-only wrapper library on top of rocPRIM which enables
developers to render portable HIP code. Existing CUDA CUB source code can
be recompiled in HIP using hipCUB.
}

%description
%{_description}

%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%install -a
rm -f %{buildroot}/%{_datadir}/doc/hipcub/LICENSE.txt

%if %{without test}
%check
%endif

%files
%doc README.md
%license LICENSE.txt
%{_includedir}/hipcub/
%{_libdir}/cmake/hipcub/

%files test
%{_bindir}/test_*
%{_bindir}/hipcub/

%changelog
%autochangelog
