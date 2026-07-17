# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Originally extracted from Fedora Project
# Authors: The Fedora Project Contributors

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

%global build_number 9948
# These libraries implement internal CLI/server tools and do not expose a
# supported ABI for third-party consumers.  The libggml-* entries are the
# dlopen()ed backend plugins under %%{_libdir}/ggml.
%global __provides_exclude ^(libllama-.*-impl|libggml-cpu.*|libggml-hip|libggml-vulkan)\\.so
%global __requires_exclude ^libllama-.*-impl\\.so
# Run the full ctest suite and blacklist only the tests that cannot pass in
# an offline OBS build: Hugging Face / network fetches, tests that require a
# downloaded model, the python+jinja2 comparison variant (not BuildRequired),
# and the unfiltered "test-backend-ops" ctest entry (its default invocation
# skips the CPU backend and would otherwise probe whichever GPU backend is
# compiled in; %%check -a below runs it directly with "-b CPU" instead).
# test-llama-archs never calls ggml_backend_load_all(), so under
# GGML_BACKEND_DL it enumerates zero devices and every arch check silently
# reports SKIP; it "passes" without exercising any real computation, so
# exclude it everywhere until upstream fixes that gap.
%global ctest_exclude_common (test-tokenizers-ggml-vocabs|test-download-model|test-thread-safety|test-state-restore-fragmented|test-recurrent-state-rollback|test-save-load-state|test-quant-type-selection|test-gguf-model-data|test-arg-parser|test-jinja-py|test-backend-ops|test-llama-archs)
%if %{with rocm} || %{with vulkan}
# test-opt enumerates every registered ggml backend device with no CPU-only
# filter; on the rocm/vulkan flavors that includes the real GPU backend,
# which OBS build workers cannot initialize without hardware.
%global ctest_exclude ^(%{ctest_exclude_common}|test-opt)$
%else
%global ctest_exclude ^%{ctest_exclude_common}$
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
Version:        b%{build_number}
Release:        %autorelease
Summary:        LLM inference in C/C++
License:        MIT AND Apache-2.0 AND Unlicense
URL:            https://github.com/ggml-org/llama.cpp
VCS:            git:https://github.com/ggml-org/llama.cpp.git
#!RemoteAsset:  sha256:ab2d4fc95692f4f712e4567585299be26611fc07b510c79f9e1cc288d30551cf
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz
BuildSystem:    cmake

%if %{with rocm}
%ifarch riscv64
# Match the openRuyi Ollama workaround for unstable riscv64 ROCm inference;
# do not reduce the default batch size for x86_64 ROCm builds.
# https://github.com/Sakura286/rocm-specs/commit/d1069acf22589a2bc60d8fefa706c1fa822f5556
Patch0:         2000-limit-rocm-batch-size.patch
%endif
%endif

BuildOption(prep):  -n llama.cpp-%{version}
BuildOption(conf):  -G Ninja
BuildOption(conf):  -DLLAMA_BUILD_NUMBER=%{build_number}
# Source0 is an archive without .git; preserve the verified release tag commit.
BuildOption(conf):  -DLLAMA_BUILD_COMMIT=074944998d3f25e7001ede30d152b59dff741c8c
BuildOption(conf):  -DLLAMA_BUILD_EXAMPLES=OFF
BuildOption(conf):  -DLLAMA_BUILD_TESTS=ON
BuildOption(conf):  -DLLAMA_TESTS_INSTALL=OFF
# Building the Web UI downloads frontend assets, which is not allowed in OBS.
BuildOption(conf):  -DLLAMA_BUILD_UI=OFF
BuildOption(conf):  -DLLAMA_USE_PREBUILT_UI=OFF
BuildOption(conf):  -DGGML_NATIVE=OFF
BuildOption(conf):  -DGGML_CCACHE=OFF
# Build the ggml backends as runtime-loaded plugins.  On x86_64 this builds
# every CPU ISA variant (x86-64 baseline up to AVX-512/AMX) and picks the
# best one for the executing CPU at startup, instead of pinning the whole
# build to the baseline.  riscv64 keeps the single default backend: the
# ALL_VARIANTS riscv64_v variant is plain rv64gc_v and would lose the
# zfh/zvfh extensions of the default march string.
BuildOption(conf):  -DGGML_BACKEND_DL=ON
BuildOption(conf):  -DGGML_BACKEND_DIR=%{_libdir}/ggml
%ifarch x86_64
BuildOption(conf):  -DGGML_CPU_ALL_VARIANTS=ON
%endif
BuildOption(check):  --output-on-failure --exclude-regex '%{ctest_exclude}'

%if %{with rocm}
BuildOption(conf):  -DGGML_HIP=ON
BuildOption(conf):  -DCMAKE_HIP_COMPILER=%{rocmllvm_bindir}/clang++
BuildOption(conf):  -DAMDGPU_TARGETS=%{rocm_gpu_list_default}
%endif

%if %{with vulkan}
BuildOption(conf):  -DGGML_VULKAN=ON
%endif

BuildRequires:  cmake
BuildRequires:  ninja
BuildRequires:  pkgconfig(openssl)
Suggests:       ffmpeg

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
BuildRequires:  lld22
BuildRequires:  llvm22-devel
BuildRequires:  rocm-llvm-macros
%else
BuildRequires:  libomp-devel
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
# The declarative ctest invocation above is a blacklist: everything runs
# except %%{ctest_exclude} (network/model-fetch tests, the python+jinja2
# variant, and, on ROCm/Vulkan, the tests that enumerate every backend device
# with no CPU-only filter).  test-backend-ops is excluded there and run
# directly below instead, filtered to "-b CPU" so it never probes a GPU
# backend that OBS build workers cannot initialize without hardware.
LD_LIBRARY_PATH=%{_vpath_builddir}/bin \
    %{_vpath_builddir}/bin/test-backend-ops -b CPU \
    -o ADD,MUL_MAT,SOFT_MAX,RMS_NORM,ROPE -j 1
# This smoke test verifies that the freshly linked CLI starts.
LD_LIBRARY_PATH=%{_vpath_builddir}/bin \
    %{_vpath_builddir}/bin/llama-cli --version

%files
%license LICENSE licenses/LICENSE-jsonhpp vendor/cpp-httplib/LICENSE
%doc README.md
%{_bindir}/llama*
%{_libdir}/ggml/
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
