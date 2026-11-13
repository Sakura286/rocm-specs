# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global llvm_maj_ver 23

Name:           stinkytofu
Version:        7.14.1
Release:        %autorelease
Summary:        AMD GPU assembly intermediate representation and optimization tools
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:81ab7041097be82df68098eeb603b2cd5c1277960ced5a5111da82c452405ebb
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-%{version}/stinkytofu.tar.gz
Patch2000:      2000-standalone-install-layout.patch
Patch2001:      2001-include-climits.patch
Patch2002:      2002-isolate-parallel-parser-test-files.patch
BuildSystem:    cmake

BuildOption(prep):  -n stinkytofu
BuildOption(conf):  -G Ninja
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++
BuildOption(conf):  -DBUILD_SHARED_LIBS=ON
BuildOption(conf):  -DSTINKYTOFU_BUILD_TESTS=ON
BuildOption(conf):  -DSTINKYTOFU_BUILD_PYTHON=OFF
BuildOption(conf):  -DSTINKYTOFU_BUILD_EXAMPLES=OFF
BuildOption(check):  --output-on-failure

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  rocm-comgr-devel >= 7.14.1
BuildRequires:  cmake(GTest)
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  rocm-cmake >= 7.14.1
BuildRequires:  rocm-llvm-macros

%description
StinkyTofu provides intermediate representations, instruction metadata and
optimization passes for AMD GPU assembly. It is used by the rocISA kernel
generator in hipBLASLt.

%package devel
Summary:        Development files and rocISA conversion sources for StinkyTofu
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers, CMake configuration and conversion sources for building consumers
of the StinkyTofu library.

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%files
%license LICENSE.md
%doc README.md
%{_bindir}/stinkytofu-opt
%{_bindir}/stinkytofu-check
%{_bindir}/intrinsic-compiler
%{_libdir}/libstinkytofu.so.0{,.*}
%{_libdir}/stinkytofu/

%files devel
%{_includedir}/stinkytofu/
%{_libdir}/libstinkytofu.so
%{_libdir}/cmake/stinkytofu/
%{_datadir}/stinkytofu/

%changelog
%autochangelog
