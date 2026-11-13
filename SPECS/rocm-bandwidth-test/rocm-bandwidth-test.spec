# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# This standalone tool has no therock-7.14.1 release; use its latest ROCm tag.
%global llvm_maj_ver 23
%global upstreamname rocm_bandwidth_test
%global rocm_release 7.2
%global rocm_patch 4
%global rocm_version %{rocm_release}.%{rocm_patch}

Name:           rocm-bandwidth-test
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Bandwidth test for ROCm
License:        MIT
URL:            https://github.com/ROCm/rocm_bandwidth_test
#!RemoteAsset:  sha256:eb3256351c00123d4536e93dd1500f5edd6fa46e5acd777c6cce8f9db894ccc0
Source0:        %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n rocm_bandwidth_test-rocm-%{version}
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++
BuildOption(conf):  -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/..
BuildOption(conf):  -DAMD_APP_ROCM_BUILD_AUTO_DETECT=OFF
BuildOption(conf):  -DAMD_APP_SUBMODULES_TRY_CHECKOUT=OFF
BuildOption(conf):  -DAMD_APP_COMPILER_TRY_CLANG=OFF
BuildOption(conf):  -DAMD_APP_LINKER_TRY_MOLD=OFF
BuildOption(conf):  -DAMD_APP_TREAT_WARNINGS_AS_ERRORS=OFF
BuildOption(conf):  '-DAMD_WORK_BENCH_INCLUDE_PLUGINS=builtin;tb'
BuildOption(conf):  -DUSE_LOCAL_FMT_LIB=ON
BuildOption(conf):  -DUSE_LOCAL_BOOST=ON
BuildOption(conf):  -DUSE_LOCAL_BOOST_STACKTRACE=ON
BuildOption(conf):  -DUSE_LOCAL_NLOHMANN_JSON=ON
BuildOption(conf):  -DUSE_LOCAL_SPDLOG=ON
BuildOption(conf):  -DUSE_LOCAL_CLI11=ON


BuildRequires:  make
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  rocr-runtime-devel >= 7.14.1
BuildRequires:  rocm-hip-devel >= 7.14.1
BuildRequires:  rocm-cmake >= 7.14.1
BuildRequires:  rocm-llvm-macros
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  git
BuildRequires:  cmake(fmt)
BuildRequires:  boost-devel
BuildRequires:  cmake(CLI11)
BuildRequires:  cmake(nlohmann_json)
BuildRequires:  cmake(spdlog)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(numa)

%patchlist
# Use distribution dependencies and standard library/plugin installation.
2000-system-build-and-install.patch

%description
ROCm Bandwidth Test is designed to capture the performance
characteristics of buffer copying and kernel read and write
operations. The benchmark help screen shows various options
for initiating copy, read, and write operations. In
addition to this, you can also query the system topology in
terms of memory pools and their agents.

%conf -p
export ROCM_PATH=%{_prefix}
export PATH=%{rocmllvm_bindir}:$PATH

%build -p
export ROCM_PATH=%{_prefix}
export PATH=%{rocmllvm_bindir}:$PATH

%install -a
ln -s rocm_bandwidth_test %{buildroot}%{_bindir}/rocm-bandwidth-test

%check
# The command line parser can be checked without a GPU.
%{_vpath_builddir}/rocm_bandwidth_test --help

%files
%doc README.md
%license LICENSE.md
%{_bindir}/rocm-bandwidth-test
%{_bindir}/rocm_bandwidth_test
%{_libdir}/libamd_work_bench.so*
%{_libdir}/libamd_tb.so*
%{_libdir}/rocm_bandwidth_test/

%changelog
%autochangelog
