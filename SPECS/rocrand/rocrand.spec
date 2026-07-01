# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Sakura286 <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# rocRAND need a GPU to run tests, but we could still
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

Name:           rocrand
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm random number generator
License:        MIT AND BSD-3-Clause
Url:            https://github.com/ROCm/rocRAND
#!RemoteAsset:  sha256:1e0295d1cf798480fe87147fc5b7d649f869a9afedd0409a4bc6548f2f097dfb
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_TEST=%{build_test}

BuildRequires:  clang22
BuildRequires:  clang22-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  compiler-rt22
BuildRequires:  lld22
BuildRequires:  llvm22
BuildRequires:  ninja
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%description
The rocRAND project provides functions that generate pseudo-random and
quasi-random numbers.

The rocRAND library is implemented in the HIP programming language and
optimized for AMD's latest discrete GPUs. It is designed to run on top of AMD's
Radeon Open Compute ROCm runtime, but it also works on CUDA enabled GPUs.

%package        devel
Summary:        The rocRAND development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The rocRAND development package.

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%install -a
rm -f %{buildroot}%{_datadir}/doc/rocrand/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_libdir}/librocrand.so.1{,.*}

%files devel
%{_includedir}/rocrand/
%{_libdir}/cmake/rocrand/
%{_libdir}/librocrand.so

%if %{with test}
%files test
%{_bindir}/rocRAND/
%{_bindir}/test_*
%endif

%changelog
%autochangelog
