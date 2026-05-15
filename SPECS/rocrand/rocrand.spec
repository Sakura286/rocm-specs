# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Sakura286 <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# rocRAND need a GPU to run tests, but we could still
# keep the test cases for packagers who have a GPU, so make it optional.
%bcond test 0

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm builds with clang
%global toolchain clang

Name:           rocrand
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm random number generator
Url:            https://github.com/ROCm/rocRAND
VCS:            git:https://github.com/ROCm/rocRAND.git
License:        MIT AND BSD-3-Clause
#!RemoteAsset:  sha256:15c33c595aa8e4de1d8b3736df9eaf2ceba7914ffebe718f0997b0da28215d9e
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DCMAKE_SKIP_RPATH=ON
BuildOption(conf):  -DROCM_SYMLINK_LIBS=OFF
%if %{with test}
BuildOption(conf):  -DBUILD_TEST=ON
%else
BuildOption(conf):  -DBUILD_TEST=OFF
%endif

BuildRequires:  clang
BuildRequires:  clang-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  compiler-rt
BuildRequires:  lld
BuildRequires:  llvm
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

%package devel
Summary:        The rocRAND development package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The rocRAND development package.

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%if %{with test}
%check -p
export LD_LIBRARY_PATH=$PWD/%{__cmake_builddir}/library:$LD_LIBRARY_PATH
%endif

%install -a
rm -f %{buildroot}%{_datadir}/doc/rocrand/LICENSE.md

%files
%license LICENSE.md
%doc README.md
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
