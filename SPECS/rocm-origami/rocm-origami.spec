# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.14
%global rocm_patch   1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 23

Name:           rocm-origami
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Analytical GEMM Solution Selection
License:        MIT
URL:            https://github.com/ROCm/rocm-libraries
#!RemoteAsset:  sha256:c2a229a3c1733b84646672311fd98b00f18792976cf93d69d964757487d484c6
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-%{version}/origami.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n origami

# Build from a release tarball without requiring unavailable Git metadata.
Patch2000:      2000-rocm-origami-use-system-build-dependencies.patch

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DCMAKE_VERBOSE_MAKEFILE=ON
# GCC 16.2.0 fails to parse [[__gnu__::__noinline__]] in libstdc++ <format>;
# use Clang for both C and C++ compilation.
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  cmake
BuildRequires:  cmake(hip)
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  ninja

%global _description %{expand:
The name "origami" still evokes the elegance of transforming
a flat (2-D) sheet into intricate higher dimensional
structures. In this context, however, Origami has evolved
into a tool set for GEMM solution selection and optimization.
Inspired by the art of paper folding, the library now enables
users to explore a range of tiling and mapping configurations
and to make informed decisions on data and computation mapping
for high-performance GEMM operations.
}

%description
%{_description}

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{_description}

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%install -a
rm -f %{buildroot}%{_datadir}/doc/origami/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_libdir}/liborigami.so.1{,.*}

%files devel
%{_includedir}/origami/
%{_libdir}/cmake/origami/
%{_libdir}/liborigami.so

%changelog
%autochangelog
