# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Without a GPU, the test cases will fail with `what():  hipGetDeviceCount failed`
# rocFFT needs a GPU to run tests
%bcond test 0

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}

%global llvm_maj_ver 24


%ifarch riscv64
# Generated GPU kernels require native workers with larger job slots.
#!BuildConstraint: hardware:jobs 32
%endif

Name:           rocfft
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm Fast Fourier Transforms library
License:        MIT
URL:            https://github.com/ROCm/rocFFT
#!RemoteAsset:  sha256:d6aa41ab83a20dd75f754800f1997c64b97caf81dfcb5827fe48b7b8c2c98df6
Source0:        https://github.com/ROCm/rocm-libraries/releases/download/therock-10.1/rocfft.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n rocfft

Patch0:         0001-cmake-use-gnu-installdirs.patch

BuildOption(conf):  -G Ninja
# Offload bundle IDs require an explicit host environment component.
# The LLVM runtime RPMs retain the distribution triple without the GNU suffix.
BuildOption(conf):  -DCMAKE_INSTALL_RPATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}
BuildOption(conf):  -DCMAKE_CXX_COMPILER_TARGET=%{_target_cpu}-openruyi-linux-gnu
%ifarch riscv64
# The native GCC directory omits the GNU environment required by offload IDs.
BuildOption(conf):  -DCMAKE_CXX_COMPILER_ARG1="--gcc-triple=%{_target_platform}"
%endif
%ifarch riscv64
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu --gcc-triple=%{_target_platform}"
%else
BuildOption(conf):  -DCMAKE_HIP_FLAGS_INIT="--target=%{_target_cpu}-openruyi-linux-gnu"
%endif
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_CLIENTS_TESTS=ON
BuildOption(conf):  -DROCFFT_BUILD_OFFLINE_TUNER=OFF
BuildOption(conf):  -DROCFFT_KERNEL_CACHE_ENABLE=OFF
BuildOption(conf):  -DSQLITE_USE_SYSTEM_PACKAGE=ON
BuildOption(conf):  -DCMAKE_C_COMPILER=%{rocmllvm_bindir}/clang
BuildOption(conf):  -DCMAKE_CXX_COMPILER=%{_libdir}/rocm/llvm%{llvm_maj_ver}/bin/clang++

BuildRequires:  boost-devel
BuildRequires:  clang(major) = %{llvm_maj_ver}
# LLVM PR 168164 propagates the lp64d host features to RDC registration objects.
BuildRequires:  rocm-clang >= 24.0.0~git20261109.b1de84e-12
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  rocm-hip-devel >= %{rocm_version}
BuildRequires:  cmake(hip)
BuildRequires:  hiprand-devel >= %{rocm_version}
BuildRequires:  cmake(hiprand)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(GTest)
BuildRequires:  rocrand-devel >= %{rocm_version}
BuildRequires:  cmake(rocrand)
BuildRequires:  compiler-rt(major) = %{llvm_maj_ver}
BuildRequires:  libomp-devel(major) = %{llvm_maj_ver}
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  ninja
BuildRequires:  pkgconfig(fftw3)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(sqlite3) >= 3.51.3
BuildRequires:  rocm-cmake
BuildRequires:  rocm-device-libs
BuildRequires:  rocm-llvm-macros

%global _description %{expand:
rocFFT is a software library for computing fast Fourier transforms (FFTs) written
in HIP. It is part of AMD's software ecosystem based on ROCm. In addition to
AMD GPU hardware, rocFFT also works on CPU devices to facilitate testing.
}

%description
%{_description}

%package        devel
Summary:        The rocFFT development package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake(hip)

%description    devel
The rocFFT development package.

%package        test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    test
%{_description}

%prep -a
# openRuyi LLVM 24 is built without the SPIR-V backend. Keep the configured
# native GPU targets, but omit the clients' additional generic SPIR-V fallback.
sed -i '/target_.*_options(.*--offload-arch=amdgcnspirv/d' clients/tests/CMakeLists.txt

%conf -p
# Preserve compiler and OpenMP probe diagnostics when configuration fails.
trap 'status=$?; if [ "$status" -ne 0 ]; then cat %{_vpath_builddir}/CMakeFiles/CMakeConfigureLog.yaml; fi; exit "$status"' EXIT
export HIP_CLANG_PATH=%{_libdir}/rocm/llvm%{llvm_maj_ver}/bin
export PATH="$HIP_CLANG_PATH":%{rocmllvm_bindir}:$PATH
export LIBRARY_PATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}${LIBRARY_PATH:+:$LIBRARY_PATH}

%build -p
export HIP_CLANG_PATH=%{_libdir}/rocm/llvm%{llvm_maj_ver}/bin
export PATH="$HIP_CLANG_PATH":%{rocmllvm_bindir}:$PATH
export LIBRARY_PATH=%{_libdir}/llvm%{llvm_maj_ver}/lib/%{_target_platform}${LIBRARY_PATH:+:$LIBRARY_PATH}

%install -a
# Preserve the versioned runtime compiler helper used by the library.
rm -rf %{buildroot}/%{_prefix}/.info
rm -f %{buildroot}%{_datadir}/doc/rocfft/LICENSE.md

%if %{with test}
%check
%{_vpath_builddir}/clients/staging/rocfft-test
%endif

%files
%doc README.md
%license LICENSE.md
%{_libdir}/librocfft.so.0{,.*}
%{_libdir}/rocfft/

%files devel
%{_includedir}/rocfft/
%{_libdir}/cmake/rocfft/
%{_libdir}/librocfft.so

%files test
%{_bindir}/rocfft-test

%changelog
%autochangelog
