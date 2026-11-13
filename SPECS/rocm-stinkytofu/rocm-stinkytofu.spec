# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global llvm_maj_ver 24

Name:           rocm-stinkytofu
Version:        10.1.0
Release:        %autorelease
Summary:        AMD GPU assembly optimizer used by ROCm TensileLite
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:acc43368e45179c66492e90ba766f4a1001342f3eb244e378291baa4afa160ca
Source0:        %{url}/releases/download/therock-10.1/stinkytofu.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n stinkytofu
BuildOption(conf):  -G Ninja
# Explicit distro compilers replace the monorepo-only default toolchain include.
BuildOption(conf):  -DCMAKE_TOOLCHAIN_FILE=/dev/null
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++
BuildOption(conf):  -DBUILD_SHARED_LIBS=ON
BuildOption(conf):  -DSTINKYTOFU_BUILD_TESTS=ON
BuildOption(conf):  -DSTINKYTOFU_BUILD_PYTHON=OFF
BuildOption(conf):  -DSTINKYTOFU_BUILD_EXAMPLES=ON
BuildOption(conf):  -DSTINKYTOFU_INSTALL_RPATH_USE_LINK_PATH=OFF

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  cmake
BuildRequires:  cmake(GTest)
BuildRequires:  cmake(amd_comgr)
BuildRequires:  gcc-c++
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  rocm-cmake >= %{version}
BuildRequires:  rocm-comgr-devel >= %{version}
BuildRequires:  rocm-llvm-macros

%description
StinkyTofu provides AMD GPU assembly optimization passes and intrinsic
compilation for TensileLite. This package follows the ROCm release;
the upstream library ABI version is 0.1.0.

%package        devel
Summary:        Development files for StinkyTofu
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and CMake exports for the StinkyTofu optimizer library.

%prep -a
# Upstream hard-codes lib for its libraries, CMake exports and intrinsic data.
sed -i 's/DESTINATION lib/DESTINATION %{_lib}/g' \
    CMakeLists.txt tools/intrinsic-compiler/CMakeLists.txt

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%check
%ctest

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libstinkytofu.so.*
%{_libdir}/intrinsics.st.bc
%{_libdir}/stinkytofu/
%{_bindir}/intrinsic-compiler
%{_bindir}/stinkytofu-opt
%{_bindir}/stinkytofu-check

%files devel
%{_libdir}/libstinkytofu.so
%{_libdir}/cmake/stinkytofu/
%{_includedir}/stinkytofu/

%changelog
%autochangelog
