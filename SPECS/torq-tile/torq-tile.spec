# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Upstream CMakeLists VERSION is 0.1.0 and the README badge matches, but
# https://github.com/XUANTIE-RV/torq-tile has no tags or GitHub releases.
# Package current main (2a0c0e1, 2026-05-22) as a never-released snapshot.
%global commit 2a0c0e1d03dbd644f3dcfbd62a4953481bbc1569

# Host C++ micro-kernels; no HIP/hipcc. openRuyi's cmake %conf writes
# CFLAGS/CXXFLAGS from the distro rva23u64 set, not from %{optflags}
# (log/torq-tile-01.log: optflags only landed on FFLAGS/FCFLAGS). Append
# zvfh/zfbfmin/zvfbfwma so try_compile enables FP16 and BF16 kernels;
# gcc uses the last -march.
%global torq_tile_march -march=rv64gcv_zfh_zvfh_zfbfmin_zvfbfmin_zvfbfwma

Name:           torq-tile
Version:        0+git20260908.2a0c0e1
Release:        %autorelease
Summary:        RISC-V Vector micro-kernels for AI workloads
License:        Apache-2.0
URL:            https://github.com/XUANTIE-RV/torq-tile
VCS:            git:%{url}.git
#!RemoteAsset:  sha256:4485123eb14c0e45aa1f0d857339d85bbe8162ab51b784e4ea5aec7f7cfc64f1
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz
# Install into libdir, ship a find_package(torq_tile) config, and refuse an
# empty library when the compiler has no RVV support.
Patch2000:      2000-gnu-installdirs-and-cmake-config.patch
# All sources are RVV kernels; cmake try_compile yields no objects on other
# ISAs. openRuyi keeps ExclusiveArch for genuinely arch-specific packages
# (see opensbi).
ExclusiveArch:  riscv64
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DTORQ_TILE_BUILD_SHARED=ON
# Tests FetchContent googletest (network) and need RVV hardware to run.
BuildOption(conf):  -DTORQ_TILE_BUILD_TEST=OFF
BuildOption(conf):  -DTORQ_TILE_BUILD_BENCHMARK=OFF
# cmake %conf assigns CFLAGS/CXXFLAGS after %conf -p, so extra -march must
# go on the cmake command line. ${CFLAGS} expands in the generated script.
BuildOption(conf):  -DCMAKE_C_FLAGS="${CFLAGS} %{torq_tile_march}"
BuildOption(conf):  -DCMAKE_CXX_FLAGS="${CXXFLAGS} %{torq_tile_march}"

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  ninja

%description
TORQ-Tile is a library of RISC-V Vector micro-kernels for AI workloads,
with GEMM, convolution, implicit GEMM, and depthwise convolution variants
in FP32, FP16, BF16, INT8, and INT4. The API is stateless and does not
allocate memory or schedule work; callers include the headers and link
the shared library.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and CMake package files for building applications that use
TORQ-Tile micro-kernels.

# GitHub commit archive extracts to torq-tile-<fullhash>, not Name-Version.
%prep
%autosetup -p1 -n %{name}-%{commit}

%files
%doc README.md
%license LICENSE
%{_libdir}/libtorq_tile.so.0{,.*}

%files devel
%{_includedir}/torq_tile/
%{_libdir}/cmake/torq_tile/
%{_libdir}/libtorq_tile.so

%changelog
%autochangelog
