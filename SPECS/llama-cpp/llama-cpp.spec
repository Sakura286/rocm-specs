# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Originally extracted from Fedora Project
# Authors: The Fedora Project Contributors

%global toolchain clang

# The default flavor builds the CPU backend. The "rocm" and "vulkan"
# multibuild flavors select the corresponding GPU backend.
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "rocm"
%bcond rocm 1
%bcond vulkan 0
%else
%if "%{flavor}" == "vulkan"
%bcond rocm 0
%bcond vulkan 1
%else
%bcond rocm 0
%bcond vulkan 0
%endif
%endif

%if %{with rocm}
Name:           llama-cpp-rocm
%else
%if %{with vulkan}
Name:           llama-cpp-vulkan
%else
Name:           llama-cpp-cpu
%endif
%endif
Version:        b9859
Release:        %autorelease
Summary:        LLM inference in C/C++
License:        MIT AND Apache-2.0 AND LicenseRef-Fedora-Public-Domain
URL:            https://github.com/ggml-org/llama.cpp
VCS:            git:https://github.com/ggml-org/llama.cpp.git
#!RemoteAsset:  sha256:5d41eec5fe4bcdfe5a74c907380fa80fa145c791d1c323c5c1143a7e0fe4b5f8
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz
BuildSystem:    cmake

BuildOption(prep):  -n llama.cpp-%{version}
BuildOption(conf):  -G Ninja
BuildOption(conf):  -DLLAMA_BUILD_NUMBER=9859
BuildOption(conf):  -DLLAMA_BUILD_EXAMPLES=OFF
BuildOption(conf):  -DLLAMA_BUILD_TESTS=OFF
# Building the Web UI downloads frontend assets, which is not allowed in OBS.
BuildOption(conf):  -DLLAMA_BUILD_UI=OFF
BuildOption(conf):  -DLLAMA_USE_PREBUILT_UI=OFF
BuildOption(conf):  -DGGML_NATIVE=OFF

# Build for the x86-64 baseline rather than the OBS worker's CPU.
%ifarch x86_64
BuildOption(conf):  -DGGML_SSE42=OFF
BuildOption(conf):  -DGGML_AVX=OFF
BuildOption(conf):  -DGGML_AVX_VNNI=OFF
BuildOption(conf):  -DGGML_AVX2=OFF
BuildOption(conf):  -DGGML_BMI2=OFF
BuildOption(conf):  -DGGML_AVX512=OFF
BuildOption(conf):  -DGGML_AVX512_VBMI=OFF
BuildOption(conf):  -DGGML_AVX512_VNNI=OFF
BuildOption(conf):  -DGGML_AVX512_BF16=OFF
BuildOption(conf):  -DGGML_FMA=OFF
BuildOption(conf):  -DGGML_F16C=OFF
%endif

%if %{with rocm}
BuildOption(conf):  -DGGML_HIP=ON
BuildOption(conf):  -DCMAKE_HIP_COMPILER=%{rocmllvm_bindir}/clang++
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
%endif

%if %{with vulkan}
BuildOption(conf):  -DGGML_VULKAN=ON
%endif

BuildRequires:  cmake
BuildRequires:  git
BuildRequires:  ninja
BuildRequires:  pkgconfig(openssl)

%if %{without rocm}
BuildRequires:  clang
BuildRequires:  libomp-devel
%endif

%if %{with rocm}
BuildRequires:  clang22
BuildRequires:  clang22-devel
BuildRequires:  clang22-tools-extra
BuildRequires:  libomp22-devel
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hipblas)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocblas)
BuildRequires:  compiler-rt22
BuildRequires:  hipcc
BuildRequires:  llvm22-devel
BuildRequires:  rocm-llvm-macros
%endif

%if %{with vulkan}
# FindVulkan needs the loader development files and the glslc executable.
BuildRequires:  vulkan-loader-devel
BuildRequires:  pkgconfig(SPIRV-Headers)
BuildRequires:  shaderc
%endif

%if %{without rocm}
%if %{without vulkan}
Provides:       llama-cpp = %{version}-%{release}
Conflicts:      llama-cpp-rocm
Conflicts:      llama-cpp-vulkan
%else
Conflicts:      llama-cpp-cpu
Conflicts:      llama-cpp-rocm
%endif
%else
Conflicts:      llama-cpp-cpu
Conflicts:      llama-cpp-vulkan
%endif

%description
llama.cpp provides performant inference for large language models in plain
C/C++. This package includes command-line tools, a server, and shared libraries.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
%if %{without rocm}
%if %{without vulkan}
Provides:       llama-cpp-devel = %{version}-%{release}
%endif
%endif

%description devel
Headers, shared-library links, pkg-config metadata, and CMake package files for
developing applications against llama.cpp and ggml.

%check -a
# Backend execution requires a model and, for GPU flavors, suitable hardware.
# This smoke test only verifies that the freshly linked CLI starts.
LD_LIBRARY_PATH=%{_vpath_builddir}/bin \
    %{_vpath_builddir}/bin/llama-cli --version

%files
%license LICENSE
%doc README.md
%{_bindir}/llama*
%{_libdir}/libggml*.so.*
%{_libdir}/libllama-*-impl.so
%{_libdir}/libllama*.so.*
%{_libdir}/libmtmd.so.*

%files devel
%{_includedir}/ggml*.h
%{_includedir}/gguf.h
%{_includedir}/llama*.h
%{_includedir}/mtmd*.h
%{_libdir}/libggml*.so
%{_libdir}/libllama.so
%{_libdir}/libllama-common.so
%{_libdir}/libmtmd.so
%{_libdir}/cmake/ggml/
%{_libdir}/cmake/llama/
%{_libdir}/pkgconfig/llama.pc

%changelog
%autochangelog
