# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Need GPU to run tests
%bcond test 0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 24

%ifarch x86_64 riscv64
# Large kernel builds need the 32-job workers on both validation architectures.
#!BuildConstraint: hardware:jobs 32
%endif

Name:           miopen
Version:        %{rocm_version}
Release:        %autorelease
Summary:        AMD's Machine Intelligence Library
License:        MIT AND BSD-2-Clause AND Apache-2.0
URL:            https://github.com/ROCm/MIOpen
#!RemoteAsset:  sha256:1134726a9ffad9da77db3716031241fbe48f792a268bc83daf01cc6e33fe29d8
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/miopen.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n miopen

BuildOption(conf):  -G Ninja
# The distribution supplies the toolchain and dependencies. Avoid the upstream
# standalone fallback, which fetches even disabled AI/test dependencies.
BuildOption(conf):  -DCMAKE_TOOLCHAIN_FILE=/dev/null
BuildOption(conf):  -DMIOPEN_STANDALONE_BUILD=OFF
# Upstream-fixed host bundle/feature handling permits the native distro triple,
# which also matches the installed compiler-rt directory.
BuildOption(conf):  -DCMAKE_HIP_COMPILER=%{_libdir}/rocm/llvm%{llvm_maj_ver}/bin/clang++
BuildOption(conf):  -DCMAKE_HIP_COMPILER_ROCM_ROOT=%{_prefix}
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBoost_USE_STATIC_LIBS=OFF
BuildOption(conf):  -DMIOPEN_BUILD_DRIVER=OFF
BuildOption(conf):  -DMIOPEN_ENABLE_AI_IMMED_MODE_FALLBACK=OFF
BuildOption(conf):  -DMIOPEN_ENABLE_AI_KERNEL_TUNING=OFF
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{_libdir}/rocm/llvm%{llvm_maj_ver}/bin/clang++
%if %{with test}
BuildOption(conf):  -DBUILD_TESTING=ON
BuildOption(conf):  -DMIOPEN_TEST_ALL=ON
%else
BuildOption(conf):  -DBUILD_TESTING=OFF
%endif
# Disable optional backends(CK) not yet packaged
BuildOption(conf):  -DMIOPEN_USE_COMPOSABLEKERNEL=OFF
BuildOption(conf):  -DMIOPEN_USE_MLIR=OFF

BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  hipblaslt-devel >= %{rocm_version}
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocblas-devel >= %{rocm_version}
BuildRequires:  cmake(rocblas)
BuildRequires:  rocrand-devel >= %{rocm_version}
BuildRequires:  cmake(rocrand)
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  rocm-clang >= 24.0.0~git20261109.b1de84e-13
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  half
BuildRequires:  hipcc
BuildRequires:  hipblas-common-devel
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(bzip2)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  rocm-core-devel >= %{rocm_version}
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
BuildRequires:  roctracer-devel

Requires:       cmake(hip)
Requires:       cmake(rocrand)
Requires:       gcc-c++

%patchlist
# Keep half conversion explicit for the distribution C++ toolchain.
2002-workaround-half-float-expr-deduction.patch
# Locate LLVM 24 under /usr/lib64, relative to the /usr ROCm prefix.
2004-fix-clang-rel-path.patch
# BF16 MFMA argument bit patterns: merged upstream PR 13016, one file only.
# https://github.com/ROCm/rocm-libraries/commit/d7b6c31cb268642a7b8f97cc202fa418ea3d4190
1001-upstream-hipconv-bf16-mfma.patch
# Same merged commit: FP8 MFMA/WMMA conversions and their vector aliases.
1002-upstream-hipconv-fp8-operands.patch
# GCC 14+ std::array exceeds Clang constexpr steps: merged upstream PR 11989.
# https://github.com/ROCm/rocm-libraries/commit/37920953b271d40f1cce9f2ab38d5e4d68c0cd2b
1003-upstream-hipconv-constexpr-limit.patch

%global _description %{expand:
AMD's library for high performance machine learning primitives.
MIOpen supports convolution, batch normalization, activation, pooling,
RNN/LSTM/GRU, and attention/transformer operations for the HIP backend.
}

%description
%{_description}

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{_description}

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}
%endif

%prep -a
# MIOpen tries to download googletest; disable when not needed
%if %{without test}
sed -i -e 's@add_subdirectory(test)@#add_subdirectory(test)@' CMakeLists.txt
sed -i -e 's@add_subdirectory(speedtests)@#add_subdirectory(speedtests)@' CMakeLists.txt
%endif

# Use the standard data directory for the MIOpen kernel database
sed -i -e 's@GetLibPath().parent_path() / "share/miopen/db"@"%{_datadir}/miopen/db"@' src/db_path.cpp.in

%conf -p
export HIP_CLANG_PATH=%{_libdir}/rocm/llvm%{llvm_maj_ver}/bin
export PATH="$HIP_CLANG_PATH":%{rocmllvm_bindir}:$PATH

%build -p
export HIP_CLANG_PATH=%{_libdir}/rocm/llvm%{llvm_maj_ver}/bin
export PATH="$HIP_CLANG_PATH":%{rocmllvm_bindir}:$PATH

%install -a
rm -f %{buildroot}%{_datadir}/doc/miopen-hip/LICENSE.md

%files
%doc README.md
%license LICENSE.md
%{_libdir}/libMIOpen.so.1{,.*}
%{_libexecdir}/miopen/

%files devel
%{_datadir}/miopen/
%{_includedir}/miopen/
%{_libdir}/cmake/miopen/
%{_libdir}/libMIOpen.so

%if %{with test}
%files test
%{_bindir}/test*
%endif

%changelog
%autochangelog
