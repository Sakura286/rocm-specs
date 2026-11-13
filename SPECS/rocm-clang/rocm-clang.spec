# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
# SPDX-License-Identifier: MulanPSL-2.0

%global llvm_major 24
%global snapshot_version 24.0.0~git20261109.b1de84e
%global source_commit b1de84ea1aa8c686639f4c0144e045e4a2a12510
%global compiler_prefix %{_libdir}/rocm/llvm%{llvm_major}
# Rebuild only Clang against the distribution LLVM, without RPM LTO.
%global build_cflags %{?build_cflags} -fno-lto
%global build_cxxflags %{?build_cxxflags} -fno-lto
#!BuildConstraint: hardware:jobs 32

Name:           rocm-clang
Version:        %{snapshot_version}
Release:        %autorelease
Summary:        Clang 24 with experimental upstream ROCm build fixes
License:        Apache-2.0 WITH LLVM-exception
URL:            https://github.com/llvm/llvm-project
#!RemoteAsset:  sha256:84d435841d4227537f27ba89ca7647013264b380050c520b28c74e452e466963
Source0:        %{url}/archive/%{source_commit}.tar.gz
Source1:        static-device-constexpr.hip
Patch0:         0000-llvm-pr-216938.patch
Patch1:         0001-llvm-pr-233925.patch
%if "%{openruyi_riscv_arch}" == "-march=rva23u64"
Patch2000:      2000-Add-riscv64-openruyi-linux-triple-and-set-it-to-rva2.patch
%endif
# Distribution GCC search list, with its missing RISC-V list comma corrected.
Patch2001:      2001-Add-openruyi-linux-to-X86_64Triples-and-RISCV64Tripl.patch
BuildSystem:    cmake
BuildOption(prep):  -n llvm-project-%{source_commit}
%global _vpath_srcdir clang
BuildOption(conf):  -G Ninja
BuildOption(conf):  -DLLVM_DIR=%{_libdir}/llvm%{llvm_major}/lib/cmake/llvm
BuildOption(conf):  -DCMAKE_INSTALL_PREFIX=%{compiler_prefix}
BuildOption(conf):  -DCMAKE_INSTALL_LIBDIR=lib
BuildOption(conf):  -DCMAKE_C_COMPILER=gcc
BuildOption(conf):  -DCMAKE_CXX_COMPILER=g++
BuildOption(conf):  -DLLVM_USE_LINKER=lld
BuildOption(conf):  -DLLVM_LINK_LLVM_DYLIB=ON
BuildOption(conf):  -DCLANG_LINK_CLANG_DYLIB=ON
BuildOption(conf):  -DCLANG_BUILD_TOOLS=ON
BuildOption(conf):  -DCLANG_INCLUDE_TESTS=OFF
BuildOption(conf):  -DCLANG_INCLUDE_DOCS=OFF
BuildOption(conf):  -DCLANG_RESOURCE_DIR=%{_libdir}/llvm%{llvm_major}/lib/clang/%{llvm_major}
BuildOption(conf):  -DCMAKE_INSTALL_RPATH='%{compiler_prefix}/lib;%{_libdir}/llvm%{llvm_major}/lib'

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja
BuildRequires:  llvm24-devel = %{snapshot_version}
BuildRequires:  clang24-devel = %{snapshot_version}
BuildRequires:  clang24-tools-extra = %{snapshot_version}
BuildRequires:  lld(major) = %{llvm_major}
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(zlib)
# LLVMConfig imports these targets even when only Clang is rebuilt.
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(liblzma)
BuildRequires:  pkgconfig(libxml-2.0)
Requires:       llvm24-libs = %{snapshot_version}
Requires:       clang24-libs = %{snapshot_version}

%description
An isolated Clang frontend and linker wrapper built from the openRuyi LLVM
snapshot, with upstream pull requests 216938 and 233925. The pull requests
are experimental and were not merged when backported. LLVM libraries,
compiler runtime, resource headers and device libraries come from the
matching distribution snapshot. Tools install under %{compiler_prefix}.

%conf -p
# GCC accepts the linker name rather than an absolute -fuse-ld path.
export PATH=%{_libdir}/llvm%{llvm_major}/bin:$PATH

%build
export PATH=%{_libdir}/llvm%{llvm_major}/bin:$PATH
%cmake_build --target clang clang-linker-wrapper

%install
DESTDIR=%{buildroot} cmake --build %{_vpath_builddir} --target install-clang install-clang-linker-wrapper install-clang-cpp

%check
export PATH=%{_libdir}/llvm%{llvm_major}/bin:$PATH
# Upstream regression checks for wrong-sided calls in static initializers.
export LD_LIBRARY_PATH="$PWD/%{_vpath_builddir}/lib:%{_libdir}/llvm%{llvm_major}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
%{_vpath_builddir}/bin/clang -cc1 -internal-isystem %{_libdir}/llvm%{llvm_major}/lib/clang/%{llvm_major}/include -x cuda -triple x86_64-unknown-linux-gnu -fsyntax-only -verify=expected,host clang/test/SemaCUDA/global-initializers.cu
%{_vpath_builddir}/bin/clang -cc1 -internal-isystem %{_libdir}/llvm%{llvm_major}/lib/clang/%{llvm_major}/include -x cuda -triple nvptx -fcuda-is-device -fsyntax-only -verify=expected,device clang/test/SemaCUDA/global-initializers.cu
%{_libdir}/llvm%{llvm_major}/bin/llvm-offload-binary -o host-triple.out --image=file=%{SOURCE1},kind=hip,triple=amdgcn-amd-amdhsa,arch=gfx1100
%{_vpath_builddir}/bin/clang-linker-wrapper --dry-run --host-triple=%{_target_platform} --emit-fatbin-only host-triple.out -o host-triple.hipfb > host-triple.log 2>&1
grep -- '-targets=host-%{_target_platform}-unknown,' host-triple.log
%{_vpath_builddir}/bin/clang -x hip -nogpuinc -nogpulib --offload-arch=gfx1100 -fsyntax-only %{SOURCE1}

%files
%license llvm/LICENSE.TXT
%doc clang/README.txt
%{compiler_prefix}/bin/clang*
%{compiler_prefix}/lib/libclang-cpp.so*

%changelog
%autochangelog
