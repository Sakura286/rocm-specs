# SPDX-FileCopyrightText: (C) 2025 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.14
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 23

Name:           hipify
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Convert CUDA to HIP
License:        MIT
URL:            https://github.com/ROCm/HIPIFY
#!RemoteAsset:  sha256:6adf9be7745f72990ee844451702d8ee54f9cbbd5d229ae9f1a1b2cb377ddda0
Source0:        https://github.com/ROCm/HIPIFY/archive/6acec7751d2b2bfe162dba9efdcf7c16efb27bd8/HIPIFY-6acec7751d2b2bfe162dba9efdcf7c16efb27bd8.tar.gz
BuildSystem:    cmake

# Use the distribution LLVM layout.
Patch0:         0001-prepare-hipify-cmake.patch

BuildOption(prep):  -n HIPIFY-6acec7751d2b2bfe162dba9efdcf7c16efb27bd8

BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_PREFIX_PATH=%{rocmllvm_cmakedir}/..

BuildRequires:  chrpath
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang-devel(major) = %{llvm_maj_ver}
BuildRequires:  clang-static(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  clang%{llvm_maj_ver}-tools-extra-devel
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  lld-devel(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  llvm-devel(major) = %{llvm_maj_ver}
BuildRequires:  llvm-static(major) = %{llvm_maj_ver}
BuildRequires:  perl
BuildRequires:  pkgconfig(zlib)
BuildRequires:  rocm-llvm-macros

%description
HIPIFY is a set of tools to translate CUDA source code into portable
HIP C++ automatically.

%check
echo "void f(int *a, const cudaDeviceProp *b) { cudaChooseDevice(a,b); }" > b.cu
echo "void f(int *a, const hipDeviceProp_t *b) { hipChooseDevice(a,b); }" > e.hip
./bin/hipify-perl b.cu -o t.hip
diff e.hip t.hip

%install -a
rm -rf %{buildroot}/usr/hip
# Fix executable perm:
chmod a+x %{buildroot}%{_bindir}/*
# Fix script shebang (Fedora doesn't allow using "env"):
sed -i 's|\(/usr/bin/\)env perl|\1perl|' %{buildroot}%{_bindir}//hipify-perl

# Fix
# /usr/bin/hipify-clang: error while loading shared libraries: libclang-cpp.so.19.0git
chrpath %{buildroot}%{_bindir}/hipify-clang -r %rocmllvm_libdir

rm -rf %{buildroot}%{_includedir}

%files
%doc README.md
%license LICENSE.txt
%{_bindir}/hipify-clang
%{_bindir}/hipify-perl
%{_libexecdir}/hipify

%changelog
%autochangelog
