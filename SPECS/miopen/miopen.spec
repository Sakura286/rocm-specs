# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Tests require an AMD GPU; keep the bcond for packagers with hardware.
%bcond test 0

%global rocm_release 7.2
%global rocm_patch   4
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm stack builds with clang
%global toolchain clang

Name:           miopen
Version:        %{rocm_version}
Release:        %autorelease
Summary:        AMD's Machine Intelligence Library
License:        MIT AND BSD-2-Clause AND Apache-2.0
Url:            https://github.com/ROCm/MIOpen
#!RemoteAsset:  sha256:983fda99d67d57f1354123101bea3af0f11f746d7ff3306bfc2700e6f6f5bb0f
Source:         %{url}/archive/rocm-%{version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -G Ninja
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBoost_USE_STATIC_LIBS=OFF
BuildOption(conf):  -DMIOPEN_BUILD_DRIVER=OFF
BuildOption(conf):  -DMIOPEN_ENABLE_AI_IMMED_MODE_FALLBACK=OFF
BuildOption(conf):  -DMIOPEN_ENABLE_AI_KERNEL_TUNING=OFF
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
%if %{with test}
BuildOption(conf):  -DBUILD_TESTING=ON
BuildOption(conf):  -DMIOPEN_TEST_ALL=ON
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
%else
BuildOption(conf):  -DBUILD_TESTING=OFF
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
%endif
# Disable optional backends not yet packaged on openRuyi
BuildOption(conf):  -DMIOPEN_USE_COMPOSABLEKERNEL=OFF
BuildOption(conf):  -DMIOPEN_USE_MLIR=OFF
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang

BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblaslt)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocblas)
BuildRequires:  cmake(rocrand)
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  clang22
BuildRequires:  clang22-tools-extra
BuildRequires:  compiler-rt22
BuildRequires:  half
BuildRequires:  hipcc
BuildRequires:  hipblas-common-devel
BuildRequires:  lld22
BuildRequires:  llvm22
BuildRequires:  ninja
BuildRequires:  pkgconfig(bzip2)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
# roctracer uses find_path/find_library rather than find_package; no cmake()/pkgconfig() provided
# FIXME
BuildRequires:  roctracer-devel

Requires:       cmake(hip)
Requires:       cmake(rocrand)
Requires:       gcc-c++

%conf -p
export PATH=%{rocmllvm_bindir}:$PATH

%description
AMD's library for high performance machine learning primitives.
MIOpen supports convolution, batch normalization, activation, pooling,
RNN/LSTM/GRU, and attention/transformer operations for the HIP backend.

%package        devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
%{summary}

%if %{with test}
%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{summary}
%endif

%prep -a
# clang-tidy is brittle and not needed when rebuilding from a tarball
sed -i -e 's@clang-tidy@true@' cmake/ClangTidy.cmake

# half_float::detail::expr is not present in all half versions
sed -i -e 's@std::is_same_v<T, half_float::detail::expr>@0@' test/verify.hpp

# MIOpen tries to download googletest; disable when not needed
%if %{without test}
sed -i -e 's@add_subdirectory(test)@#add_subdirectory(test)@' CMakeLists.txt
sed -i -e 's@add_subdirectory(speedtests)@#add_subdirectory(speedtests)@' CMakeLists.txt
%endif

# Use the standard data directory for the MIOpen kernel database
sed -i -e 's@GetLibPath().parent_path() / "share/miopen/db"@"%{_datadir}/miopen/db"@' src/db_path.cpp.in

# -fno-offload-uniform-block is unsupported on this ROCm version
sed -i -e 's@opts.push_back("-fno-offload-uniform-block");@//opts.push_back("-fno-offload-uniform-block");@' src/comgr.cpp

# Fix the path used to locate the ROCm clang binary at build time
sed -i -e 's@llvm/bin/clang@bin/clang@' src/hip/hip_build_utils.cpp

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
