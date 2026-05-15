# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Sakura286 <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global rocm_release 7.1
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

# rocm stack builds with clang
%global toolchain clang

Name:           rccl
Version:        %{rocm_version}
Release:        %autorelease
Summary:        ROCm Communication Collectives Library

Url:            https://github.com/ROCm/rccl
VCS:            git:https://github.com/ROCm/rccl.git
License:        BSD-3-Clause AND MIT AND Apache-2.0
# From License.txt the main license is BSD 3
# Modifications from Microsoft is MIT
# The NVIDIA based header files below are Apache-2.0
#  src/include/nvtx3/nv*.h and similar
# The URL for NVIDIA in the License.txt https://github.com/NVIDIA/NVTX is Apache-2.0
#!RemoteAsset:  sha256:REPLACE_WITH_ACTUAL_SHA256
Source:         %{url}/archive/rocm-%{rocm_version}.tar.gz
BuildSystem:    cmake

BuildOption(conf):  -DGPU_TARGETS=%{rocm_gpu_list_default}
BuildOption(conf):  -DBUILD_TESTS=ON
BuildOption(conf):  -DENABLE_MSCCLPP=OFF
BuildOption(conf):  -DEXPLICIT_ROCM_VERSION=%{rocm_version}
BuildOption(conf):  -DROCM_PATH=%{_prefix}
BuildOption(prep):  -p1 -n rccl-rocm-%{version}

BuildRequires:  cmake
BuildRequires:  cmake(amd_comgr)
BuildRequires:  cmake(fmt)
BuildRequires:  cmake(hip)
BuildRequires:  cmake(hsa-runtime64)
BuildRequires:  cmake(rocm_smi)
BuildRequires:  cmake(rocm-core)
BuildRequires:  hipify
BuildRequires:  python3
BuildRequires:  rocm-cmake
BuildRequires:  rocm-llvm-macros
BuildRequires:  rocprofiler-register

Requires:       %{name}-data = %{version}-%{release}

%description
RCCL (pronounced "Rickle") is a stand-alone library of standard
collective communication routines for GPUs, implementing all-reduce,
all-gather, reduce, broadcast, reduce-scatter, gather, scatter, and
all-to-all. There is also initial support for direct GPU-to-GPU
send and receive operations. It has been optimized to achieve high
bandwidth on platforms using PCIe, xGMI as well as networking using
InfiniBand Verbs or TCP/IP sockets. RCCL supports an arbitrary
number of GPUs installed in a single node or multiple nodes, and
can be used in either single- or multi-process (e.g., MPI)
applications.

The collective operations are implemented using ring and tree
algorithms and have been optimized for throughput and latency. For
best performance, small operations can be either batched into
larger operations or aggregated through the API.

%package devel
Summary:        Headers and libraries for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       rccl-devel = %{version}-%{release}

%description devel
Headers and libraries for %{name}

%package data
Summary:        Data for %{name}
BuildArch:      noarch

%description data
Data for %{name}

%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}

%prep -a
# Do not force install
sed -i -e 's@set(CMAKE_INSTALL_LIBDIR@#set(CMAKE_INSTALL_LIBDIR@' cmake/Dependencies.cmake

%build -a
# Workaround
(while true; do echo "[heartbeat] $(date) - build still running..."; sleep 300; done) &
HEARTBEAT_PID=$!

%cmake_build

kill $HEARTBEAT_PID 2>/dev/null || true

%install -a
rm -f %{buildroot}%{_datadir}/doc/rccl/LICENSE.txt

%files
%license LICENSE.txt
%{_libdir}/librccl.so.*
%{_bindir}/rcclras

%files data
%{_datadir}/rccl/msccl-algorithms/
%{_datadir}/rccl/msccl-unit-test-algorithms/

%files devel
%doc README.md
%{_includedir}/rccl/
%{_libdir}/cmake/rccl/
%{_libdir}/librccl.so

%files test
%{_bindir}/rccl-UnitTests

%changelog
%autochangelog
