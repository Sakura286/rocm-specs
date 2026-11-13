# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Need GPU to run tests
%bcond test 0

%global rocm_release 7.14
%global rocm_patch   1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 23

# Keep this in the recipe: server-generated _constraints has a service prefix.
#!BuildConstraint: hardware:jobs 32

Name:           miopen
Version:        %{rocm_version}
Release:        %autorelease
Summary:        AMD's Machine Intelligence Library
License:        MIT AND BSD-2-Clause AND Apache-2.0
URL:            https://github.com/ROCm/MIOpen
#!RemoteAsset:  sha256:afd9fe9121e3a64a8e2b8d4bc021d00e171f029c84631c576eb190fbe645fb97
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-%{version}/miopen.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n miopen

# LLVM 23's HIP bundler requires the host triple's environment field.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -DCMAKE_HIP_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
BuildOption(conf):  -G Ninja
# Use the declared system dependencies instead of fetching third-party sources.
BuildOption(conf):  -DMIOPEN_STANDALONE_BUILD=OFF
# Do not run developer clang-tidy analysis during distribution builds.
BuildOption(conf):  -DCLANG_TIDY_EXE=/usr/bin/true
BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBoost_USE_STATIC_LIBS=OFF
BuildOption(conf):  -DMIOPEN_BUILD_DRIVER=OFF
BuildOption(conf):  -DMIOPEN_ENABLE_AI_IMMED_MODE_FALLBACK=OFF
BuildOption(conf):  -DMIOPEN_ENABLE_AI_KERNEL_TUNING=OFF
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{rocmllvm_bindir}/clang++
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
BuildRequires:  cmake(hip)
BuildRequires:  rocm-hip-devel >= 7.14.1
BuildRequires:  cmake(hipblaslt)
BuildRequires:  hipblaslt-devel >= 7.14.1
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  rocr-runtime-devel >= 7.14.1
BuildRequires:  cmake(rocblas)
BuildRequires:  rocblas-devel >= 7.14.1
BuildRequires:  cmake(rocrand)
BuildRequires:  rocrand-devel >= 7.14.1
%if %{with test}
BuildRequires:  cmake(GTest)
%endif
BuildRequires:  clang(major) = %{llvm_maj_ver}
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
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros
BuildRequires:  roctracer-devel

Requires:       cmake(hip)
Requires:       cmake(rocrand)
Requires:       gcc-c++

%patchlist
2002-workaround-half-float-expr-deduction.patch
2004-fix-clang-rel-path.patch
2005-use-version-header-in-cxx20.patch

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

%build -p
# Also cover hipcc launched directly by generated kernel build scripts.
export HIPCC_COMPILE_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export HIPCC_LINK_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"

%conf -p
# Also cover hipcc launched directly by generated kernel build scripts.
export HIPCC_COMPILE_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export HIPCC_LINK_FLAGS_APPEND="--target=%{_target_cpu}-openruyi-linux-gnu"
export PATH=%{rocmllvm_bindir}:$PATH

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
