# SPDX-FileCopyrightText: (C) 2025, 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2025, 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-FileContributor: Yifan Xu <xuyifan@iscas.ac.cn>
# SPDX-FileContributor: misaka00251 <liuxin@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# The package follows LLVM's major version, but API version is still important:
%global comgr_maj_api_ver 3
%global comgr_full_api_ver %{comgr_maj_api_ver}.5

# What LLVM is upstream using (use LLVM_VERSION_MAJOR from cmake/Modules/LLVMVersion.cmake):
%global llvm_maj_ver 24

%global rocm_release 10.1
%global rocm_patch 0
%global rocm_version %{rocm_release}.%{rocm_patch}
%global source_tag therock-%{rocm_release}

%global bundle_prefix %{_libdir}/llvm%{llvm_maj_ver}
%global llvm_triple %{_target_platform}
%global amd_device_libs_prefix %{bundle_prefix}/lib/clang/%{llvm_maj_ver}
%global amd_device_libs_install_dir %{_lib}/llvm%{llvm_maj_ver}/lib/clang/%{llvm_maj_ver}/amdgcn

%global toolchain clang

%ifarch x86_64
%global targets_to_build "X86;AMDGPU"
%endif
%ifarch riscv64
#!BuildConstraint: hardware:jobs 32
%global targets_to_build "RISCV;AMDGPU"
%endif

%bcond device_libs_test 1
%bcond comgr_test 1

Name:           rocm-llvm
Version:        %{rocm_version}
Release:        %autorelease
Summary:        Various AMD ROCm LLVM related services
# llvm is Apache-2.0 WITH LLVM-exception OR NCSA
# hipcc is MIT, device-libs are NCSA, comgr is Apache-2.0 WITH LLVM-exception:
License:        (Apache-2.0 WITH LLVM-exception OR NCSA) AND Apache-2.0 WITH LLVM-exception AND NCSA AND MIT
URL:            https://github.com/ROCm/llvm-project
#!RemoteAsset:  sha256:db317aadb90366b61af0fd93b0ccf3cefe70a18e4e37c23744d968ea6f900654
Source0:        %{url}/archive/refs/tags/%{source_tag}.tar.gz
Source1:        rocm-llvm.prep.in

BuildRequires:  clang(major) = %{llvm_maj_ver}
BuildRequires:  clang-devel(major) = %{llvm_maj_ver}
BuildRequires:  clang-static(major) = %{llvm_maj_ver}
BuildRequires:  clang%{llvm_maj_ver}-tools-extra
BuildRequires:  cmake
BuildRequires:  fdupes
BuildRequires:  libcxx%{llvm_maj_ver}-devel
BuildRequires:  lld(major) = %{llvm_maj_ver}
BuildRequires:  lld-devel(major) = %{llvm_maj_ver}
BuildRequires:  llvm(major) = %{llvm_maj_ver}
BuildRequires:  llvm-static(major) = %{llvm_maj_ver}
# Clang's exported ClangIR targets reference the MLIR CMake package and archives.
BuildRequires:  mlir%{llvm_maj_ver}-devel
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(libzstd)
# comgr requires python
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  rocm-cmake >= %{rocm_version}

%patchlist
# https://salsa.debian.org/rocm-team/rocm-llvm/-/merge_requests/2
0001-Use-signed-char-in-comgr-building.patch
# https://github.com/ROCm/llvm-project/commit/f327d0b1b4bc61ef9042747ffa77e70b92254c11
1001-comgr-use-feature-bitsets.patch
# Follow-up to 1001; retain upstream regression with 10.1 test context.
# https://github.com/ROCm/llvm-project/commit/6b5ccd0e88b0eb23ba3103e730b8efd26ac9e8f8
1002-comgr-sramecc-on-off-modes.patch
# https://github.com/ROCm/llvm-project/commit/5778526e3e788f8fa60bd8a8b37b2b737a1413ee
1003-comgr-independent-cache-tags.patch
# https://github.com/ROCm/llvm-project/commit/25affef0d99027aee4dcdf573e6b2b9d174b04eb
1004-device-libs-update-stale-tests.patch
# https://github.com/ROCm/llvm-project/commit/3acdcc1e8f1feb831aa7e0238d8c850d2266799c
1005-comgr-subarch-triples.patch
# Depends on 1005.
# https://github.com/ROCm/llvm-project/commit/2bc76dfeecf71b94d0f83487dadc42e75a2d1362
1006-comgr-unbundle-subarch-tests.patch
# https://github.com/ROCm/llvm-project/commit/fad9cb3d631c287314e2de2f190274fb8c866a01
1007-comgr-gfx125-xnack-tests.patch
# Independent test-unit hunk only; dynamic LLVM linkage is retained.
# https://github.com/ROCm/llvm-project/commit/feb6bdbb08b2c55077377cd3e0a36bbcd04e49a0
1008-comgr-gtest-llvm-support.patch
# Follow-up to 1007: generic gfx12.5 does not expose selectable XNACK.
# https://github.com/ROCm/llvm-project/commit/1c1a11bcabbfda3f52d8541f5536bf69c95941e4
1009-comgr-gfx125-generic-feature-tests.patch
# Distribution path for the installed libc++ headers.
2000-comgr-support-system-llvm.patch
# Keep source Python lit separate from system LLVM tool paths.
2003-comgr-separate-lit-and-tool-paths.patch
# Avoid host-only libstdc++ runtime assertions in the header coexistence test.
2007-comgr-update-llvm24-test-expectations.patch
# Exercise upstream postopt linking with the COMGR cache enabled and disabled.
2008-comgr-test-cached-device-linking.patch
# Upstream IR checks require names omitted by distribution Clang defaults.
2009-device-libs-retain-ir-value-names.patch

%description
%{summary}

%package        macros
Summary:        ROCm Compiler RPM macros for RPM Build
BuildArch:      noarch

%description    macros
This package contains ROCm compiler related RPM macros.

%package     -n rocm-device-libs
Summary:        AMD ROCm LLVM bit code libraries

%description -n rocm-device-libs
This package contains a set of AMD specific device-side language runtime
libraries in the form of bit code. Specifically:
 - Open Compute library controls
 - Open Compute Math library
 - Open Compute Kernel library
 - OpenCL built-in library
 - HIP built-in library
 - Heterogeneous Compute built-in library

%package     -n rocm-comgr
Summary:        AMD ROCm LLVM Code Object Manager
Provides:       comgr(major) = %{comgr_maj_api_ver}
Provides:       rocm-comgr = %{comgr_full_api_ver}-%{release}

%description -n rocm-comgr
The AMD Code Object Manager (Comgr) is a shared library which provides
operations for creating and inspecting code objects.

%package     -n rocm-comgr-devel
Summary:        AMD ROCm LLVM Code Object Manager
Requires:       rocm-comgr%{?_isa} = %{version}-%{release}
Requires:       rocm-device-libs

%description -n rocm-comgr-devel
The AMD Code Object Manager (Comgr) development package.

%package     -n hipcc
Summary:        HIP compiler driver
Requires:       clang%{llvm_maj_ver}
Requires:       clang%{llvm_maj_ver}-tools-extra
Requires:       compiler-rt%{llvm_maj_ver}
Requires:       lld%{llvm_maj_ver}
Requires:       llvm%{llvm_maj_ver}
Requires:       rocm-device-libs = %{version}-%{release}
Suggests:       rocminfo

%description -n hipcc
hipcc is a compiler driver utility that will call clang or nvcc, depending on
target, and pass the appropriate include and library options for the target
compiler and HIP infrastructure.

hipcc will pass-through options to the target compiler. The tools calling hipcc
must ensure the compiler options are appropriate for the target compiler.

%prep
%autosetup -p1 -n llvm-project-%{source_tag}

# llvm_maj_ver sanity check (we should be matching the bundled llvm major ver):
if ! grep -q "set(LLVM_VERSION_MAJOR %{llvm_maj_ver})" cmake/Modules/LLVMVersion.cmake; then
    echo "ERROR llvm_maj_ver macro is not correctly set"
    exit 1
fi

# Keep the matching Python test runner; all compiled LLVM code is discarded.
mv llvm/utils/lit llvm-lit
ls | grep -xvE 'amd|llvm-lit' | xargs rm -r

install -pm 755 %{SOURCE1} prep.sh
sed -i -e 's@%%{_prefix}@%{_prefix}@' prep.sh
sed -i -e 's@%%{_lib}@%{_lib}@' prep.sh
sed -i -e 's@%%{amd_device_libs_prefix}@%{amd_device_libs_prefix}@' prep.sh
sed -i -e 's@%%{bundle_prefix}@%{bundle_prefix}@' prep.sh
sed -i -e 's@%%{llvm_maj_ver}@%{llvm_maj_ver}@' prep.sh
grep -v '%%{' prep.sh

. ./prep.sh

%build
CLANG_VERSION=%llvm_maj_ver

# Maybe use llvm-config-%{llvm_maj_ver} in the future
LLVM_BINDIR=`%{_libdir}/llvm%{llvm_maj_ver}/bin/llvm-config --bindir`
LLVM_CMAKEDIR=`%{_libdir}/llvm%{llvm_maj_ver}/bin/llvm-config --cmakedir`
# Only enable limited targets to accelerate build
GPU_TARGET="gfx1100;gfx1101;gfx1200;gfx1201"

echo "%%rocmllvm_version $CLANG_VERSION"        >  macros.rocmcompiler
echo "%%rocmllvm_bindir $LLVM_BINDIR"           >> macros.rocmcompiler
echo "%%rocmllvm_cmakedir $LLVM_CMAKEDIR"       >> macros.rocmcompiler
echo "%%rocm_gpu_list_default \"$GPU_TARGET\""  >> macros.rocmcompiler

export PATH=%{_libdir}/llvm%{llvm_maj_ver}/bin:$PATH
export INCLUDE_PATH=%{_libdir}/llvm%{llvm_maj_ver}/include

# Build device-libs first, hipcc and comgr need it
%define _vpath_srcdir amd/device-libs
%define _vpath_builddir build-devicelibs
#TODO ROCM_DEVICE_LIBS_BITCODE_INSTALL_LOC_* should be removed in ROCm 7.0:
%cmake -DCMAKE_PREFIX_PATH=%{bundle_prefix} \
    -DROCM_DEVICE_LIBS_BITCODE_INSTALL_LOC_NEW="%{amd_device_libs_install_dir}" \
    -DCMAKE_EXE_LINKER_FLAGS:STRING="-fuse-ld=lld"
%cmake_build -- %{?_smp_mflags}
# Used by comgr to find device libs when building:
export ROCM_PATH=$(realpath %__cmake_builddir)

# Build comgr
%define _vpath_srcdir amd/comgr
%define _vpath_builddir build-comgr
%cmake -DCMAKE_PREFIX_PATH="$ROCM_PATH;%{bundle_prefix}" \
    -DCMAKE_EXE_LINKER_FLAGS:STRING="-fuse-ld=lld" \
    -DCOMGR_LIBCXX_INCLUDE_DIR=%{bundle_prefix}/include/c++/v1 \
    -DLLVM_LIT_PATH="$PWD/llvm-lit/lit.py" \
    -DBUILD_TESTING=%{?with_comgr_test:ON}%{!?with_comgr_test:OFF}
%cmake_build -- %{?_smp_mflags}

# Build hipcc
%define _vpath_srcdir amd/hipcc
%define _vpath_builddir build-hipcc
%cmake -DHIPCC_BACKWARD_COMPATIBILITY=OFF \
    -DCMAKE_EXE_LINKER_FLAGS:STRING="-fuse-ld=lld"
%cmake_build -- %{?_smp_mflags}

%check
check_status=0
# Test device-libs
%define _vpath_srcdir amd/device-libs
%define _vpath_builddir build-devicelibs
# OCL.cmake mirrors the relative install path below the build directory.
# Point Clang's --rocm-path at those freshly built libraries, not the host.
ln -s %{amd_device_libs_install_dir} build-devicelibs/amdgcn
# Upstream 1004 accounts for non-foldable reciprocal intrinsics in lgamma_r.
%{?with_device_libs_test:%ctest || check_status=1}

# Test comgr
%define _vpath_srcdir amd/comgr
%define _vpath_builddir build-comgr
%{?with_comgr_test:%ctest || check_status=1}
%{?with_comgr_test:%cmake_build --target test-unit test-lit -- %{?_smp_mflags} || check_status=1}
exit "$check_status"

%install
# Install macros
install -Dpm 644 macros.rocmcompiler \
    %{buildroot}%{_rpmmacrodir}/macros.rocmcompiler

# Install device-libs
%define _vpath_builddir build-devicelibs
%cmake_install

# Install comgr
%define _vpath_builddir build-comgr
%cmake_install

# Install hipcc
%define _vpath_builddir build-hipcc
%cmake_install

rm -f %{buildroot}%{_datadir}/doc/rocm-device-libs/LICENSE.TXT
rm -rf %{buildroot}%{_datadir}/doc/amd_comgr
rm -f %{buildroot}%{_datadir}/doc/hipcc/LICENSE.txt
rm -f %{buildroot}%{_datadir}/doc/hipcc/README.md

%files macros
%{_rpmmacrodir}/macros.rocmcompiler

%files -n rocm-device-libs
%doc        amd/device-libs/README.md amd/device-libs/doc/*.md
%license    amd/device-libs/LICENSE.TXT
%dir        %{_libdir}/cmake/AMDDeviceLibs
%{_libdir}/cmake/AMDDeviceLibs/*.cmake
%{amd_device_libs_prefix}/amdgcn

%files -n rocm-comgr
%doc        amd/comgr/README.md
%license    amd/comgr/LICENSE.txt
%{_libdir}/libamd_comgr.so.*

%files -n rocm-comgr-devel
%dir        %{_includedir}/amd_comgr
%dir        %{_libdir}/cmake/amd_comgr
%{_includedir}/amd_comgr/amd_comgr.h
%{_libdir}/libamd_comgr.so
%{_libdir}/cmake/amd_comgr/*.cmake

%files -n hipcc
%doc        amd/hipcc/README.md
%license    amd/hipcc/LICENSE.txt
%{_bindir}/hipcc
%{_bindir}/hipconfig

%changelog
%autochangelog
